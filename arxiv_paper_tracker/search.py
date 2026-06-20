"""arXiv search and filtering logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from arxiv_paper_tracker.config import TrackerConfig


@dataclass(frozen=True)
class Paper:
    arxiv_id: str
    title: str
    url: str
    published: datetime
    updated: datetime | None
    authors: list[str]
    categories: list[str]
    summary: str
    matched_by: list[str]


def collect_papers(config: TrackerConfig) -> list[Paper]:
    """Query arXiv according to config and return deduplicated papers."""
    try:
        import arxiv
    except ImportError as error:  # pragma: no cover - depends on runtime environment.
        raise RuntimeError("Please install dependencies first: pip install -e .") from error

    client = arxiv.Client()
    collected: dict[str, Paper] = {}

    for label, query in build_queries(config):
        search = arxiv.Search(
            query=query,
            max_results=config.limits.max_results_per_query,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )
        for result in client.results(search):
            paper = _paper_from_result(result, label)
            if not _is_recent_enough(paper, config.limits.days_back):
                continue
            if not _passes_keyword_filters(paper, config):
                continue
            if paper.arxiv_id in collected:
                previous = collected[paper.arxiv_id]
                collected[paper.arxiv_id] = Paper(
                    arxiv_id=previous.arxiv_id,
                    title=previous.title,
                    url=previous.url,
                    published=previous.published,
                    updated=previous.updated,
                    authors=previous.authors,
                    categories=previous.categories,
                    summary=previous.summary,
                    matched_by=sorted(set(previous.matched_by + paper.matched_by)),
                )
            else:
                collected[paper.arxiv_id] = paper

    return sorted(collected.values(), key=lambda paper: paper.published, reverse=True)


def build_queries(config: TrackerConfig) -> list[tuple[str, str]]:
    """Build labeled arXiv query strings from config."""
    queries: list[tuple[str, str]] = []
    for author in config.queries.authors:
        queries.append((f"author:{author}", f'au:"{author}"'))
    for category in config.queries.categories:
        queries.append((f"category:{category}", f"cat:{category}"))
    for keyword in config.queries.keywords:
        queries.append((f"keyword:{keyword}", f'all:"{keyword}"'))
    for institution in config.queries.institutions:
        queries.append((f"institution:{institution}", f'all:"{institution}"'))
    return queries


def _paper_from_result(result: object, matched_by: str) -> Paper:
    entry_id = str(getattr(result, "entry_id"))
    arxiv_id = entry_id.rstrip("/").split("/")[-1]
    authors = [str(author) for author in getattr(result, "authors", [])]
    return Paper(
        arxiv_id=arxiv_id,
        title=str(getattr(result, "title", "")).strip(),
        url=entry_id,
        published=getattr(result, "published"),
        updated=getattr(result, "updated", None),
        authors=authors,
        categories=list(getattr(result, "categories", [])),
        summary=str(getattr(result, "summary", "")).strip().replace("\n", " "),
        matched_by=[matched_by],
    )


def _is_recent_enough(paper: Paper, days_back: int) -> bool:
    threshold = datetime.now(timezone.utc) - timedelta(days=days_back)
    published = paper.published
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    return published >= threshold


def _passes_keyword_filters(paper: Paper, config: TrackerConfig) -> bool:
    searchable_text = " ".join([paper.title, paper.summary, " ".join(paper.categories)]).lower()
    include_keywords = [keyword.lower() for keyword in config.filters.include_keywords]
    exclude_keywords = [keyword.lower() for keyword in config.filters.exclude_keywords]

    if include_keywords and not any(keyword in searchable_text for keyword in include_keywords):
        return False
    if exclude_keywords and any(keyword in searchable_text for keyword in exclude_keywords):
        return False
    return True
