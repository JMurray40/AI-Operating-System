# Known Limitations

This is a read-only prototype. By design it does **not**:

- write, move, rename, or delete anything (no vault mutation of any kind);
- access a live vault by default (input defaults to bundled fixtures);
- read `.obsidian/` or other application-managed state;
- connect to real AI providers, or use API keys or the network;
- use a database, embeddings, vector/semantic search, agents, MCP, or a GUI.

Functional limitations of the current implementation:

- **YAML frontmatter only.** No Dataview inline fields or non-YAML metadata.
- **Frontmatter parsing is line/`safe_load` based.** Exotic multi-document YAML is not
  supported; such files are reported, not crashed on.
- **Relationship resolution is name-based** (id/title/alias/stem), case-insensitive.
  It does not yet use folder scoping or block references (`^block-id`).
- **Project membership** is inferred from `projects:` frontmatter and dashboard
  out-links; there is no transitive/graph expansion beyond one hop.
- **Validation** implements the five stages at a practical depth; it is not a full
  JSON-Schema validation against `schemas/note.schema.json` (that is a natural next step).
- **Determinism** assumes a stable filesystem ordering; discovery sorts explicitly to
  remove that dependency.
- **Tested on Python 3.10** in the build sandbox; 3.12+ is the recommended target
  (see ADR-0006).
