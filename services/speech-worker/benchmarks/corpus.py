from __future__ import annotations

import json
from pathlib import Path

from .schemas import BenchmarkCorpus, BenchmarkCorpusItem

PACKAGE_ROOT = Path(__file__).resolve().parent
CORPUS_ROOT = PACKAGE_ROOT / "corpus"
FIXTURES_DIR = CORPUS_ROOT / "fixtures"
RUNS_DIR = PACKAGE_ROOT / "runs"
REPORTS_DIR = PACKAGE_ROOT / "reports"
MANIFEST_PATH = CORPUS_ROOT / "manifest.json"


def _resolve_manifest_path(manifest_path: str | Path | None) -> Path:
    if manifest_path is None:
        resolved_manifest_path = MANIFEST_PATH
    else:
        resolved_manifest_path = Path(manifest_path)
        if not resolved_manifest_path.is_absolute():
            resolved_manifest_path = (CORPUS_ROOT / resolved_manifest_path).resolve()
    return resolved_manifest_path


def _resolve_fixture_path(fixture_path: str | Path) -> Path:
    candidate_path = Path(fixture_path)
    if candidate_path.is_absolute():
        resolved_path = candidate_path.resolve()
    else:
        resolved_path = (CORPUS_ROOT / candidate_path).resolve()

    fixtures_root = FIXTURES_DIR.resolve()
    if not resolved_path.is_relative_to(fixtures_root):
        raise ValueError(
            "benchmark fixture path must stay inside the corpus fixtures directory",
        )
    if not resolved_path.exists():
        raise FileNotFoundError(f"benchmark fixture file not found: {resolved_path}")
    return resolved_path


def load_benchmark_corpus(manifest_path: str | Path | None = None) -> BenchmarkCorpus:
    resolved_manifest_path = _resolve_manifest_path(manifest_path)
    raw_manifest = json.loads(resolved_manifest_path.read_text())
    raw_items = raw_manifest.get("items")
    if not isinstance(raw_items, list):
        raise ValueError("benchmark corpus manifest must include an items list")

    items: list[BenchmarkCorpusItem] = []
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            raise ValueError("benchmark corpus items must be objects")

        item_data = dict(raw_item)
        if item_data.get("fixture_path") is not None:
            item_data["fixture_path"] = _resolve_fixture_path(item_data["fixture_path"])

        items.append(BenchmarkCorpusItem.model_validate(item_data))

    return BenchmarkCorpus(items=items)
