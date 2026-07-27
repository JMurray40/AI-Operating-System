# PRD: Mobile Companion

| Field | Value |
|---|---|
| Status | Draft |
| Target | v1.2 |
| Owner | Product/Mobile |
| Depends on | Stable API, identity/device trust, secure remote gateway, sync/conflict protocol |

## Problem statement

Mobile is valuable for capture, approvals, notifications, and quick project orientation, but directly exposing a local vault or desktop service creates severe security and synchronization risk. The companion must extend the trusted system, not become a second brain.

## Goals

- Fast secure capture and review from phone/tablet.
- Project resume and search with scoped cached data.
- Safe approval of pending actions.
- Offline drafts that reconcile without duplicate durable writes.

## User stories

- Capture text/photo/voice into Inbox while away.
- Review and approve a proposed memory or automation action.
- Check a project Resume briefing and open linked resources.
- Revoke a lost device immediately.
- Use offline mode without exposing the full vault.

## Functional requirements

1. Pair through an authenticated desktop/account flow; show device identity and last access.
2. Support inbox text, photo/document scan, voice transcription, and share-sheet URLs.
3. Provide home/project dashboards, search, source previews, and approval queue.
4. Encrypt local cache and allow biometric/app lock.
5. Cache only explicitly scoped data with expiry and remote wipe/revocation.
6. Queue offline captures with client IDs and idempotent reconciliation.
7. Show exact action, target, data egress, and risk before approval.
8. Minimize notification content; sensitivity-aware previews.
9. Never expose local filesystem paths as usable remote endpoints.
10. Export diagnostics without user content by default.

## Non-functional requirements

- Modern supported iOS/Android versions defined near implementation.
- TLS plus application-layer device authentication.
- Lost-device revocation takes effect within five minutes when online.
- Common screens meet mobile accessibility standards.
- Background work respects OS energy and privacy restrictions.

## Architecture considerations

Use a narrow remote gateway or relay with end-to-end device/session protection; never port-forward the local API. Mobile stores drafts and bounded cache, not canonical knowledge. Approval tokens bind action digest, target, expiry, device, and user; notification taps cannot approve directly.

## Edge cases

Clock skew; duplicate offline uploads; revoked device offline; biometric reset; screenshot/screen recording; approval target changes after preview; intermittent connection; large attachment; desktop unavailable.

## Acceptance criteria

- Lost-device and token theft threat tests pass.
- Offline capture reconciles once and retains provenance.
- Approval fails if action digest or target revision changes.
- Full vault cannot be enumerated from mobile API without explicit scope.
- Accessibility, background, and network transition tests pass.

## Future enhancements

Wearable quick capture, voice conversation, location-aware suggestions with opt-in, team approvals, and end-to-end encrypted relay hosting.
