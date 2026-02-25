# Cover Art Wrapper (Home Assistant Custom Integration)

This integration provides cover artwork based on `media_artist` + `media_title` from a selected `media_player`, exposed as **Image**, **Camera**, and an optional **Media Player wrapper** entity.

Current providers: **iTunes Search API** + **MusicBrainz/Cover Art Archive** (no login required).

## Features

- Image entity (for example: `image.media_cover_art_homepods_cover`)
- Track change detection: refreshes only when `(artist,title,album)` changes
- Frontend-friendly caching: UI refetches when `image_last_updated` changes
- Integration icon/logo assets (SVG)
- Additional Camera entity for Picture Cards (`camera.*_cover_camera`)
- Additional universal-style Media Player wrapper entity with inherited controls + generated cover image (`media_player.*_cover`)
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
- Settings → Devices & Services → Add Integration → **Cover Art Wrapper**
- Select your `media_player` (for example HomePods)

## Lovelace usage
- Use a Picture card with entity:
  - `type: picture-entity`
  - `entity: image.media_cover_art_homepods_cover`

## Notes / limitations
- Radio streams with very generic metadata can still produce wrong matches.
- More providers can be added over time.


## Troubleshooting
- If you see startup errors related to `ImageEntity.__init__`/`Camera.__init__`, update to the latest release and fully restart Home Assistant.
- For debugging, watch these logs first:
  - `custom_components.media_cover_art`
  - `homeassistant.components.image`
  - `homeassistant.components.camera`
- Typical generated entities (based on selected source `media_player.homepods`):
  - `image.cover_homepods`
  - `camera.cover_homepods`
  - `media_player.homepods_cover`

## Development
- Domain: `media_cover_art`
- Platforms: `image`, `camera`, `media_player`
