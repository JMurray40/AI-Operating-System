# Handoff 22b — Chief-of-Staff Personal Recall Integration Authorization

## 1. Decision and task

The Product Owner approved the complete Handoff 22 implementation package on 2026-09-25.

**Task `V06-PR-07` is AUTHORIZED.**

Owner: Principal Engineer. Reviewer: Chief Architect / CTO. Chief-of-Staff routing applies.

The required outcome is one native-Windows runnable, fixture-only Personal Recall flow in the accepted text prototype, complete offline verification, a deterministic operator demonstration, and one immutable local candidate commit in each repository.

## 2. Exact bases

- Core commit `cf7ac875cea1843295e825ea4322696d42af9ce1`, tree `56b27a9d6663eabb39692925f662c663ca6adc62`.
- Voice commit `0588d3b05af2f225e63457583e7c321b283ddeb2`, tree `0acf74ae09ad09cc86dc5e6eb9d90aec37ba4528`.

Engineering must create and verify dedicated worktrees and branches from these exact bases before editing. The required native Git writer is `Mighty_Mouse/jmurr`; no elevation, ACL change, persistent global trust edit or Git-policy bypass is authorized.

## 3. Authorized candidate paths

Only these eighteen paths may change; a subset is allowed:

### Core

1. `src/jarvis_core/personal_recall/__init__.py`
2. `src/jarvis_core/personal_recall/contract.py`
3. `src/jarvis_core/personal_recall/application.py`
4. `src/jarvis_core/personal_recall/corpus.py`
5. `tests/unit/test_personal_recall_application.py`
6. `tests/unit/test_personal_recall.py`
7. `docs/software/PERSONAL_RECALL_APPLICATION_V1.md`

### Voice

8. `voice_shell/contracts.py`
9. `voice_shell/recall_bridge.py`
10. `voice_shell/controller.py`
11. `voice_shell/cli.py`
12. `voice_shell/recall_prototype.py`
13. `tests/voice_shell/test_recall_bridge.py`
14. `tests/voice_shell/test_recall_controller.py`
15. `tests/voice_shell/test_recall_interactive.py`
16. `tests/voice_shell/test_structural.py`
17. `tests/voice_shell/test_core_bridge_structural.py`
18. `docs/PERSONAL_RECALL_PROTOTYPE.md`

An additional candidate path is a scope change and requires one consolidated decision before it is edited.

## 4. Authorized execution

Engineering may:

- create the two dedicated worktrees and branches;
- implement the complete Handoff 22 API, DTO, lifecycle, bridge, controller, CLI and fixture design;
- create and delete only owned synthetic `jarvis-recall-prototype-` temporary fixtures;
- run all focused and complete Core/Voice tests, Ruff, mypy, structural/privacy checks and the scripted and interactive demonstrations;
- write the six evidence and coordination outputs listed in Handoff 22 section 7;
- stage only the authorized candidate paths;
- create one normal local commit in each repository; and
- return Handoff 23 with every R01–R30 disposition and exact paired candidate identities.

Ordinary implementation defects and in-scope corrections remain inside `V06-PR-07`. They must not become serial planning or review tasks.

## 5. Prohibited activity

No private-vault read, private-note copy, live benchmark, persistent index, embedding, provider or credential use, network access, real microphone/speaker activation, policy/manifest edit, dependency acquisition, merge, push, tag, packaging, publication or release is authorized.

The deleted private proof snapshot must not be recreated. Recall must remain isolated from conversation prompts, history, approvals, providers and speech.

## 6. Return and stop rules

Pass route: return one Handoff 23 to the Chief Architect / CTO with complete evidence and both clean immutable candidates.

Stop before implementation only for unavailable native Git authority or a missing external capability. Stop during implementation only for an unsafe/irreversible condition or a genuinely required scope change outside the eighteen paths. Ordinary test failures are diagnosed and corrected within this task.

No task is accepted by its author. No implementation has been performed by this authorization.

