from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TrackQuery:
    artist: str | None
    title: str | None
    album: str | None
    artwork_width: int
    artwork_height: int
    original_title: str | None = None  # raw title before remix/edit stripping


@dataclass(slots=True)
class ResolvedCover:
    provider: str
    artwork_url: str | None
    content_type: str
    image: bytes
