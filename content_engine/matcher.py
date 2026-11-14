#!/usr/bin/env python3
"""Match a singer profile to verified, currently open Opera Lirico opportunities.

This module deliberately does not store profiles or send email. It is a pure
matching layer that can be tested before a consented profile store is enabled.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

INTEREST_TYPES = {
    "competitions": {"vocal_competition"},
    "opera_house_auditions": {"choir", "audition", "opera_audition"},
    "young_artist_programs": {"young_artist", "academy"},
    "masterclasses": {"masterclass"},
}
VALID_VOICES = {
    "soprano", "mezzo_soprano", "contralto", "countertenor",
    "tenor", "baritone", "bass",
}


def _as_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except (TypeError, ValueError):
        return None


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    voice = str(profile.get("voice_type", "")).strip().lower()
    if voice not in VALID_VOICES:
        raise ValueError("voice_type must be one of the supported voice categories")
    age = profile.get("age")
    if isinstance(age, bool) or not isinstance(age, int) or not 16 <= age <= 100:
        raise ValueError("age must be an integer between 16 and 100")
    interests = profile.get("interests", [])
    if not isinstance(interests, list) or not interests:
        raise ValueError("interests must be a non-empty list")
    unknown = set(interests) - set(INTEREST_TYPES)
    if unknown:
        raise ValueError("unsupported interests: " + ", ".join(sorted(unknown)))
    return {"voice_type": voice, "age": age, "interests": set(interests)}


def match_opportunities(
    profile: dict[str, Any],
    records: list[dict[str, Any]],
    today: date | None = None,
) -> list[dict[str, Any]]:
    """Return eligible, verified opportunities with transparent match notes."""
    user = validate_profile(profile)
    today = today or date.today()
    accepted_types = set().union(*(INTEREST_TYPES[x] for x in user["interests"]))
    matches: list[dict[str, Any]] = []

    for item in records:
        if not (
            item.get("publisher_status") == "official"
            and item.get("review_status") == "verified"
            and item.get("publication_status") == "published"
        ):
            continue
        if item.get("opportunity_type") not in accepted_types:
            continue

        deadline = _as_date(item.get("application_deadline_at"))
        if deadline is None or deadline < today:
            continue

        voices = {str(v).lower() for v in item.get("voice_types", [])}
        voice_status = "match" if user["voice_type"] in voices else (
            "unspecified" if "unspecified" in voices or "all_voices" in voices else "no_match"
        )
        if voice_status == "no_match":
            continue

        age_min, age_max = item.get("age_min"), item.get("age_max")
        age_known = age_min is not None or age_max is not None
        if age_min is not None and user["age"] < int(age_min):
            continue
        if age_max is not None and user["age"] > int(age_max):
            continue

        notes = []
        notes.append("声部符合" if voice_status == "match" else "官方未明确列出声部，建议申请前确认")
        notes.append(
            "年龄符合已公布限制" if age_known
            else "官方记录未提供明确年龄上下限，需查看章程确认"
        )
        matches.append({
            "id": item["id"],
            "title": item["title"],
            "opportunity_type": item["opportunity_type"],
            "deadline": item["application_deadline_at"],
            "location": item.get("location", ""),
            "source_name": item.get("source_name", ""),
            "official_url": item.get("application_url") or item.get("source_url", ""),
            "voice_match": voice_status,
            "age_eligibility": "within_published_limits" if age_known else "not_specified",
            "match_notes": notes,
        })

    return sorted(matches, key=lambda row: (row["deadline"], row["title"].casefold()))


def load_and_match(profile: dict[str, Any], opportunity_data: dict[str, Any], masterclass_data: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    records = list(opportunity_data.get("items", []))
    if masterclass_data:
        records.extend(masterclass_data.get("items", []))
    return match_opportunities(profile, records)


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Match a profile JSON file to current official opportunities.")
    parser.add_argument("profile", help="JSON file with voice_type, age and interests")
    parser.add_argument("--opportunities", default="data/opportunities.json")
    parser.add_argument("--masterclasses", default="data/masterclasses.json")
    args = parser.parse_args()
    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    opportunities = json.loads(Path(args.opportunities).read_text(encoding="utf-8"))
    masterclasses = json.loads(Path(args.masterclasses).read_text(encoding="utf-8"))
    print(json.dumps(load_and_match(profile, opportunities, masterclasses), ensure_ascii=False, indent=2))
