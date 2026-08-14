# PT33 Ollama Confinement - Rollback Procedure

| Field | Value |
|---|---|
| Task | V05-PT-33 reversible local-runtime confinement |
| Rollback owner | Principal Engineer (elevation) / Product Owner (UAC approval) |
| Before-state evidence | `docs/evidence/v0.5/pt33-ollama-confinement-before/before-state.json`, `firewall-rules.json`, `listeners-before.txt` |

## 1. Restore the original all-interfaces listener behavior

1. Stop the confined server: `Stop-Process -Id <confined PID> -Force` (or `Stop-Process -Name ollama -Force`).
2. Launch the normal app so it re-spawns the server as it did originally:
   `Start-Process "C:\Users\jmurr\AppData\Local\Programs\Ollama\ollama app.exe"`
   (This is the same startup-shortcut target; the app re-launches `ollama.exe serve`.)
3. The original before-state listener was `0.0.0.0:11434` + `[::]:11434`. If the user-level
   `OLLAMA_HOST=127.0.0.1:11434` prevents that, remove the user env value (HKCU) or launch with
   `OLLAMA_HOST=0.0.0.0:11434` to reproduce the exact before-state listener. Record the result.

## 2. Restore the removed inbound allow rules

The two removed "Query User" inbound allow rules were (exact identity from before export):

- Name `ollama.exe`, Action `Allow`, Direction `Inbound`, Profile `Public`
  - Program `C:\users\jmurr\appdata\local\programs\ollama\ollama.exe`
  - Protocol TCP, port any
  - RuleId `TCP Query User{445BBDC9-6371-470A-ABAF-9351125F8370}C:\users\jmurr\appdata\local\programs\ollama\ollama.exe`
- Name `ollama.exe`, Action `Allow`, Direction `Inbound`, Profile `Public`
  - Program `C:\users\jmurr\appdata\local\programs\ollama\ollama.exe`
  - Protocol UDP, port any
  - RuleId `UDP Query User{84C3DD48-8B25-4B16-B4A0-6BAE0E0C7921}C:\users\jmurr\appdata\local\programs\ollama\ollama.exe`

Recreate with (elevated):

```powershell
New-NetFirewallRule -DisplayName "ollama.exe" -Direction Inbound -Action Allow -Profile Public `
  -Program "C:\users\jmurr\appdata\local\programs\ollama\ollama.exe" -Protocol TCP -ErrorAction Continue
New-NetFirewallRule -DisplayName "ollama.exe" -Direction Inbound -Action Allow -Profile Public `
  -Program "C:\users\jmurr\appdata\local\programs\ollama\ollama.exe" -Protocol UDP -ErrorAction Continue
```

## 3. Remove the added outbound deny rule

```powershell
Remove-NetFirewallRule -DisplayName "Jarvis PT33 block ollama outbound" -ErrorAction SilentlyContinue
```

## 4. Verification after rollback

1. `netstat -ano | findstr ":11434"` shows the original listener(s).
2. `Get-NetFirewallRule | Where DisplayName -eq 'ollama.exe'` shows inbound Allow rules present again.
3. `Get-NetFirewallRule -DisplayName "Jarvis PT33 block ollama outbound"` returns nothing.
4. `ollama --version` still works and loopback health responds.
