from __future__ import annotations

import logging
from typing import Iterable

from .const import PROVIDER_ITUNES
from .itunes import async_itunes_resolve
from .models import ResolvedCover, TrackQuery

_LOGGER = logging.getLogger(__name__)


async def async_resolve_cover(*, session, query: TrackQuery, providers: Iterable[str]) -> ResolvedCover | None:
    """Try providers in order and return first match."""
    provider_list = [p for p in providers if isinstance(p, str)]
    if not provider_list:
        provider_list = [PROVIDER_ITUNES]

    last_err: Exception | None = None

    for provider in provider_list:
        try:
            if provider == PROVIDER_ITUNES:
                resolved = await async_itunes_resolve(session=session, query=query)
                if resolved:
                    return resolved
                continue

            _LOGGER.debug("Unknown provider '%s' (skipping)", provider)

        except Exception as err:
            last_err = err
            _LOGGER.debug("Provider '%s' failed: %s", provider, err)

    if last_err:
        # Only raise if you want errors to surface; for covers we keep it soft.
        _LOGGER.debug("All providers failed, last error: %s", last_err)

    return None
