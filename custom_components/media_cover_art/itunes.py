from __future__ import annotations

import re
from typing import Any

from homeassistant.exceptions import HomeAssistantError

from .models import ResolvedCover, TrackQuery

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"

# Some Apple endpoints return non-standard content-type headers; allow json parsing anyway.
_JSON_KW = {"content_type": None}

_RE_ARTWORK_SIZE = re.compile(r"/(\d{2,4})x(\d{2,4})bb\.(jpg|png)$", re.IGNORECASE)


def _clean(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    # remove "(feat...)" / "[feat...]" fragments (helps radio metadata)
    s = re.sub(r"\((feat\.|featuring).*?\)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\[(feat\.|featuring).*?\]", "", s, flags=re.IGNORECASE)
    return s.strip()


def _score_result(query: TrackQuery, item: dict[str, Any]) -> int:
    q_artist = _clean(query.artist or "")
    q_title = _clean(query.title or "")
    q_album = _clean(query.album or "")

    r_artist = _clean(str(item.get("artistName", "")))
    r_title = _clean(str(item.get("trackName", "")))
    r_album = _clean(str(item.get("collectionName", "")))

    score = 0

    if q_title and r_title:
        if q_title == r_title:
            score += 10
        elif q_title in r_title or r_title in q_title:
            score += 6

    if q_artist and r_artist:
        if q_artist == r_artist:
            score += 8
        elif q_artist in r_artist or r_artist in q_artist:
            score += 4

    if q_album and r_album:
        if q_album == r_album:
            score += 3
        elif q_album in r_album or r_album in q_album:
            score += 1

    # Prefer "song" items
    if str(item.get("wrapperType", "")).lower() == "track":
        score += 1

    return score


def _upscale_artwork(url: str, size: int) -> str:
    # Many Apple artwork URLs end with ".../100x100bb.jpg". We swap to requested size.
    m = _RE_ARTWORK_SIZE.search(url)
    if not m:
        return url
    ext = m.group(3)
    return _RE_ARTWORK_SIZE.sub(f"/{size}x{size}bb.{ext}", url)


async def async_itunes_resolve(*, session, query: TrackQuery) -> ResolvedCover | None:
    if not (query.artist or query.title):
        return None

    term = " ".join([p for p in [query.artist, query.title] if p])
    params = {
        "term": term,
        "entity": "song",
        "media": "music",
        "limit": "10",
        # Country is optional; leaving it out increases global matches.
        # "country": "DE",
    }

    try:
        async with session.get(ITUNES_SEARCH_URL, params=params, timeout=10) as resp:
            resp.raise_for_status()
            payload = await resp.json(**_JSON_KW)
    except Exception as err:
        raise HomeAssistantError(f"iTunes search failed: {err}") from err

    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list) or not results:
        return None

    # Pick best scored match
    best: dict[str, Any] | None = None
    best_score = -1

    for item in results:
        if not isinstance(item, dict):
            continue
        score = _score_result(query, item)
        if score > best_score:
            best_score = score
            best = item

    if not best or best_score <= 0:
        return None

    artwork = best.get("artworkUrl100") or best.get("artworkUrl60") or best.get("artworkUrl30")
    if not isinstance(artwork, str) or not artwork:
        return None

    artwork_url = _upscale_artwork(artwork, max(100, int(query.artwork_size)))

    # Fetch the image bytes
    try:
        async with session.get(artwork_url, timeout=10) as img_resp:
            img_resp.raise_for_status()
            content_type = img_resp.headers.get("Content-Type", "image/jpeg")
            image = await img_resp.read()
    except Exception as err:
        raise HomeAssistantError(f"iTunes artwork fetch failed: {err}") from err

    if not image:
        return None

    return ResolvedCover(
        provider="itunes",
        artwork_url=artwork_url,
        content_type=content_type,
        image=image,
    )
