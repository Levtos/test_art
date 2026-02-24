from __future__ import annotations

import logging
from dataclasses import replace
from typing import Iterable

from .const import PROVIDER_ITUNES, PROVIDER_MUSICBRAINZ
from .itunes import async_itunes_resolve
from .models import ResolvedCover, TrackQuery
from .musicbrainz import async_musicbrainz_resolve

_LOGGER = logging.getLogger(__name__)


async def _try_providers(
    *,
    session,
    query: TrackQuery,
    provider_list: list[str],
) -> ResolvedCover | None:
    """Try each provider once with the given query. Returns first match or None."""
    for provider in provider_list:
        try:
            if provider == PROVIDER_ITUNES:
                resolved = await async_itunes_resolve(session=session, query=query)
                if resolved:
                    return resolved
                continue

            if provider == PROVIDER_MUSICBRAINZ:
                resolved = await async_musicbrainz_resolve(session=session, query=query)
                if resolved:
                    return resolved
                continue

            _LOGGER.debug("Unknown provider '%s' (skipping)", provider)

        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Provider '%s' failed (title=%r): %s", provider, query.title, err)

    return None


async def async_resolve_cover(*, session, query: TrackQuery, providers: Iterable[str]) -> ResolvedCover | None:
    """Resolve cover art with a staged title fallback strategy.

    Stage 1 – original title (e.g. "Song (Remix)"): lets providers find a
              remix-specific cover if one exists.
    Stage 2 – cleaned title (e.g. "Song"): strips remix/edit annotations and
              retries so the original release cover is used as a fallback.

    Returns the first successful result or None (callers should show the
    default fallback logo in that case).
    """
    provider_list = [p for p in providers if isinstance(p, str)]
    if not provider_list:
        provider_list = [PROVIDER_ITUNES]

    # Build the ordered list of title variants to try.
    # original_title is set only when it differs from the cleaned title.
    if query.original_title and query.original_title != query.title:
        title_stages: list[str | None] = [query.original_title, query.title]
    else:
        title_stages = [query.title]

    for stage_title in title_stages:
        stage_query = replace(query, title=stage_title, original_title=None) if stage_title != query.title else query
        _LOGGER.debug("Cover search stage title=%r", stage_title)
        resolved = await _try_providers(session=session, query=stage_query, provider_list=provider_list)
        if resolved:
            return resolved

    _LOGGER.debug("All stages exhausted – no cover found for artist=%r title=%r", query.artist, query.title)
    return None
