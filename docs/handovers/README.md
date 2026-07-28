# Handoff Router

| Field | Value |
|---|---|
| Purpose | Route contributors to current milestone state without conversation history |
| Owner | Chief of Staff |
| Status | Active |
| Updated | 2026-07-27 |

## Start here

1. Open the active milestone index below.
2. Read its **Current effective state** section.
3. Follow only the artifact marked **Current incoming artifact** for your role.
4. Use historical artifacts for evidence and decision history, not current instructions.
5. If no current artifact is assigned to your role, do not begin that lifecycle stage.

| Milestone | Status | Index |
|---|---|---|
| v0.3.1 — Query Trust Contracts | Librarian closeout complete; final Product Owner action | [v0.3.1 handoff index](v0.3.1/README.md) |
| v0.4 — Project Resume | Planning validated; implementation blocked | [v0.4 planning index](v0.4/README.md) |

Project-wide priority and decision state remains in
[Project Control](../coordination/README.md).

## Supersession rules

- A later accepted revision in the same artifact supersedes earlier dispositions in that
  artifact.
- A later numbered handoff supersedes an earlier handoff only for the lifecycle transition
  it explicitly replaces.
- A Chief of Staff remediation prompt is current only while its named finding remains open.
- Closure of a finding makes its remediation prompt historical; it does not delete it.
- Exact-HEAD approvals apply only to the named commit. A subsequent executable change
  requires renewed clearance.
- Documentation/evidence commits may describe a frozen executable candidate separately;
  both identities must be recorded.

Never infer the latest state from filename order alone. Use the milestone index.

## Required milestone index fields

Every active milestone directory must maintain a `README.md` containing:

- current lifecycle stage;
- next responsible role;
- current incoming artifact;
- frozen or active candidate identity;
- open gates;
- latest effective revision for each cumulative artifact;
- required next output;
- historical/superseded artifact map.

The Chief of Staff updates the milestone index whenever responsibility changes.
