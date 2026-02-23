# Media Cover Art (Home Assistant Custom Integration)

This integration provides cover artwork as an **Image entity**, based on `media_artist` + `media_title` from a selected `media_player`.

Current providers: **iTunes Search API** + **MusicBrainz/Cover Art Archive** (no login required).

## Features

- Image entity (for example: `image.media_cover_art_homepods_cover`)
- Track change detection: refreshes only when `(artist,title,album)` changes
- Frontend-friendly caching: UI refetches when `image_last_updated` changes
- Integration icon/logo assets (SVG)
- Additional Camera entity for Picture Cards (`camera.*_cover_camera`)
- More robust metadata cleanup (Remix/Edit/Timecode) and query order `Artist Title` → `Title Artist`
- Keeps last successful cover during temporary API/metadata failures
- Visible no-cover SVG fallback (`no_cover.svg`) instead of a transparent pixel

## Installation

### Option A: HACS (Custom Repository)
1. Create a GitHub repository and copy these files as-is
2. In Home Assistant:
   - HACS → (⋮) → *Custom repositories*
   - Enter repository URL
   - Type: **Integration**
   - Install
3. Restart Home Assistant

### Option B: Manual
1. Copy folder `custom_components/media_cover_art/` to `<config>/custom_components/media_cover_art/`
2. Restart Home Assistant

## Setup
- Settings → Devices & Services → Add Integration → **Media Cover Art**
- Select your `media_player` (for example HomePods)

## Lovelace usage
- Use a Picture card with entity:
  - `type: picture-entity`
  - `entity: image.media_cover_art_homepods_cover`

## Notes / limitations
- Radio streams with very generic metadata can still produce wrong matches.
- More providers can be added over time.

## Development
- Domain: `media_cover_art`
- Platforms: `image`, `camera`
