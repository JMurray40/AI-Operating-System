"""V05-PT-37: the local profile's readiness/capacity/in-flight lifecycle state machine
(``LocalReadinessGateway``, Handoff 147 sec 3.2, corrected/extended by 147b sec 3). Every
transition, deadline, and sample-count boundary is exercised with ``SyntheticClock`` /
``SyntheticCapacityProbe`` fakes only -- no real time.sleep, no live loopback endpoint
(Handoff 148 sec 3).
"""

from __future__ import annotations

import pytest

from jarvis_core.providers.local_ollama import (
    ADMISSION_MAX_LOAD_PERCENT,
    ADMISSION_MIN_AVAIL_BYTES,
    ADMISSION_SAMPLES,
    COLD_TO_READY_CEILING_SECONDS,
    READINESS_PROBE_DEADLINE_SECONDS,
    READY_EXPIRY_SECONDS,
    RECOVERY_MAX_LOAD_PERCENT,
    RECOVERY_MIN_AVAIL_BYTES,
    RECOVERY_SAMPLES,
    RUNTIME_LOSS_LOAD_PERCENT,
    RUNTIME_MIN_AVAIL_BYTES,
    RUNTIME_SAMPLES,
    LocalGatewayBlocked,
    LocalReadinessGateway,
    LocalReadinessState,
    MemoryObservation,
    SyntheticCapacityProbe,
    SyntheticClock,
)

_OK = MemoryObservation(avail_phys_bytes=16 * 1024**3, memory_load_percent=10)
_ADMISSION_LOW_MEM = MemoryObservation(avail_phys_bytes=ADMISSION_MIN_AVAIL_BYTES - 1, memory_load_percent=10)
_ADMISSION_HIGH_LOAD = MemoryObservation(avail_phys_bytes=ADMISSION_MIN_AVAIL_BYTES, memory_load_percent=ADMISSION_MAX_LOAD_PERCENT + 1)
_RUNTIME_LOW_MEM = MemoryObservation(avail_phys_bytes=RUNTIME_MIN_AVAIL_BYTES - 1, memory_load_percent=10)
_RUNTIME_HIGH_LOAD = MemoryObservation(avail_phys_bytes=RUNTIME_MIN_AVAIL_BYTES, memory_load_percent=RUNTIME_LOSS_LOAD_PERCENT)
_RECOVERY_OK = MemoryObservation(avail_phys_bytes=RECOVERY_MIN_AVAIL_BYTES, memory_load_percent=RECOVERY_MAX_LOAD_PERCENT)
_RECOVERY_NOT_ENOUGH = MemoryObservation(avail_phys_bytes=RECOVERY_MIN_AVAIL_BYTES - 1, memory_load_percent=RECOVERY_MAX_LOAD_PERCENT)


def _gateway() -> tuple[LocalReadinessGateway, SyntheticCapacityProbe, SyntheticClock]:
    clock = SyntheticClock()
    probe = SyntheticCapacityProbe()
    return LocalReadinessGateway(capacity_probe=probe, clock=clock), probe, clock


def _warm_to_ready(gw: LocalReadinessGateway) -> None:
    gw.begin_warming()
    gw.complete_warm_up(
        min_probe_ok=True, min_probe_elapsed_seconds=1.0, max_probe_ok=True, max_probe_elapsed_seconds=1.0
    )
    assert gw.state is LocalReadinessState.READY


# ------------------------------------------------------------------ cold -> ready (147 sec 3.2)
def test_initial_state_is_cold() -> None:
    gw, _, _ = _gateway()
    assert gw.state is LocalReadinessState.COLD


def test_begin_warming_from_cold_enters_warming() -> None:
    gw, _, _ = _gateway()
    gw.begin_warming()
    assert gw.state is LocalReadinessState.WARMING


@pytest.mark.parametrize("start", [LocalReadinessState.WARMING, LocalReadinessState.READY])
def test_begin_warming_rejected_from_invalid_states(start: LocalReadinessState) -> None:
    gw, probe, _ = _gateway()
    if start is LocalReadinessState.WARMING:
        gw.begin_warming()
    elif start is LocalReadinessState.READY:
        _warm_to_ready(gw)
    with pytest.raises(LocalGatewayBlocked) as ei:
        gw.begin_warming()
    assert ei.value.details["reason"] == "invalid_transition"


@pytest.mark.parametrize("start", [LocalReadinessState.NOT_READY, LocalReadinessState.UNAVAILABLE])
def test_begin_warming_allowed_from_not_ready_and_unavailable(start: LocalReadinessState) -> None:
    gw, probe, clock = _gateway()
    if start is LocalReadinessState.NOT_READY:
        _warm_to_ready(gw)
        for _ in range(ADMISSION_SAMPLES):
            probe.push(_OK)
        clock.advance(READY_EXPIRY_SECONDS + 1)
        with pytest.raises(LocalGatewayBlocked):
            gw.check_admission()  # expires -> NOT_READY
        assert gw.state is LocalReadinessState.NOT_READY
    else:
        gw.begin_warming()
        with pytest.raises(LocalGatewayBlocked):
            gw.complete_warm_up(
                min_probe_ok=False, min_probe_elapsed_seconds=1.0, max_probe_ok=True, max_probe_elapsed_seconds=1.0
            )
        assert gw.state is LocalReadinessState.UNAVAILABLE
    gw.begin_warming()
    assert gw.state is LocalReadinessState.WARMING


def test_complete_warm_up_outside_warming_rejected() -> None:
    gw, _, _ = _gateway()
    with pytest.raises(LocalGatewayBlocked) as ei:
        gw.complete_warm_up(min_probe_ok=True, min_probe_elapsed_seconds=1.0, max_probe_ok=True, max_probe_elapsed_seconds=1.0)
    assert ei.value.details["reason"] == "invalid_transition"


def test_complete_warm_up_success_enters_ready() -> None:
    gw, _, _ = _gateway()
    _warm_to_ready(gw)


def test_complete_warm_up_min_probe_failed_enters_unavailable() -> None:
    gw, _, _ = _gateway()
    gw.begin_warming()
    with pytest.raises(LocalGatewayBlocked) as ei:
        gw.complete_warm_up(min_probe_ok=False, min_probe_elapsed_seconds=1.0, max_probe_ok=True, max_probe_elapsed_seconds=1.0)
    assert ei.value.details["reason"] == "min_probe_failed"
    assert gw.state is LocalReadinessState.UNAVAILABLE


def test_complete_warm_up_max_probe_failed_enters_unavailable() -> None:
    gw, _, _ = _gateway()
    gw.begin_warming()
    with pytest.raises(LocalGatewayBlocked) as ei:
        gw.complete_warm_up(min_probe_ok=True, min_probe_elapsed_seconds=1.0, max_probe_ok=False, max_probe_elapsed_seconds=1.0)
    assert ei.value.details["reason"] == "max_probe_failed"
    assert gw.state is LocalReadinessState.UNAVAILABLE


@pytest.mark.parametrize(
    ("elapsed", "should_fail"),
    [(READINESS_PROBE_DEADLINE_SECONDS, False), (READINESS_PROBE_DEADLINE_SECONDS + 0.001, True)],
)
def test_min_probe_deadline_boundary(elapsed: float, should_fail: bool) -> None:
    gw, _, _ = _gateway()
    gw.begin_warming()
    if should_fail:
        with pytest.raises(LocalGatewayBlocked) as ei:
            gw.complete_warm_up(min_probe_ok=True, min_probe_elapsed_seconds=elapsed, max_probe_ok=True, max_probe_elapsed_seconds=1.0)
        assert ei.value.details["reason"] == "min_probe_failed"
    else:
        gw.complete_warm_up(min_probe_ok=True, min_probe_elapsed_seconds=elapsed, max_probe_ok=True, max_probe_elapsed_seconds=1.0)
        assert gw.state is LocalReadinessState.READY


@pytest.mark.parametrize(
    ("elapsed", "should_fail"),
    [(READINESS_PROBE_DEADLINE_SECONDS, False), (READINESS_PROBE_DEADLINE_SECONDS + 0.001, True)],
)
def test_max_probe_deadline_boundary(elapsed: float, should_fail: bool) -> None:
    gw, _, _ = _gateway()
    gw.begin_warming()
    if should_fail:
        with pytest.raises(LocalGatewayBlocked) as ei:
            gw.complete_warm_up(min_probe_ok=True, min_probe_elapsed_seconds=1.0, max_probe_ok=True, max_probe_elapsed_seconds=elapsed)
        assert ei.value.details["reason"] == "max_probe_failed"
    else:
        gw.complete_warm_up(min_probe_ok=True, min_probe_elapsed_seconds=1.0, max_probe_ok=True, max_probe_elapsed_seconds=elapsed)
        assert gw.state is LocalReadinessState.READY


@pytest.mark.parametrize(
    ("elapsed", "should_fail"),
    [(COLD_TO_READY_CEILING_SECONDS, False), (COLD_TO_READY_CEILING_SECONDS + 0.001, True)],
)
def test_cold_to_ready_ceiling_boundary(elapsed: float, should_fail: bool) -> None:
    gw, _, clock = _gateway()
    gw.begin_warming()
    clock.advance(elapsed)
    if should_fail:
        with pytest.raises(LocalGatewayBlocked) as ei:
            gw.complete_warm_up(min_probe_ok=True, min_probe_elapsed_seconds=1.0, max_probe_ok=True, max_probe_elapsed_seconds=1.0)
        assert ei.value.details["reason"] == "cold_to_ready_ceiling"
        assert gw.state is LocalReadinessState.UNAVAILABLE
    else:
        gw.complete_warm_up(min_probe_ok=True, min_probe_elapsed_seconds=1.0, max_probe_ok=True, max_probe_elapsed_seconds=1.0)
        assert gw.state is LocalReadinessState.READY


# ------------------------------------------------------------------ check_admission (pre-retrieval)
@pytest.mark.parametrize("state", [LocalReadinessState.COLD, LocalReadinessState.WARMING])
def test_check_admission_rejected_when_cold_or_warming(state: LocalReadinessState) -> None:
    gw, _, _ = _gateway()
    if state is LocalReadinessState.WARMING:
        gw.begin_warming()
    with pytest.raises(LocalGatewayBlocked) as ei:
        gw.check_admission()
    assert ei.value.code == "blocked_local_not_ready"
    assert ei.value.details["reason"] == state.value


def test_check_admission_rejected_when_unavailable() -> None:
    gw, _, _ = _gateway()
    gw.begin_warming()
    with pytest.raises(LocalGatewayBlocked):
        gw.complete_warm_up(min_probe_ok=False, min_probe_elapsed_seconds=1.0, max_probe_ok=True, max_probe_elapsed_seconds=1.0)
    with pytest.raises(LocalGatewayBlocked) as ei:
        gw.check_admission()
    assert ei.value.code == "blocked_local_unavailable"
    assert ei.value.details["reason"] == "unavailable"


def test_check_admission_passes_when_ready_with_good_capacity() -> None:
    gw, probe, _ = _gateway()
    _warm_to_ready(gw)
    for _ in range(ADMISSION_SAMPLES):
        probe.push(_OK)
    gw.check_admission()  # must not raise


@pytest.mark.parametrize("bad_sample", [_ADMISSION_LOW_MEM, _ADMISSION_HIGH_LOAD])
def test_check_admission_blocked_on_capacity_violation(bad_sample: MemoryObservation) -> None:
    gw, probe, _ = _gateway()
    _warm_to_ready(gw)
    probe.push(bad_sample)
    with pytest.raises(LocalGatewayBlocked) as ei:
        gw.check_admission()
    assert ei.value.code == "blocked_local_capacity"
    assert ei.value.details["reason"] == "admission_memory"
    # A capacity violation leaves readiness UNCHANGED (147b sec 3.1) -- not demoted.
    assert gw.state is LocalReadinessState.READY


def test_check_admission_metric_unavailable_enters_unavailable() -> None:
    gw, probe, _ = _gateway()
    _warm_to_ready(gw)
    # An exhausted synthetic queue reads as "metric unavailable".
    with pytest.raises(LocalGatewayBlocked) as ei:
        gw.check_admission()
    assert ei.value.code == "blocked_local_unavailable"
    assert ei.value.details["reason"] == "metric_unavailable"
    assert gw.state is LocalReadinessState.UNAVAILABLE


def test_check_admission_samples_exactly_three_consecutive() -> None:
    gw, probe, _ = _gateway()
    _warm_to_ready(gw)
    for _ in range(ADMISSION_SAMPLES):
        probe.push(_OK)
    gw.check_admission()
    assert len(probe._queue) == 0, "expected exactly ADMISSION_SAMPLES samples to be consumed"


@pytest.mark.parametrize(
    ("elapsed", "should_expire"), [(READY_EXPIRY_SECONDS, False), (READY_EXPIRY_SECONDS + 0.001, True)]
)
def test_ready_expiry_boundary(elapsed: float, should_expire: bool) -> None:
    gw, probe, clock = _gateway()
    _warm_to_ready(gw)
    clock.advance(elapsed)
    if should_expire:
        with pytest.raises(LocalGatewayBlocked) as ei:
            gw.check_admission()
        assert ei.value.code == "blocked_local_not_ready"
        assert ei.value.details["reason"] == "expired"
        assert gw.state is LocalReadinessState.NOT_READY
    else:
        for _ in range(ADMISSION_SAMPLES):
            probe.push(_OK)
        gw.check_admission()  # must not raise; still counts as READY at the boundary


# ------------------------------------------------------------------ in-flight / no queue (147 sec 3)
def test_in_flight_rejects_a_second_concurrent_attempt() -> None:
    gw, probe, _ = _gateway()
    _warm_to_ready(gw)
    for _ in range(ADMISSION_SAMPLES):
        probe.push(_OK)
    gw.check_admission()
    gw.begin_attempt()
    with pytest.raises(LocalGatewayBlocked) as ei:
        gw.check_admission()
    assert ei.value.details["reason"] == "in_flight"
    with pytest.raises(LocalGatewayBlocked):
        gw.begin_attempt()
    gw.end_attempt(success=True)
    for _ in range(ADMISSION_SAMPLES):
        probe.push(_OK)
    gw.check_admission()  # must not raise once released


def test_end_attempt_success_refreshes_ready_since(monkeypatch=None) -> None:
    gw, probe, clock = _gateway()
    _warm_to_ready(gw)
    gw.begin_attempt()
    clock.advance(100.0)
    gw.end_attempt(success=True)
    clock.advance(READY_EXPIRY_SECONDS - 1)  # would have expired from the ORIGINAL ready_since
    for _ in range(ADMISSION_SAMPLES):
        probe.push(_OK)
    gw.check_admission()  # must not raise -- ready_since was refreshed by the successful end


# ------------------------------------------------------------------ runtime capacity loss (147b sec 3.1)
def test_runtime_capacity_loss_requires_three_consecutive_violations() -> None:
    gw, _, _ = _gateway()
    _warm_to_ready(gw)
    assert gw.observe_runtime_capacity(_RUNTIME_LOW_MEM) is False
    assert gw.state is LocalReadinessState.READY
    assert gw.observe_runtime_capacity(_RUNTIME_LOW_MEM) is False
    assert gw.state is LocalReadinessState.READY
    assert gw.observe_runtime_capacity(_RUNTIME_LOW_MEM) is True  # third consecutive -> loss
    assert gw.state is LocalReadinessState.NOT_READY


def test_runtime_capacity_violation_streak_resets_on_a_good_sample() -> None:
    gw, _, _ = _gateway()
    _warm_to_ready(gw)
    assert gw.observe_runtime_capacity(_RUNTIME_LOW_MEM) is False
    assert gw.observe_runtime_capacity(_OK) is False  # resets the consecutive count
    assert gw.observe_runtime_capacity(_RUNTIME_LOW_MEM) is False
    assert gw.observe_runtime_capacity(_RUNTIME_LOW_MEM) is False
    assert gw.state is LocalReadinessState.READY  # only 2 consecutive so far


def test_runtime_capacity_high_load_boundary_uses_ge_not_gt() -> None:
    gw, _, _ = _gateway()
    _warm_to_ready(gw)
    at_ceiling_ok = MemoryObservation(avail_phys_bytes=RUNTIME_MIN_AVAIL_BYTES, memory_load_percent=RUNTIME_LOSS_LOAD_PERCENT - 1)
    for _ in range(RUNTIME_SAMPLES):
        assert gw.observe_runtime_capacity(at_ceiling_ok) is False
    assert gw.state is LocalReadinessState.READY
    for _ in range(RUNTIME_SAMPLES - 1):
        assert gw.observe_runtime_capacity(_RUNTIME_HIGH_LOAD) is False
    assert gw.observe_runtime_capacity(_RUNTIME_HIGH_LOAD) is True
    assert gw.state is LocalReadinessState.NOT_READY


def test_runtime_capacity_metric_unavailable_enters_unavailable_immediately() -> None:
    gw, _, _ = _gateway()
    _warm_to_ready(gw)
    assert gw.observe_runtime_capacity(None) is True
    assert gw.state is LocalReadinessState.UNAVAILABLE


def test_mark_cancellation_failed_enters_unavailable() -> None:
    gw, _, _ = _gateway()
    _warm_to_ready(gw)
    gw.mark_cancellation_failed()
    assert gw.state is LocalReadinessState.UNAVAILABLE


# ------------------------------------------------------------------ recovery (147b sec 3.2)
def test_recovery_requires_exactly_ten_consecutive_samples() -> None:
    gw, _, _ = _gateway()
    gw.begin_recovery()
    for _ in range(RECOVERY_SAMPLES - 1):
        assert gw.observe_recovery_sample(_RECOVERY_OK) is False
    assert gw.observe_recovery_sample(_RECOVERY_OK) is True


def test_recovery_streak_resets_on_a_violating_sample() -> None:
    gw, _, _ = _gateway()
    gw.begin_recovery()
    for _ in range(RECOVERY_SAMPLES - 1):
        assert gw.observe_recovery_sample(_RECOVERY_OK) is False
    assert gw.observe_recovery_sample(_RECOVERY_NOT_ENOUGH) is False  # resets progress
    for _ in range(RECOVERY_SAMPLES - 1):
        assert gw.observe_recovery_sample(_RECOVERY_OK) is False
    assert gw.observe_recovery_sample(_RECOVERY_OK) is True  # needs a fresh run of 10


def test_recovery_alone_does_not_reenter_ready() -> None:
    gw, _, _ = _gateway()
    gw.begin_recovery()
    for _ in range(RECOVERY_SAMPLES):
        gw.observe_recovery_sample(_RECOVERY_OK)
    assert gw.state is LocalReadinessState.COLD  # begin_warming/complete_warm_up still required


def test_recovery_metric_unavailable_counts_as_a_violation() -> None:
    gw, _, _ = _gateway()
    gw.begin_recovery()
    assert gw.observe_recovery_sample(None) is False
