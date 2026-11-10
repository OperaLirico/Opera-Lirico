"""Shared, fail-closed robots policy for every production collector.

HTTP 404 for robots.txt means no published rules. Other unavailable or
ambiguous robots responses block the fetch. Cross-host redirects are stopped
until the destination host's robots.txt has been checked.
"""
from __future__ import annotations

import re
import time
import urllib.error
import urllib.parse
import urllib.request
from functools import lru_cache

USER_AGENT = "ItaliaAudizioniResearchBot/1.0 (+https://github.com/wl19971007-lgtm/leo)"
REDIRECT_CODES = {301, 302, 303, 307, 308}
MAX_ROBOTS_BYTES = 512 * 1024


class SameHostRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old_host = urllib.parse.urlsplit(req.full_url).netloc.lower()
        new_host = urllib.parse.urlsplit(newurl).netloc.lower()
        if old_host != new_host:
            raise urllib.error.HTTPError(
                req.full_url, code, "Cross-host redirect requires a robots check", headers, fp
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(SameHostRedirectHandler())


def _origin(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    return f"{parts.scheme.lower()}://{parts.netloc.lower()}"


def robots_allows(url: str, robots_text: str, user_agent: str = USER_AGENT) -> bool:
    parsed = urllib.parse.urlsplit(url)
    target = parsed.path or "/"
    if parsed.query:
        target += "?" + parsed.query
    token = user_agent.split("/", 1)[0].lower()

    groups = []
    agents = []
    rules = []
    saw_rule = False
    for raw in robots_text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        key = key.lower()
        if key == "user-agent":
            if saw_rule:
                groups.append((agents, rules))
                agents, rules, saw_rule = [], [], False
            agents.append(value.lower())
        elif key in ("allow", "disallow"):
            saw_rule = True
            if value:
                rules.append((key, value))
    if agents:
        groups.append((agents, rules))

    applicable = []
    for group_agents, group_rules in groups:
        if "*" in group_agents or token in group_agents:
            applicable.extend(group_rules)

    matches = []
    for kind, rule in applicable:
        anchored = rule.endswith("$")
        pattern = rule[:-1] if anchored else rule
        regex = "^" + re.escape(pattern).replace(r"\*", ".*")
        if anchored:
            regex += "$"
        if re.search(regex, target):
            matches.append((len(pattern.replace("*", "")), kind))
    if not matches:
        return True
    longest = max(length for length, _ in matches)
    return any(kind == "allow" for length, kind in matches if length == longest)


@lru_cache(maxsize=256)
def fetch_robots(origin: str) -> dict:
    robots_url = origin.rstrip("/") + "/robots.txt"
    request = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT})
    try:
        with _OPENER.open(request, timeout=12) as response:
            body = response.read(MAX_ROBOTS_BYTES + 1)
            if len(body) > MAX_ROBOTS_BYTES:
                return {"status": "unavailable", "http_status": response.status,
                        "robots_url": robots_url, "reason": "robots_file_too_large"}
            return {"status": "ok", "http_status": response.status,
                    "robots_url": response.geturl(),
                    "text": body.decode("utf-8", "replace")}
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"status": "not_found", "http_status": 404,
                    "robots_url": robots_url, "text": ""}
        if exc.code in REDIRECT_CODES and exc.headers.get("Location"):
            return {"status": "redirect_requires_review", "http_status": exc.code,
                    "robots_url": robots_url,
                    "redirect_url": urllib.parse.urljoin(exc.geturl(), exc.headers["Location"])}
        return {"status": "unavailable", "http_status": exc.code,
                "robots_url": robots_url, "reason": str(exc)[:240]}
    except Exception as exc:
        return {"status": "unavailable", "http_status": None,
                "robots_url": robots_url,
                "reason": f"{type(exc).__name__}: {str(exc)[:240]}"}


def check_url(url: str, user_agent: str = USER_AGENT) -> dict:
    policy = fetch_robots(_origin(url))
    if policy["status"] == "not_found":
        return {"allowed": True, "status": "allowed_no_robots_file",
                "robots_status": "not_found", "robots_http_status": 404,
                "robots_url": policy["robots_url"]}
    if policy["status"] != "ok":
        return {"allowed": False, "status": "robots_policy_unavailable",
                "robots_status": policy["status"],
                "robots_http_status": policy.get("http_status"),
                "robots_url": policy.get("robots_url"),
                "reason": policy.get("reason") or policy.get("redirect_url")}
    allowed = robots_allows(url, policy["text"], user_agent)
    return {"allowed": allowed,
            "status": "allowed" if allowed else "robots_disallowed",
            "robots_status": "ok", "robots_http_status": policy["http_status"],
            "robots_url": policy["robots_url"]}


def fetch_page_with_robots(url: str, fetcher, timeout: float = 30,
                           retries: int = 0, max_redirects: int = 5,
                           delay: float = 1.2):
    """Fetch with Scrapling while checking robots before every redirect hop.

    The caller supplies Fetcher.get (or a compatible retry wrapper). Redirects
    are disabled in the underlying request and followed manually only after the
    next host/path has passed robots checks.
    """
    current = url
    chain = []
    for _ in range(max_redirects + 1):
        decision = check_url(current)
        if not decision["allowed"]:
            return None, {**decision, "redirect_chain": chain, "final_url": current}
        if delay:
            time.sleep(delay)
        response = fetcher(
            current, timeout=timeout, retries=retries,
            follow_redirects=False, stealthy_headers=False,
        )
        status = int(getattr(response, "status", 0) or 0)
        if status in REDIRECT_CODES:
            headers = getattr(response, "headers", {}) or {}
            location = headers.get("Location") or headers.get("location")
            if not location:
                return response, {**decision, "status": "redirect_without_location",
                                  "redirect_chain": chain, "final_url": current}
            target = urllib.parse.urljoin(current, location)
            chain.append({"from": current, "to": target, "status": status})
            current = target
            continue
        return response, {**decision,
                          "status": "fetched" if status < 400 else "http_error",
                          "http_status": status, "redirect_chain": chain,
                          "final_url": current}
    return None, {"allowed": False, "status": "redirect_limit",
                  "redirect_chain": chain, "final_url": current}


def fetch_bytes_with_robots(url: str, max_bytes: int, timeout: float = 25,
                            user_agent: str = USER_AGENT, delay: float = 1.2) -> dict:
    """Fetch a public file with robots checks and no automatic cross-host redirects."""
    current = url
    chain = []
    for _ in range(6):
        decision = check_url(current, user_agent=user_agent)
        if not decision["allowed"]:
            return {"status": decision["status"], "http_status": decision.get("robots_http_status"),
                    "body": b"", "final_url": current, "access_policy": decision,
                    "redirect_chain": chain}
        if delay:
            time.sleep(delay)
        request = urllib.request.Request(current, headers={"User-Agent": user_agent})
        try:
            with _OPENER.open(request, timeout=timeout) as response:
                body = response.read(max_bytes + 1)
                truncated = len(body) > max_bytes
                return {"status": "too_large" if truncated else "ok",
                        "http_status": response.status, "body": body[:max_bytes],
                        "final_url": response.geturl(), "content_type": response.headers.get("Content-Type"),
                        "truncated": truncated, "access_policy": decision,
                        "redirect_chain": chain}
        except urllib.error.HTTPError as exc:
            location = exc.headers.get("Location") if exc.headers else None
            if exc.code in REDIRECT_CODES and location:
                target = urllib.parse.urljoin(exc.geturl(), location)
                chain.append({"from": current, "to": target, "status": exc.code})
                current = target
                continue
            return {"status": "restricted" if exc.code in (403, 429) else "http_error",
                    "http_status": exc.code, "body": b"", "final_url": current,
                    "error": str(exc)[:240], "access_policy": decision,
                    "redirect_chain": chain}
        except Exception as exc:
            return {"status": "error", "http_status": None, "body": b"",
                    "final_url": current,
                    "error": f"{type(exc).__name__}: {str(exc)[:240]}",
                    "access_policy": decision, "redirect_chain": chain}
    return {"status": "redirect_limit", "http_status": None, "body": b"",
            "final_url": current, "redirect_chain": chain}
