# Prepared Prompt — Packaging, Recovery, Privacy, and Integrity Review

**Inactive until:** a frozen candidate and its installation/recovery documentation exist.

Act as a release-operations reviewer. Independently verify A7 and A12 plus the final CTO
brief's packaging, diagnostics, recovery, privacy, and unchanged-source requirements.

Use a clean supported Windows environment and exact candidate `<CANDIDATE_SHA>`. Follow
only published documentation as a non-author would. Test installation, `jarvis --help`,
fixture resume, both authorized pilot commands, no-Git degradation, authorized local Git,
invalid vault/root diagnostics, missing/corrupt derived-state rebuild, uninstall/reinstall,
and stdout-only product behavior.

Capture before/after vault and Git inventories, hashes, timestamps where required, status,
HEAD, refs, config, index, packed refs, and derived-state location. Confirm private
evidence stays in the approved ignored non-vault destination and committed evidence is
redacted.

Do not repair documentation or implementation during the review. Do not write canonical
sources, access network/GitHub, expose private content, merge, push, or release.

Append evidence to the QA handoff or create the exact artifact assigned by the active CTO
disposition. Report reproducible failures, environmental skips, and whether A7/A12 pass.
