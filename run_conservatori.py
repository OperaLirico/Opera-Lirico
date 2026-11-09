#!/usr/bin/env python3
"""Run the conservatory collector, retrying the fetch and keeping the last good copy.

Two problems show up in practice:

* Conservatory sites time out or stall mid-handshake. One run loses Turin, the
  next loses Genoa, and a stalled connection can hold the whole job open.
* A failed run must not delete what a previous run already read.

So: retry once at the fetcher boundary behind a hard per-request deadline,
and after the collector writes its file, replace any failed record with the
most recent successful snapshot of that institution (marked ``cached`` with
its own ``checked_at``) when one exists in the repository. A site that never
succeeds stays marked unreachable.
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path

import scrape_conservatori as core

ATTEMPTS = 2
TIMEOUT = 25
HARD_DEADLINE = 40  # seconds; covers a stalled handshake that curl's timeout misses
DATA = Path(__file__).resolve().parent / "data" / "conservatori.json"
POOL = ThreadPoolExecutor(max_workers=1)


def _attempt(url: str):
    return POOL.submit(core.Fetcher.get, url, timeout=TIMEOUT, retries=0)


class RetryingFetcher:
    @staticmethod
    def get(url: str, **_kwargs):
        last_error: Exception | None = None
        for attempt in range(1, ATTEMPTS + 1):
            try:
                return _attempt(url).result(timeout=HARD_DEADLINE)
            except FutureTimeout:
                raise TimeoutError(f"no response within {HARD_DEADLINE}s: {url}")
            except Exception as exc:  # curl timeouts, TLS resets, empty replies
                last_error = exc
                if attempt < ATTEMPTS:
                    time.sleep(3 * attempt)
        raise last_error if last_error else RuntimeError("fetch failed")


def snapshots() -> dict[int, dict]:
    """Successful records already in the repository, keyed by institution number."""
    if not DATA.exists():
        return {}
    try:
        payload = json.loads(DATA.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    keep: dict[int, dict] = {}
    for item in payload.get("items", []):
        if item.get("status") == "ok":
            keep[item.get("number")] = item
    return keep


def backfill(previous: dict[int, dict]) -> None:
    if not previous or not DATA.exists():
        return
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    replaced = 0
    for item in payload.get("items", []):
        if item.get("status") == "ok":
            continue
        old = previous.get(item.get("number"))
        if not old:
            continue
        for field in ("deadline_lines", "exam_dates", "requirements", "documents", "title"):
            if old.get(field):
                item[field] = old[field]
        item["status"] = "ok"
        item["cached"] = True
        item["checked_at"] = old.get("checked_at")
        item["note"] = "本次未连通，显示上一次成功读取的内容"
        replaced += 1
    if replaced:
        DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Kept the previous snapshot for {replaced} institution(s)")


if __name__ == "__main__":
    previous = snapshots()
    core.Fetcher = RetryingFetcher
    core.main()
    backfill(previous)
