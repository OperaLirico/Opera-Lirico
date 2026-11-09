#!/usr/bin/env python3
"""Run the conservatory collector, retrying the fetch and keeping the last good copy.

Two problems show up in practice:

* Conservatory sites time out often. One run loses Turin, the next loses Genoa,
  so a single attempt leaves visible holes in the board.
* A failed run therefore must not delete what a previous run already read.

So: retry at the fetcher boundary, and after the collector writes its file,
replace any failed record with the most recent successful snapshot of that
institution (marked ``cached`` with its own ``checked_at``) when one exists in
the repository. A site that never succeeds stays marked unreachable.
"""

from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path

from scrapling.fetchers import Fetcher as RawFetcher

import scrape_conservatori as core

# Announcements that reach the admission page but are not admission deadlines:
# grants, research doctorates, seminars, staff shortlists, "admitted students" lists.
OTHER_NOTICE = re.compile(
    r"assegnazion|dottorat|seminari|individuazione di|graduator|ammess|borsa di studio|"
    r"masterclass|rassegna|stagione concertistica",
    re.IGNORECASE,
)

ATTEMPTS = 2
TIMEOUT = 25
DATA = Path(__file__).resolve().parent / "data" / "conservatori.json"


HARD_DEADLINE = 40  # seconds; covers a stalled TLS handshake the curl timeout misses
# One worker per in-flight request: the collector already fans out over
# ``core.WORKERS`` threads, and a single-slot pool would serialise them again.
POOL = ThreadPoolExecutor(max_workers=core.WORKERS)


def _attempt(url: str):
    # ``core.Fetcher`` is replaced by RetryingFetcher below; submitting *that* would
    # re-enter this pool and deadlock, so the raw client is captured once here.
    return POOL.submit(RawFetcher.get, url, timeout=TIMEOUT, retries=0)


class RetryingFetcher:
    @staticmethod
    def get(url: str, **_kwargs):
        last_error: Exception | None = None
        for attempt in range(1, ATTEMPTS + 1):
            try:
                # A site can accept the connection and then stall past curl's
                # own timeout; the future deadline keeps the whole run bounded.
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


def drop_other_notices() -> None:
    """Strip scholarship/doctorate/seminar notices that slipped into the timeline fields."""
    if not DATA.exists():
        return
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    removed = 0
    for item in payload.get("items", []):
        for field in ("deadline_lines", "exam_dates", "requirements"):
            kept = [line for line in item.get(field) or [] if not OTHER_NOTICE.search(line)]
            if len(kept) != len(item.get(field) or []):
                removed += len(item.get(field) or []) - len(kept)
                item[field] = kept
    if removed:
        DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Dropped {removed} non-admission notice(s)")


if __name__ == "__main__":
    previous = snapshots()
    core.Fetcher = RetryingFetcher
    core.main()
    backfill(previous)
    drop_other_notices()
