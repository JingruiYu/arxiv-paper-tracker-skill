"""Persistent deduplication state."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from arxiv_paper_tracker.search import Paper


def load_seen_ids(state_path: str | Path) -> set[str]:
    path = Path(state_path)
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return set(data.get("seen_arxiv_ids", []))


def filter_new_papers(papers: list[Paper], seen_ids: set[str]) -> list[Paper]:
    return [paper for paper in papers if paper.arxiv_id not in seen_ids]


def save_seen_ids(state_path: str | Path, seen_ids: set[str], papers: list[Paper]) -> None:
    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    updated_ids = sorted(seen_ids | {paper.arxiv_id for paper in papers})
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "seen_arxiv_ids": updated_ids,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
