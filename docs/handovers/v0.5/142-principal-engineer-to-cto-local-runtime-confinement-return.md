# Handoff 142 - Principal Engineer to CTO: Local-runtime Confinement Return

| Field | Value |
|---|---|
| Date | 2026-08-14 |
| From | Principal Engineer |
| To | Chief Architect / CTO |
| Milestone | v0.5 Personal Prototype |
| Task | `V05-PT-33` |
| Status | **READY FOR REVIEW - LOOPBACK CONFINEMENT APPLIED, REVERSIBLE** |
| Frozen executable | `08b0b11383031d6e91f6f26145bfdffc710ca36b` (tree `df041615730ee65faa6001f717f2ccff3b8d726c`) |
| Documentation pin | `d345910f6239f5707975c77c45ea3759249d145e` (tree `a68b0d0657fc752cfe2ef017ffaecdbe8ffd27aa`) |
| Authority | [PO local-runtime confinement decision](../../../../../docs/coordination/reviews/V05-PT-32-PRODUCT-OWNER-ACCEPTANCE-AND-NEXT-GATES.md) and [Handoff 141](141-cto-to-product-owner-local-model-security-and-profile-disposition.md) |

## 1. Preflight confirmation

- PT32 accepted by Product Owner; PT33 authorized; PT34 remains blocked (unchanged).
- Frozen executable commit `08b0b11383031d6e91f6f26145bfdffc710ca36b` verified present with tree
  `df041615730ee65faa6001f717f2ccff3b8d726c` (J.A.R.V.I.S recovery worktree HEAD).
- Documentation pin `d345910f6239f5707975c77c45ea3759249d145e` verified as `v0.3.1-release`
  worktree HEAD.
- Elevation for firewall operations was explicitly approved by the Product Owner after identity and
  rollback preflight (UAC). No other elevation occurred.

## 2. Before-state (captured read-only first)

Evidence: `docs/evidence/v0.5/pt33-ollama-confinement-before/before-state.json`,
`firewall-rules.json`, `listeners-before.txt`, `rollback-procedure.md`.

| Item | Before value |
|---|---|
| Ollama version | 0.32.6 |
| Server executable | `C:\Users\jmurr\AppData\Local\Programs\Ollama\ollama.exe` SHA-256 `A64341018083A575267896F8117E66CCA0A04262A963BFB3053E46CE2FC4ACDA` |
| GUI executable | `C:\Users\jmurr\AppData\Local\Programs\Ollama\ollama app.exe` SHA-256 `F19F9D3A1D17E05CB5220F0778DF8B220035E68EBAB6652751998DDB9C41D3AA` |
| Server process | PID 3596, `ollama.exe serve`, owner `MIGHTY_MOUSE\jmurr`, parent PID 25912 |
| GUI process | PID 25912, `ollama app.exe`, owner `MIGHTY_MOUSE\jmurr` |
| Listeners | `0.0.0.0:11434` and `[::]:11434` (all interfaces) |
| Network profile | "Network 3" Ethernet, Public |
| Env (user) | `OLLAMA_HOST=127.0.0.1:11434`, `OLLAMA_CONTEXT_LENGTH=16384`, `OLLAMA_NUM_PARALLEL=1` |
| Env (machine) | none |
| Inbound firewall | 2 allow rules, both program-bound to ollama.exe, Public profile, TCP and UDP (Query User rules) |
| Startup | `Startup\Ollama.lnk` -> `ollama app.exe` (autostart at login) |
| Single install | Confirmed: no `Program Files\Ollama`, no `C:\Ollama`, no second binary |

No non-loopback established connections existed from PIDs 25912/3596 before mutation.

## 3. Reversible operations performed

1. **Stopped only the two proven Ollama processes** (server PID 3596, then GUI PID 25912) after
   identity proof. Verified no `ollama*` process remained and no listener on 11434.
2. **Launched the exact existing server executable** with a controlled per-process environment
   forcing `OLLAMA_HOST=127.0.0.1:11434` (plus `OLLAMA_NUM_PARALLEL=1`,
   `OLLAMA_CONTEXT_LENGTH=16384`), command `ollama.exe serve`. New PID 40516, owner jmurr.
3. **Removed only the two proven inbound allow rules** (exact-name match, identity re-verified:
   program = exact ollama.exe path, action Allow, direction Inbound) via elevated PowerShell:
   - `TCP Query User{445BBDC9-6371-470A-ABAF-9351125F8370}C:\users\jmurr\appdata\local\programs\ollama\ollama.exe`
   - `UDP Query User{84C3DD48-8B25-4B16-B4A0-6BAE0E0C7921}C:\users\jmurr\appdata\local\programs\ollama\ollama.exe`
4. **Added one exact-program outbound deny**:
   `Jarvis PT33 block ollama outbound`, Action Block, Direction Outbound, Profile Any, Program
   `C:\Users\jmurr\AppData\Local\Programs\Ollama\ollama.exe`
   (GUID `f28e9ff6-c7ea-4e3e-8582-9dc9f357ae24`).

## 4. After-state (verified)

Evidence: `docs/evidence/v0.5/pt33-ollama-confinement-after/after-state.json`,
`firewall-rules-after.json`, `listeners-after.txt`.

| Check | Result |
|---|---|
| Listener | `127.0.0.1:11434` ONLY; no `0.0.0.0`, no `[::]`, no LAN/public listener |
| Loopback health | HTTP 200 "Ollama is running" on `http://127.0.0.1:11434/` |
| Loopback under deny | exact `ollama.exe list` succeeded over `127.0.0.1:11434` (model list only; no model load, no inference) |
| LAN denial | `Test-NetConnection` to 172.26.112.1:11434, 172.30.224.1:11434, 192.168.12.157:11434 all `False` |
| Non-loopback connections | none from PID 40516 before, during, or after health check |
| Inbound allow rules | both removed (firewall diff: 2 Allow/Inbound/Public -> 1 Block/Outbound/Any) |
| Outbound deny | present, enabled, program-bound to exact ollama.exe, all profiles |
| GUI process | not running; not auto-relaunched |
| Ordinary-user verification | all read/health/list checks performed as `mighty_mouse\jmurr` (Medium integrity, no elevation) |

## 5. Rollback procedure

Recorded in full at `docs/evidence/v0.5/pt33-ollama-confinement-before/rollback-procedure.md`.
Covers: stop confined server, relaunch the normal app (startup-shortcut target), restore the two
inbound allow rules (exact names/programs/profiles), remove the outbound deny rule, and verify the
original listener/rule set. The before-state firewall JSON enables exact rule reconstruction.

## 6. Limitations and residual notes

- **Persistent confinement requires a later decision.** The Startup shortcut (`Ollama.lnk`) still
  auto-launches the GUI at login. A next-login relaunch could recreate a broad listener or prompt
  rules. This session's confinement is active now; persistence across login is not guaranteed and
  was not modified (startup change was outside this task's exact scope).
- **Outbound-deny loopback exemption is inherent** to Windows Firewall (loopback is not filtered),
  which is why the deny does not break `127.0.0.1:11434`.
- No model was loaded, no inference ran, no private data touched, no Jarvis/repository change made.
- The server binds IPv4 loopback only; no IPv6 `[::1]` listener was created (Handoff 141 allows
  `[::1]` only if explicitly supported and allowlisted; it was neither attempted nor required).

## 7. Exact exclusions honored

No installation, download, update, uninstall, model load/inference, private data, Jarvis/repo
changes, model relocation, broad firewall weakening, packaging, certification, merge, push,
publication, or release.

## 8. Exit statement

**READY FOR REVIEW.** Exact reversible loopback confinement applied and verified: loopback-only
listener, both inbound allows removed, exact-program outbound deny added, loopback health proven
without inference, LAN and non-loopback denial proven, complete before/after evidence and rollback
recorded, ordinary-user verification passed. Stop condition for CTO review reached.
