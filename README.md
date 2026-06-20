# arxiv-paper-tracker

<p align="center">
  <img src="https://img.shields.io/badge/language-Python-blue" />
  <img src="https://img.shields.io/badge/source-arXiv-b31b1b" />
  <img src="https://img.shields.io/badge/output-Markdown-green" />
  <img src="https://img.shields.io/badge/license-Apache--2.0-lightgrey" />
</p>

A small, configurable arXiv paper tracker. It searches arXiv by authors,
categories, keywords and institution terms, deduplicates results by arXiv ID,
keeps a local seen-state file, and renders a Markdown digest.

It is designed for personal research workflows and can be called manually, from
cron, GitHub Actions, or any other automation system.

## Features

- Track papers by author, category, keyword and institution term.
- Limit results to recent papers via `days_back`.
- Deduplicate papers from multiple matching queries.
- Persist a local seen-state file to avoid repeated notifications.
- Render clean Markdown digests.
- Optional email notification configured by a local config file.
- Agent-friendly `SKILL.md` included for tools that support skill files.

## Installation

```bash
git clone https://github.com/JingruiYu/arxiv-paper-tracker-skill.git
cd arxiv-paper-tracker-skill
python -m pip install -e .
```

## Quick start

Create a local config file:

```bash
arxiv-paper-tracker init-config config.yaml
```

Edit `config.yaml`, then run:

```bash
arxiv-paper-tracker scan \
  --config config.yaml \
  --state outputs/arxiv_tracker/state.json \
  --output outputs/arxiv_tracker/latest.md
```

The digest is printed to stdout and, when `--output` is provided, also written to
a Markdown file.

## Configuration

Public example configuration is provided in:

- `config.example.yaml`

Local user configs such as `config.yaml` and `*.local.yaml` are ignored by git.
Do not commit SMTP passwords or other personal credentials.

Minimal example:

```yaml
queries:
  authors:
    - Pollefeys
  categories:
    - cs.CV
    - cs.RO
  keywords:
    - SLAM
    - 3D reconstruction
  institutions:
    - NVIDIA

limits:
  max_results_per_query: 20
  days_back: 7

state:
  path: outputs/arxiv_tracker/state.json

email:
  enabled: false
```

## Optional email notification

Email is disabled by default. To enable it, edit your local config file:

```yaml
email:
  enabled: true
  smtp_host: smtp.example.com
  smtp_port: 465
  use_ssl: true
  username: your_email@example.com
  password: your_smtp_app_password
  sender: your_email@example.com
  receivers:
    - receiver@example.com
  subject: "arXiv paper digest"
```

The project intentionally reads email credentials only from the local config
file. Keep that config file private.

## Automation

The tracker is intentionally CLI-first. You can run it from cron, GitHub Actions,
or any other scheduler. A minimal cron-style command looks like:

```bash
python -m arxiv_paper_tracker.cli scan \
  --config config.yaml \
  --state outputs/arxiv_tracker/state.json \
  --output outputs/arxiv_tracker/latest.md
```

The generated Markdown file can then be sent by your own notification pipeline,
email setup, chat bot, or agent runtime.

## Development checks

```bash
python -m py_compile arxiv_paper_tracker/*.py
python -m unittest discover -s tests
```

## License

Apache License 2.0. See [LICENSE](LICENSE).
