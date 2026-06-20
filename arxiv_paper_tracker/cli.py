"""Command line interface for arxiv-paper-tracker."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from arxiv_paper_tracker.config import load_config
from arxiv_paper_tracker.notifier import maybe_send_email
from arxiv_paper_tracker.render import render_markdown_digest
from arxiv_paper_tracker.search import collect_papers
from arxiv_paper_tracker.state import filter_new_papers, load_seen_ids, save_seen_ids


def main() -> None:
    parser = argparse.ArgumentParser(description="Track new arXiv papers and generate a digest.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Search arXiv and render a digest")
    scan_parser.add_argument("--config", required=True, help="Path to YAML/JSON config file")
    scan_parser.add_argument("--state", help="Override state file path")
    scan_parser.add_argument("--output", help="Write digest to this Markdown file")
    scan_parser.add_argument("--include-seen", action="store_true", help="Include papers already recorded in state")
    scan_parser.add_argument("--dry-run", action="store_true", help="Do not update state or send email")

    init_parser = subparsers.add_parser("init-config", help="Copy config.example.yaml to a target path")
    init_parser.add_argument("path", nargs="?", default="config.yaml")

    arguments = parser.parse_args()
    if arguments.command == "init-config":
        _init_config(arguments.path)
        return
    if arguments.command == "scan":
        _scan(arguments)
        return
    raise ValueError(f"unknown command: {arguments.command}")


def _init_config(target_path: str) -> None:
    source_path = Path(__file__).resolve().parent.parent / "config.example.yaml"
    destination_path = Path(target_path)
    if destination_path.exists():
        raise FileExistsError(f"refusing to overwrite existing file: {destination_path}")
    shutil.copyfile(source_path, destination_path)
    print(f"created {destination_path}")


def _scan(arguments: argparse.Namespace) -> None:
    config = load_config(arguments.config)
    state_path = Path(arguments.state or config.state.path)

    papers = collect_papers(config)
    seen_ids = load_seen_ids(state_path)
    digest_papers = papers if arguments.include_seen else filter_new_papers(papers, seen_ids)
    markdown_text = render_markdown_digest(
        digest_papers,
        max_abstract_chars=config.output.max_abstract_chars,
    )

    if arguments.output:
        output_path = Path(arguments.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown_text, encoding="utf-8")
    print(markdown_text, end="")

    if not arguments.dry_run:
        save_seen_ids(state_path, seen_ids, papers)
        maybe_send_email(markdown_text, config.email)


if __name__ == "__main__":
    main()
