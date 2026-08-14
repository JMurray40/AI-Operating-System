# Extending Jarvis Core

The prototype is built around two replaceable seams. Both are Protocols, so new
implementations need no changes to domain logic.

## Adding a provider adapter

Implement the `Provider` contract (`src/jarvis_core/providers/base.py`):

```python
class Provider(Protocol):
    name: str
    def summarize(self, package: ContextPackage, model_role: str = "fast") -> ProviderResponse: ...
```

Steps:
1. Create `providers/<name>.py` with a class exposing `name` and `summarize`.
2. Normalize the provider's request/response into `ProviderResponse` (messages,
   tool calls, structured output, usage/cost, timeouts/retries — per
   `SYSTEM_ARCHITECTURE.md`).
3. Register it in `providers/__init__.py::AVAILABLE_PROVIDERS`.
4. Real providers require a **separate design and explicit approval** and must respect
   sensitivity/trust-boundary rules — private/restricted content must not cross to a
   cloud provider without policy + approval. The current placeholder adapters
   (`placeholders.py`) show where Anthropic/OpenAI/Gemini/Ollama attach and intentionally
   raise `NotImplementedError`.

Use **role aliases**, not provider model names, throughout the application.

### ADR-0025 provider-routing constraints

An adapter does not choose itself and cannot request fallback. A policy evaluator selects one exact
destination before candidate generation from the explicit scope, sensitivity ceiling, active grant,
and readiness metadata. `public`/`internal` may use only the exact approved Gemini profile;
`private`/`restricted` and mixed ceilings may use only an exact approved loopback Ollama profile.
Missing/unknown sensitivity has no route.

The Ollama adapter must use the normalized non-streaming gateway, an exact loopback authority and
pinned runtime/model identities. Non-loopback traffic, proxies, redirects, telemetry, updates,
cloud services, ambient endpoint/model overrides, tools, memory and fallback are prohibited. Local
failure is a blocked result, never permission for remote dispatch. New adapters or model profiles
require separate Product Owner approval and the shared C01-C40 contract suite.

## Adding a storage adapter

Implement the `KnowledgeRepository` contract
(`src/jarvis_core/repositories/base.py`):

```python
class KnowledgeRepository(Protocol):
    def discover(self) -> list[Note]: ...
    def all_notes(self) -> list[Note]: ...
```

The first implementation is `FileSystemKnowledgeRepository` (read-only). A future
indexed or service-backed repository (e.g. a rebuildable search index) can replace it as
long as it returns the same `Note` models in deterministic order. **Any write capability
is a separate, explicitly-approved design** — this layer stays read-only until then.

## Where new note types go

Add the type to `models/base.py::NoteType` and, if it has required fields, to
`TYPE_REQUIRED_FIELDS`. Keep values aligned with `VAULT_SCHEMA.md` and update
`schemas/note.schema.json` in the same change (KNOWLEDGE_STANDARD.md).
