# v0.4 A12 Packaging and Recovery Evidence — `ff402d7`

**Date:** 2026-07-29

**Reviewer:** Independent Codex non-author reviewer

**Disposition:** **PASS**

## Bound identities

| Item | Identity |
|---|---|
| Executable | `ff402d7f82c061426a5e960f7177d916c355bbf2` |
| Executable tree | `a7ff2c023b0e59df1f8bbc2ad05a3af843a5e344` |
| Candidate wheel | `jarvis_core-0.1.0-py3-none-any.whl` |
| Candidate wheel SHA-256 | `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3` |
| Candidate wheel size | 126,683 bytes |
| PyYAML wheel SHA-256 | `4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac` |
| Isolated runtime | CPython 3.14.4, pip 26.0.1 |

The wheel bound to `014076c` was not installed or reused.

## Independent payload verification

- Wheel digest and size matched Engineering's return.
- Inventory contained 74 entries: 68 `jarvis_core` payload files and 6 distribution
  metadata entries.
- All 68 runtime payload files were byte-identical to
  `ff402d7:src/jarvis_core/*`.
- No payload was missing, mismatched, unbound, or under an unexpected top-level package.
- Distribution metadata declared `jarvis-core` 0.1.0, Python 3.10 or newer,
  `PyYAML>=6.0`, `jarvis = jarvis_core.cli:main`, and `py3-none-any`.

## Offline installation boundary

A new isolated environment was created. The retained PyYAML wheel and candidate wheel were
installed with:

```text
pip install --no-index --no-deps <verified-wheel>
```

Setuptools was absent. Installed `jarvis`, `jarvis resume`, and `jarvis resume-doctor`
help commands exited successfully.

Before either classified pilot was exposed, the exact isolated interpreter attempted an
outbound HTTPS connection. It failed with Windows error 10051, network unreachable.

## Affected behavior

| Check | Result |
|---|---|
| Survivor granted repository | Partial briefing, 10 repository citations, no limitation |
| Survivor doctor | Exit 0, healthy |
| AI Prompt Suite no-Git degradation | Partial, `unavailable_not_a_repository`, no repository citation |
| AI Prompt Suite doctor | Exit 0, healthy |
| Deterministic fixture | Exit 0; 11,182 bytes; stable SHA-256 |

The deterministic fixture SHA-256 before and after reinstall was:

```text
8e5136c86a61ba877c5e0af2996b7d798ca0888c3fc47b877c019ecc322953e5
```

## Uninstall and reinstall

Uninstall removed the `jarvis` command. The candidate wheel digest was reverified, and the
same wheel was reinstalled offline with dependency resolution disabled. Help, fixture,
granted repository, no-Git degradation, and both doctors reproduced their pre-reinstall
exit codes and exact stdout SHA-256 values.

## No-artifact and integrity result

The installed candidate contains no temporary-file security subsystem or related imports.
No new Jarvis Git-configuration file, directory, ACL namespace, global configuration, or
repository configuration was created. Pre-existing `jarvis-safe*` artifacts from superseded
candidate testing predated this run and were neither accessed nor modified.

The complete accepted before/after comparison was exact for:

- Survivor canonical files;
- Survivor worktree status, index, refs, reflogs, configuration, remotes, ownership,
  reachable objects, and recorded loose-object boundary;
- AI Prompt Suite canonical files and no-Git state;
- deterministic fixture files; and
- the integrity command set.

| Boundary | Stable SHA-256 |
|---|---|
| Survivor canonical files | `f6a92d78e7b42f62f7b7abe9fa6385de53cb9b87e9c601911bfb9d6febbb32a3` |
| Survivor reachable Git state | `27b23f5b25ebf8154d995a0ce22c2b6cecd1cea0d1b167ab7dd74f2bb87e972d` |
| AI Prompt Suite canonical files | `7caa0e245ecd6a9590095c5f1e2850e049e0b31e3d5c7899a4a4f35e0dd920a5` |
| Deterministic fixture | `fff1a61e1a5212da2e17020687f63c9ee353020c059df5d38b563927e88979e4` |

Private evidence files remain under the approved ignored evidence root. Their integrity
capture digests are:

- before: `e6d01b5a55dc80c293a7fd7860221c7ce3d496afd91a81b346a9c8d157a1a63a`;
- after: `fc058663e04143a4bcbc73ab464de2e2c7b8af8f5eae7008dc9dc22a3902c963`.

The files differ only in phase, timestamp, and evidence-file identity; every compared
canonical, Git, fixture, no-Git, and command boundary is equal.
