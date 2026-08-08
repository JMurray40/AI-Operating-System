# Packaging Acquisition Evidence — Handoff 32

**Bound candidate**

- executable commit `d7105e4f6793f1317ba15f98c7e9c9f03c9f8910`
- executable tree `f221c7451726437956acf61ecad2fc701bbbbefe`
- Handoff 30 SHA-256 `268dcf19b0ab0ebab967158be8ea2448943d874784e190293e943b8991958aef`

This acquisition did **not** export, inspect, build, install, or execute the candidate. No
build, staging, or quarantine directory was created. No A12 environment was touched. No
provider or credential was used.

## 1. Environment

- Acquisition Python: `3.10.12`
- Acquisition OS: Linux (Ubuntu 22.04, x86_64), disposable sandbox shell
- Acquisition tool: `pip 25.3`
- Package index: `pypi.org` (default simple index, not overridden)
- File-delivery host: `files.pythonhosted.org`
- Proxy: a sandbox-level transport proxy (HTTP CONNECT / SOCKS5, localhost-bound) was present
  for all outbound sandbox traffic during acquisition. This is the sandbox's baseline network
  path, not a chosen alternate index/mirror and not credentialed — the index and file host
  actually contacted were the unmodified PyPI defaults above. Disclosed as a limitation for
  Chief-of-Staff judgment.
- Network access ended when acquisition completed; no persistent network capability remains
  open for later stages.

## 2. Acquisition method

Binary-only, no-dependency downloads (`pip download --no-deps --only-binary=:all:`), one
command per package, private paths redacted:

```
pip download pip==26.1.2 --no-deps --only-binary=:all: --no-cache-dir -d <private-dir>
pip download setuptools==80.9.0 --no-deps --only-binary=:all: --no-cache-dir -d <private-dir>
pip download wheel==0.45.1 --no-deps --only-binary=:all: --no-cache-dir -d <private-dir>
pip download PyYAML==6.0.3 --no-deps --only-binary=:all: \
  --platform win_amd64 --implementation cp --python-version 314 --abi cp314 \
  --no-cache-dir -d <private-dir>
```

No source distribution, prerelease, version substitution, or additional package was requested
or received.

## 3. Existing retained PyYAML wheel — validation and disposition

Handoff 31 reported a private retained file eligible for validation:
`pyyaml-6.0.3-cp314-cp314-win_amd64.whl`, size `156429` bytes, SHA-256
`4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac` (relative category: v0.4 A12
wheelhouse).

Read-only validation confirmed: filename, size, and SHA-256 match exactly; the archive is free
of duplicate, absolute, traversal, reserved-device, alternate-stream, case-collision, and
symlink members; distribution/version (`PyYAML 6.0.3`), compatibility tag
(`cp314-cp314-win_amd64`), METADATA, WHEEL, and RECORD are present and internally consistent
(RECORD hashes verified against every archive member, zero mismatches); license is MIT.

**Source provenance could not be established.** The only nearby record was an installed
package's `direct_url.json` recording a `file://` install from that same local wheelhouse path
— evidence of what installed from the file, not of where the file itself came from. No
PyPI/files.pythonhosted.org download record for the retained file could be located.

**Disposition: reuse rejected.** Per Handoff 32 §3, an unestablished required fact means the
file may not be accepted; a fresh exact `PyYAML==6.0.3` `cp314-cp314-win_amd64` binary wheel was
acquired instead (Section 2 method, above). The freshly acquired wheel is byte-identical (same
size and SHA-256) to the retained file, which corroborates but does not substitute for direct
provenance. The **freshly acquired copy**, with its own logged `files.pythonhosted.org` source
URL, is the accepted file below — the retained file was not moved, modified, or used as the
accepted artifact.

## 4. Accepted files

| Distribution | Version | Tag | Bytes | SHA-256 | Source | License |
|---|---|---|---|---|---|---|
| pip | 26.1.2 | py3-none-any | 1813144 | `382ff9f685ee3bc25864f820aa50505825f10f5458ffff07e30a6d96e5715cab` | fresh, files.pythonhosted.org | MIT |
| setuptools | 80.9.0 | py3-none-any | 1201486 | `062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922` | fresh, files.pythonhosted.org | MIT |
| wheel | 0.45.1 | py3-none-any | 72494 | `708e7481cc80179af0e556bbf0cc00b8444c7321e2700b8d8580231d13017248` | fresh, files.pythonhosted.org | MIT |
| PyYAML | 6.0.3 | cp314-cp314-win_amd64 | 156429 | `4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac` | fresh, files.pythonhosted.org | MIT |

Exactly four files accepted. No source distribution and no unrelated package was acquired.

## 5. Validation performed on every accepted file

- Independent SHA-256 rehash after copy into the private acquisition path — byte-identical to
  the download-time hash in every case.
- Archive hazard scan: zero duplicate, absolute-path, path-traversal, reserved-device-name,
  alternate-data-stream, case-collision, or symlink members in any of the four wheels.
- `WHEEL` file compatibility tag confirmed against the required tag for each package.
- Top-level `RECORD` verified against actual archive members for each package: every listed
  file present with a matching hash and size, and no archive member absent from `RECORD`. (Note:
  `setuptools` additionally bundles 16 nested vendored-dependency `RECORD` files under
  `setuptools/_vendor/`, each scoped to its own vendored subtree — this is setuptools' standard
  vendoring layout, not an additional acquired package, and was excluded from the top-level
  check by design.)
- `METADATA` name/version cross-checked against the requested distribution/version for each
  package.

No archive, RECORD, or tag defect was found in any of the four accepted files.

## 6. Private outputs

- accepted wheels: `data/v0.5-evidence/d7105e4/packaging/acquisition/wheelhouse/` (4 files)
- raw acquisition evidence: `data/v0.5-evidence/d7105e4/packaging/acquisition/raw/` (download
  URL log, per-file hazard-scan and RECORD-verification transcripts, retained-file validation
  transcript)
- acquisition manifest: `data/v0.5-evidence/d7105e4/packaging/acquisition/acquisition-manifest.json`
  (7405 bytes, SHA-256 `20d3cb89c7e3ef22692f9342d55f51cb2ff28bd9b7a0d4016b5bdd214a13576d`)

All three paths were confirmed git-ignored and untracked before writing, and remain so.

## 7. Limitations

- The sandbox-level transport proxy noted in Section 1 could not be disabled; it is
  infrastructure-level and applies to all outbound sandbox traffic, not something selected for
  this acquisition. The index and file host contacted were not substituted.
- Source provenance for the pre-existing retained PyYAML wheel could not be established; reuse
  was rejected on that basis alone (see Section 3).

## 8. Confirmation

- Candidate commit/tree above: not exported, inspected, modified, built, installed, or executed.
- No build, staging, or quarantine directory created.
- No A12 environment created, installed, uninstalled, reinstalled, or executed.
- No provider, credential, pilot, or vault used.
- No Quality run, merge, push, tag, publication, or release performed.
- Network access used only for the four acquisition downloads above; ended on completion.
