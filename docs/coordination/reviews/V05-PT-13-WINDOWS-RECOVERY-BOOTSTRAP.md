# V05-PT-13 Native-Windows Recovery Bootstrap Return

| Field | Value |
|---|---|
| Task | `V05-PT-13` |
| Date | 2026-08-12 |
| Status | Blocked by the mandatory pre-Git writer self-test |
| Authority | [V05-PT-12 acceptance](V05-PT-12-ACCEPTANCE.md) |

The production atomic writer operated, but the known-byte self-test correctly failed before any
Git command. Windows PowerShell 5 interpreted the BOM-free script source through its legacy
source encoding, so the embedded literal `U+03A9` reached the writer as different characters.
The output was 30 bytes with SHA-256
`306264957206e450c827182da119f5f06568f52580f37126963e1002e047629e`, not the required 28-byte
payload.

The durable stop record is 181 bytes with SHA-256
`8c244a848e23368120eff4a7e85276509aa08eab7216638bdf5ac5993471ed21`.
No Git command, protected baseline, payload, branch, worktree, export, copy, or implementation
occurred.

The bounded correction is to construct the self-test character from code point `0x03A9` at
runtime and concatenate it with ASCII text and CRLF, avoiding any non-ASCII script-source
literal. The exact same 28-byte and digest assertions must remain unchanged.
