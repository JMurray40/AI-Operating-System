# Handoff 03 - Personal Recall Unicode baseline correction

Date: 2026-09-22
Sender: Chief of Staff
Receiver: Principal Engineer
Task: `V06-PR-01`
Disposition: **CURRENT FILENAME ACCEPTED; CONTROLLED CONTINUATION AUTHORIZED**

## Corrected diagnosis

[Verified] Direct Unicode code-point inspection supersedes the rendering-based description in Handoff 02. The current vault filename contains one proper em dash, Unicode `U+2014`. The retained baseline path contains the three-code-point mojibake sequence `U+00E2 U+20AC U+201D`, which is a misdecoded UTF-8 representation of an em dash.

[Verified] The Product Owner observes the current em-dash filename. It is the intended current identity and must not be renamed by Engineering. File bytes, size, source count, aggregate bytes and the complete content-hash set remain unchanged.

The mandatory stop remains useful because the retained path identity did not match, but there is no unresolved human filename decision. Preserve the original baseline unchanged as historical evidence of the mismatch.

## Authorized continuation

Engineering may resume `V06-PR-01` under its existing scope:

1. Diagnose and, if necessary, correct any candidate or invocation path that can create mojibake in private inventory records. Add a deterministic Unicode filename regression test covering the exact em-dash code point and round-trip serialization.
2. Take two complete read-only inventories of the approved corpus separated by a short quiescence interval.
3. Require exact equality of paths by Unicode code points, sizes and content hashes. Both snapshots must contain the current proper `U+2014` filename and no mojibake equivalent.
4. Bind the matching second inventory as a new baseline while preserving the stopped baseline and this superseding diagnosis.
5. Rerun the full preflight and synthetic gates, then continue the private benchmark and remaining Handoff 258 acceptance evidence in the same task.

Any further path or content drift stops the task. No automatic retry loop, Engineering vault write, scope expansion or new capability is authorized.

Product Owner action: none. Next role: Principal Engineer.
