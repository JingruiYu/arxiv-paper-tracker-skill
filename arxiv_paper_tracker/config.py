"""Configuration loading and validation for arxiv-paper-tracker."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - exercised only when PyYAML is absent.
    yaml = None


@dataclass
class QueryConfig:
    authors: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    institutions: list[str] = field(default_factory=list)


@dataclass
class LimitConfig:
    max_results_per_query: int = 20
    days_back: int = 7


@dataclass
class FilterConfig:
    include_keywords: list[str] = field(default_factory=list)
    exclude_keywords: list[str] = field(default_factory=list)


@dataclass
class OutputConfig:
    format: str = "markdown"
    max_abstract_chars: int = 900


@dataclass
class StateConfig:
    path: str = ".arxiv_tracker_state.json"


@dataclass
class EmailConfig:
    enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 465
    use_ssl: bool = True
    username: str = ""
    password: str = ""
    sender: str = ""
    receivers: list[str] = field(default_factory=list)
    subject: str = "arXiv paper digest"


@dataclass
class TrackerConfig:
    queries: QueryConfig = field(default_factory=QueryConfig)
    limits: LimitConfig = field(default_factory=LimitConfig)
    filters: FilterConfig = field(default_factory=FilterConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    state: StateConfig = field(default_factory=StateConfig)
    email: EmailConfig = field(default_factory=EmailConfig)


def load_config(config_path: str | Path) -> TrackerConfig:
    """Load YAML or JSON configuration from disk."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")

    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required to read YAML config files")
        raw_config = yaml.safe_load(text) or {}
    else:
        raw_config = json.loads(text)

    return parse_config(raw_config)


def parse_config(raw_config: dict[str, Any]) -> TrackerConfig:
    """Convert a raw dict into a typed TrackerConfig with defaults."""
    queries = raw_config.get("queries", {}) or {}
    limits = raw_config.get("limits", {}) or {}
    filters = raw_config.get("filters", {}) or {}
    output = raw_config.get("output", {}) or {}
    state = raw_config.get("state", {}) or {}
    email = raw_config.get("email", {}) or {}

    return TrackerConfig(
        queries=QueryConfig(
            authors=_string_list(queries.get("authors", [])),
            categories=_string_list(queries.get("categories", [])),
            keywords=_string_list(queries.get("keywords", [])),
            institutions=_string_list(queries.get("institutions", [])),
        ),
        limits=LimitConfig(
            max_results_per_query=int(limits.get("max_results_per_query", 20)),
            days_back=int(limits.get("days_back", 7)),
        ),
        filters=FilterConfig(
            include_keywords=_string_list(filters.get("include_keywords", [])),
            exclude_keywords=_string_list(filters.get("exclude_keywords", [])),
        ),
        output=OutputConfig(
            format=str(output.get("format", "markdown")),
            max_abstract_chars=int(output.get("max_abstract_chars", 900)),
        ),
        state=StateConfig(path=str(state.get("path", ".arxiv_tracker_state.json"))),
        email=EmailConfig(
            enabled=bool(email.get("enabled", False)),
            smtp_host=str(email.get("smtp_host", "")),
            smtp_port=int(email.get("smtp_port", 465)),
            use_ssl=bool(email.get("use_ssl", True)),
            username=str(email.get("username", "")),
            password=str(email.get("password", "")),
            sender=str(email.get("sender", "")),
            receivers=_string_list(email.get("receivers", [])),
            subject=str(email.get("subject", "arXiv paper digest")),
        ),
    )


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value if str(item).strip()]
