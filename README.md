# Media Cover Art (Home Assistant Custom Integration)

Diese Integration stellt ein Cover-Artwork als **Image-Entity** bereit, basierend auf `media_artist` + `media_title` eines ausgewählten `media_player`.

Aktuell: Provider = **iTunes Search API** (kein Login nötig).

## Features

- Image-Entity (z. B. `image.media_cover_art_homepods_cover`)
- Track-Change-Erkennung: holt neu nur wenn sich `(artist,title,album)` ändert
- Caching: Das Frontend refetcht nur wenn `image_last_updated` aktualisiert wurde
- Eigenes Integrations-Icon als SVG (`custom_components/media_cover_art/icon.svg`)
- Zusätzliche Status-Sensor-Entity als stabiler Fallback (`sensor.*_cover_status`)
- Robustere Titel-Bereinigung (Remix/Edit/Timecode) und Suchreihenfolge `Artist Title` → `Title Artist`
- Beibehaltung des letzten erfolgreichen Covers bei temporären API-/Metadaten-Ausfällen

## Installation

### Option A: HACS (Custom Repository)
1. GitHub Repo erstellen und diese Dateien 1:1 reinpacken
2. In Home Assistant:
   - HACS → (⋮) → *Custom repositories*
   - Repo-URL eintragen
   - Type: **Integration**
   - Installieren
3. Home Assistant neu starten

(HACS Custom Repository Schritte siehe Doku.) 

### Option B: Manuell
1. Ordner `custom_components/media_cover_art/` nach `<config>/custom_components/media_cover_art/` kopieren
2. Home Assistant neu starten

## Einrichtung
- Einstellungen → Geräte & Dienste → Integration hinzufügen → **Media Cover Art**
- Wähle deinen `media_player` (z. B. HomePods)

## Lovelace Nutzung
- Eine Picture Card mit Entity:
  - `type: picture-entity`
  - `entity: image.media_cover_art_homepods_cover`

## Hinweise / Grenzen
- Radiosender/Streams mit sehr generischen Titeln können “falsche” Treffer liefern (z. B. nur “For Real”).
- Später können weitere Provider ergänzt werden (Spotify/MusicBrainz).

## Entwicklung
- Domain: `media_cover_art`
- Platform: `image`
