"""Live arXiv API smoke test.

This test is intentionally opt-in because it depends on network access and arXiv
availability. Run it manually with:

    ARXIV_TRACKER_RUN_LIVE_TEST=1 python -m unittest tests/test_arxiv_api.py
"""

from __future__ import annotations

import os
import unittest

from arxiv_paper_tracker.config import TrackerConfig, LimitConfig, QueryConfig
from arxiv_paper_tracker.search import collect_papers


@unittest.skipUnless(
    os.environ.get("ARXIV_TRACKER_RUN_LIVE_TEST") == "1",
    "set ARXIV_TRACKER_RUN_LIVE_TEST=1 to run the live arXiv API smoke test",
)
class ArxivApiSmokeTest(unittest.TestCase):
    def test_fetch_recent_robotics_paper(self) -> None:
        config = TrackerConfig(
            queries=QueryConfig(categories=["cs.RO"], keywords=["robot"]),
            limits=LimitConfig(max_results_per_query=3, days_back=3650),
        )
        papers = collect_papers(config)
        self.assertGreater(len(papers), 0)
        self.assertTrue(papers[0].arxiv_id)
        self.assertTrue(papers[0].title)
        self.assertTrue(papers[0].url.startswith("https://arxiv.org/abs/"))


if __name__ == "__main__":
    unittest.main()
