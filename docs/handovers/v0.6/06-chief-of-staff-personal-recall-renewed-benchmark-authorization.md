# Handoff 06 - Personal Recall renewed benchmark authorization

Date: 2026-09-22
Sender: Chief of Staff
Receiver: Principal Engineer
Task: `V06-PR-01`
Disposition: **ONE RENEWED BENCHMARK ATTEMPT AUTHORIZED AFTER QUIESCENCE GATE**

## Independent disposition

[Verified] The completed private manifest validated. The benchmark stopped before its first question because one frozen path returned fixed category `source_boundary:metadata_unavailable`. Complete inventories immediately before and after the event match the governed v2 baseline exactly across all 27 paths, sizes, timestamps and content hashes. The affected path is accessible again and matches by Unicode code point.

[Inferred] The evidence supports a transient filesystem-availability event rather than a rename, content change, candidate defect or benchmark-dependent failure. Because no query ran and no result was observed, one renewed attempt does not create result-shopping risk.

## Authorized route

Engineering may make exactly one renewed benchmark invocation under the existing candidate and private manifest, only after:

1. Taking three complete read-only inventories over a minimum two-minute quiescence window.
2. Requiring exact equality with the governed v2 baseline for every relative path by code point, size, timestamp and content hash.
3. Confirming every frozen source permits a read-only metadata lookup and complete binary read immediately before invocation.
4. Reconfirming the socket/DNS guard, absent result files, unchanged candidate digest, unchanged private manifest digest and zero unauthorized processes.

The renewed invocation must run the full planned three-run benchmark as one attempt. It may not silently skip, substitute or retry an individual source or question. Preserve the stopped attempt evidence separately.

If any preflight differs, or any source becomes unavailable again, stop without another retry. A repeated availability failure requires a separately reviewed immutable corpus-acquisition design; it may not be solved by pausing sync software, copying private note content, adding per-file retries or weakening source-integrity checks under this authority.

All Handoff 258 exclusions remain in force. Product Owner action: none. Next role: Principal Engineer.
