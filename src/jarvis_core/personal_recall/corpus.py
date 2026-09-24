"""Windows-safe, read-only discovery and parsing for the authorized vault view."""
from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

from jarvis_core.models.note import Note
from jarvis_core.parsing.markdown_parser import parse_note
from jarvis_core.personal_recall.policy import RecallPolicy
from jarvis_core.policy.errors import PolicyError
from jarvis_core.policy.sensitivity import within_ceiling

_REPARSE = 0x400
_HIDDEN = 0x2
_EXCLUDED_PARTS = frozenset({
    "attachments", "templates", "archive", "archives", "conversations", "sessions",
    "cache", "caches", "config", "configuration", "legacy-memory", "legacy_memory",
})


@dataclass(frozen=True)
class SourceInventory:
    relpath: str
    size: int
    mtime_ns: int
    sha256: str


@dataclass(frozen=True)
class AcquiredSource:
    """One verified, immutable in-memory source for a single benchmark invocation."""

    inventory: SourceInventory
    path: Path
    data: bytes


def _is_reparse(path: Path) -> bool:
    try:
        return bool(getattr(path.lstat(), "st_file_attributes", 0) & _REPARSE) or path.is_symlink()
    except OSError as exc:
        raise PolicyError("source_boundary:metadata_unavailable") from exc


def _inside(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath((str(path), str(root))) == str(root)
    except ValueError:
        return False


def resolve_roots(policy: RecallPolicy) -> tuple[Path, tuple[Path, ...]]:
    """Resolve approved roots without reading note content."""
    try:
        vault = policy.vault_root.resolve(strict=True)
    except OSError as exc:
        raise PolicyError("preflight:root_unavailable") from exc
    if _is_reparse(vault):
        raise PolicyError("preflight:root_reparse")
    roots: list[Path] = []
    for name in policy.include_roots:
        candidate = vault / name
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            raise PolicyError("preflight:include_unavailable") from exc
        if _is_reparse(candidate) or not _inside(resolved, vault) or not resolved.is_dir():
            raise PolicyError("preflight:include_boundary")
        roots.append(resolved)
    return vault, tuple(roots)


def _walk(root: Path, vault: Path) -> list[Path]:
    files: list[Path] = []
    pending = [root]
    while pending:
        current = pending.pop()
        try:
            entries = sorted(os.scandir(current), key=lambda e: e.name.casefold())
        except OSError as exc:
            raise PolicyError("source_boundary:scan_failed") from exc
        for entry in entries:
            path = Path(entry.path)
            try:
                attributes = getattr(entry.stat(follow_symlinks=False), "st_file_attributes", 0)
            except OSError as exc:
                raise PolicyError("source_boundary:metadata_unavailable") from exc
            if (entry.name.startswith(".") or entry.name.casefold() in _EXCLUDED_PARTS
                    or attributes & _HIDDEN):
                continue
            if entry.is_symlink() or _is_reparse(path):
                raise PolicyError("source_boundary:reparse")
            try:
                resolved = path.resolve(strict=True)
            except OSError as exc:
                raise PolicyError("source_boundary:resolve_failed") from exc
            if not _inside(resolved, vault):
                raise PolicyError("source_boundary:escape")
            if entry.is_dir(follow_symlinks=False):
                pending.append(path)
            elif entry.is_file(follow_symlinks=False):
                if path.suffix.casefold() != ".md":
                    continue
                files.append(path)
    return sorted(files, key=lambda p: p.relative_to(vault).as_posix().casefold())


def inventory_sources(policy: RecallPolicy) -> tuple[SourceInventory, ...]:
    vault, roots = resolve_roots(policy)
    records: list[SourceInventory] = []
    seen: set[str] = set()
    for path in (p for root in roots for p in _walk(root, vault)):
        relpath = path.relative_to(vault).as_posix()
        key = relpath.casefold()
        if key in seen:
            raise PolicyError("source_boundary:duplicate_identity")
        seen.add(key)
        label = policy.classify(relpath)
        if label is None:
            raise PolicyError("source_boundary:unclassified")
        if not within_ceiling(label, policy.max_sensitivity):
            continue
        try:
            stat_before = path.stat()
            with path.open("rb") as stream:
                data = stream.read()
            stat_after = path.stat()
        except OSError as exc:
            raise PolicyError("source_boundary:read_failed") from exc
        if (stat_before.st_size, stat_before.st_mtime_ns) != (
            stat_after.st_size, stat_after.st_mtime_ns
        ):
            raise PolicyError("source_boundary:changed_during_read")
        records.append(SourceInventory(
            relpath, len(data), stat_after.st_mtime_ns, hashlib.sha256(data).hexdigest()
        ))
    return tuple(records)


def build_corpus(policy: RecallPolicy, inventory: tuple[SourceInventory, ...]) -> list[Note]:
    """Read exactly the frozen inventory and construct Core Notes in memory."""
    return build_corpus_from_acquired(policy, acquire_sources(policy, inventory))


def acquire_sources(
    policy: RecallPolicy, inventory: tuple[SourceInventory, ...]
) -> tuple[AcquiredSource, ...]:
    """Open each policy-authorized frozen source once, retaining only verified bytes."""
    acquired: list[AcquiredSource] = []
    for source in inventory:
        label = policy.classify(source.relpath)
        if label is None or not within_ceiling(label, policy.max_sensitivity):
            raise PolicyError("source_boundary:unclassified")
        path, data = read_frozen_source(policy, source)
        acquired.append(AcquiredSource(source, path, data))
    return tuple(acquired)


def build_corpus_from_acquired(
    policy: RecallPolicy, acquired: tuple[AcquiredSource, ...]
) -> list[Note]:
    """Parse already-verified bytes without touching the live vault."""
    notes: list[Note] = []
    for item in acquired:
        source, path, data = item.inventory, item.path, item.data
        try:
            text = data.decode("utf-8")
        except UnicodeError as exc:
            raise PolicyError("source_boundary:parse_input") from exc
        label = policy.classify(source.relpath)
        if label is None or not within_ceiling(label, policy.max_sensitivity):
            raise PolicyError("source_boundary:unclassified")
        parsed = parse_note(path, source.relpath, text)
        if parsed.parse_errors:
            raise PolicyError("source_boundary:parse_failure")
        frontmatter = dict(parsed.frontmatter)
        frontmatter["sensitivity"] = label
        notes.append(replace(
            parsed,
            frontmatter=frontmatter,
            source_text=text,
            source_fingerprint="sha256:" + source.sha256,
            source_bytes=data,
        ))
    return notes


def read_frozen_source(policy: RecallPolicy, source: SourceInventory) -> tuple[Path, bytes]:
    """Recheck path, metadata, and exact bytes before using a frozen source."""
    vault = policy.vault_root.resolve(strict=True)
    path = vault / Path(source.relpath)
    try:
        if _is_reparse(path) or not _inside(path.resolve(strict=True), vault):
            raise PolicyError("source_boundary:changed_path")
        before = path.stat()
        with path.open("rb") as stream:
            data = stream.read()
        after = path.stat()
    except OSError as exc:
        raise PolicyError("source_boundary:read_failed") from exc
    if ((before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns)
            or len(data) != source.size
            or after.st_mtime_ns != source.mtime_ns
            or hashlib.sha256(data).hexdigest() != source.sha256):
        raise PolicyError("source_boundary:fingerprint_changed")
    return path, data


def materialize_private_snapshot(
    policy: RecallPolicy, acquired: tuple[AcquiredSource, ...], destination: Path,
) -> None:
    """Create one exclusive private copy from fully verified in-memory source bytes."""
    if destination.exists() or not destination.parent.is_dir():
        raise PolicyError("snapshot:destination_unavailable")
    identities: set[str] = set()
    for item in acquired:
        relpath = PurePosixPath(item.inventory.relpath)
        if (not relpath.parts or relpath.is_absolute() or ".." in relpath.parts
                or relpath.parts[0] not in policy.include_roots
                or relpath.suffix.casefold() != ".md"
                or not within_ceiling(
                    policy.classify(item.inventory.relpath) or "restricted",
                    policy.max_sensitivity,
                )):
            raise PolicyError("snapshot:source_boundary")
        identity = item.inventory.relpath.casefold()
        if identity in identities:
            raise PolicyError("snapshot:duplicate_identity")
        identities.add(identity)
        if (len(item.data) != item.inventory.size
                or hashlib.sha256(item.data).hexdigest() != item.inventory.sha256):
            raise PolicyError("snapshot:fingerprint_mismatch")
    destination.mkdir()
    for name in policy.include_roots:
        (destination / name).mkdir()
    for item in acquired:
        relative = PurePosixPath(item.inventory.relpath)
        target = destination.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(item.data)
            stream.flush()
            os.fsync(stream.fileno())
        os.utime(target, ns=(item.inventory.mtime_ns, item.inventory.mtime_ns))
        os.chmod(target, stat.S_IREAD)


def verify_private_snapshot(
    policy: RecallPolicy, expected: tuple[SourceInventory, ...]
) -> tuple[SourceInventory, ...]:
    """Independently reject extras, reparses, writes and content drift in the copy."""
    root, _roots = resolve_roots(policy)
    expected_files = {source.relpath for source in expected}
    allowed_dirs = {"", *policy.include_roots}
    for relpath in expected_files:
        parent = PurePosixPath(relpath).parent
        while str(parent) != ".":
            allowed_dirs.add(parent.as_posix())
            parent = parent.parent
    observed: set[str] = set()
    folded: set[str] = set()
    def scan_error(_error: OSError) -> None:
        raise PolicyError("snapshot:scan_failed")

    for current, dirs, files in os.walk(root, followlinks=False, onerror=scan_error):
        current_path = Path(current)
        for name in dirs:
            path = current_path / name
            relpath = path.relative_to(root).as_posix()
            if _is_reparse(path) or relpath not in allowed_dirs:
                raise PolicyError("snapshot:unexpected_entry")
        for name in files:
            path = current_path / name
            relpath = path.relative_to(root).as_posix()
            folded_name = relpath.casefold()
            if (_is_reparse(path) or relpath not in expected_files
                    or path.suffix.casefold() != ".md" or folded_name in folded):
                raise PolicyError("snapshot:unexpected_entry")
            folded.add(folded_name)
            observed.add(relpath)
            attributes = getattr(path.stat(), "st_file_attributes", 0)
            if not attributes & stat.FILE_ATTRIBUTE_READONLY:
                raise PolicyError("snapshot:writable_file")
    if observed != expected_files:
        raise PolicyError("snapshot:missing_source")
    actual = inventory_sources(policy)
    if [(row.relpath, row.size, row.sha256) for row in actual] != [
        (row.relpath, row.size, row.sha256) for row in expected
    ]:
        raise PolicyError("snapshot:inventory_mismatch")
    return actual
