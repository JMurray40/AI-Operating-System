from __future__ import annotations

from jarvis_core.metrics import PerfReport, measure


def test_measure_records_stage():
    r = PerfReport(note_count=5)
    with measure(r, "parse"):
        sum(range(1000))
    assert "parse" in r.durations
    assert r.durations["parse"] >= 0.0


def test_total_falls_back_to_stage_sum():
    r = PerfReport(note_count=2)
    r.record("parse", 0.1)
    r.record("resolve", 0.2)
    assert abs(r.total_seconds - 0.3) < 1e-9
    r.record("total", 0.5)
    assert r.total_seconds == 0.5


def test_to_dict_shape():
    r = PerfReport(note_count=10)
    r.record("parse", 0.01)
    r.record("total", 0.02)
    d = r.to_dict()
    assert d["note_count"] == 10
    assert d["total_ms"] == 20.0
    assert "parse" in d["durations_ms"]
    assert d["notes_per_second"] > 0
