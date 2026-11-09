#!/usr/bin/env python3
"""Run the conservatory collector with retries around the network call.

Conservatory sites time out often enough that a single attempt leaves holes in
the board — one run loses Turin, the next loses Genoa. ``fetch_page`` builds a
fresh request each time, so retrying at the fetcher boundary is enough, and a
site that still fails is recorded as unreachable instead of aborting the run.
"""

from __future__ import annotations

import time

import scrape_conservatori as core

ATTEMPTS = 3
TIMEOUT = 45


class RetryingFetcher:
    @staticmethod
    def get(url: str, **_kwargs):
        last_error: Exception | None = None
        for attempt in range(1, ATTEMPTS + 1):
            try:
                return core.Fetcher.get(url, timeout=TIMEOUT, retries=0)
            except Exception as exc:  # curl timeouts, TLS resets, empty replies
                last_error = exc
                if attempt < ATTEMPTS:
                    time.sleep(4 * attempt)
        raise last_error if last_error else RuntimeError("fetch failed")


if __name__ == "__main__":
    core.Fetcher = RetryingFetcher
    core.main()
