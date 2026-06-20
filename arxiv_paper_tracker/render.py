"""Markdown digest rendering."""

from __future__ import annotations

from datetime import datetime, timezone

from arxiv_paper_tracker.search import Paper


def render_markdown_digest(papers: list[Paper], *, title: str = "arXiv Paper Digest", max_abstract_chars: int = 900) -> str:
    """Render papers as a compact Markdown digest."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# {title}", "", f"Generated at: {generated_at}", "", f"New papers: {len(papers)}", ""]

    if not papers:
        lines.append("No new papers matched the configured queries.")
        return "\n".join(lines).rstrip() + "\n"

    for index, paper in enumerate(papers, 1):
        published = paper.published.strftime("%Y-%m-%d")
        abstract = _truncate(paper.summary, max_abstract_chars)
        lines.extend([
            f"## {index}. {paper.title}",
            "",
            f"- arXiv: [{paper.arxiv_id}]({paper.url})",
            f"- Published: {published}",
            f"- Authors: {', '.join(paper.authors) if paper.authors else 'Unknown'}",
            f"- Categories: {', '.join(paper.categories)}",
            f"- Matched by: {', '.join(paper.matched_by)}",
            "",
            abstract,
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def _truncate(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"
