from __future__ import annotations

from pathlib import Path

from benchmarks.corpus import FIXTURES_DIR, load_benchmark_corpus


PROTECTED_TERMS = ("Loki", "Tom Hiddleston", "Marvel")


def _manifest_strings(item) -> list[str]:
    values: list[str] = []
    for field_name in (
        "id",
        "modality",
        "text",
        "tone",
        "voice_id",
        "transcript",
        "expected_failure",
        "safety_notes",
    ):
        value = getattr(item, field_name, None)
        if value is not None:
            values.append(str(value))

    fixture_path = getattr(item, "fixture_path", None)
    if fixture_path is not None:
        values.append(str(fixture_path))

    condition_tags = getattr(item, "condition_tags", None)
    if condition_tags:
        values.extend(str(tag) for tag in condition_tags)

    return values


def test_load_benchmark_corpus_pins_tone_coverage_fixture_metadata_and_safety() -> None:
    corpus = load_benchmark_corpus()

    assert len(corpus.items) >= 6
    assert len({item.id for item in corpus.items}) == len(corpus.items)

    text_items = [item for item in corpus.items if item.modality == "text"]
    audio_items = [item for item in corpus.items if item.modality == "audio"]

    assert text_items
    assert audio_items

    assert {item.tone for item in text_items} >= {"measured", "cutting", "grandiose"}

    for item in corpus.items:
        assert item.voice_id == "vesper-glass"
        assert item.safety_notes

    for item in text_items:
        assert item.text
        assert item.fixture_path is None
        assert item.transcript is None
        assert item.speech_window_start_ms is None
        assert item.speech_window_end_ms is None
        assert item.duration_ms is None

    for item in audio_items:
        assert item.transcript
        assert item.speech_window_start_ms is not None
        assert item.speech_window_end_ms is not None
        assert item.speech_window_start_ms < item.speech_window_end_ms
        assert item.duration_ms is not None
        assert item.duration_ms > 0
        assert item.condition_tags
        assert item.fixture_path is not None
        assert isinstance(item.fixture_path, Path)
        assert item.fixture_path.is_relative_to(FIXTURES_DIR)
        assert item.fixture_path.exists()

    manifest_text = " ".join(
        value
        for item in corpus.items
        for value in _manifest_strings(item)
    ).lower()

    for term in PROTECTED_TERMS:
        assert term.lower() not in manifest_text
