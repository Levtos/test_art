# Changelog

## 0.2.3 (2026-02-25)
- Neue `media_player`-Wrapper-Entity hinzugefügt, die Steuerfunktionen des gewählten Source-Players durchreicht und gleichzeitig das ermittelte Cover als Media-Bild nutzt
- Wrapper folgt Künstler/Titel-Updates über den bestehenden Coordinator und nutzt denselben Fallback-Mechanismus wie `image`/`camera`
- Dokumentation um die neue Entity ergänzt
- MusicBrainz User-Agent auf `0.2.3` aktualisiert

## 0.2.2 (2026-02-24)
- Gemeinsamen Code (`FALLBACK_IMAGE`, `source_name`) aus `image.py` und `camera.py` in neue Datei `helpers.py` ausgelagert (Duplikation beseitigt)
- `itunes.py`: Vier Regex-Muster in `_clean()` auf Modulebene vorkompiliert statt bei jedem Aufruf neu zu kompilieren
- `musicbrainz.py`: Debug-Logging bei fehlgeschlagenem Artwork-Download hinzugefügt (statt stilles `return None`)
- `musicbrainz.py`: User-Agent-Header auf aktuelle Version angepasst (`0.2.2`)

## 0.2.1 (2026-02-23)
- Staged Remix Fallback: Erst Remix-spezifisches Cover suchen, dann Original-Release als Fallback
- MusicBrainz als zweiter Provider hinzugefügt (Cover Art Archive)
- Camera-Entity für bessere Lovelace-Kompatibilität
- Status-Sensor mit Diagnostik-Attributen
- Konfigurierbare Artwork-Dimensionen (Breite/Höhe getrennt)
- Englische und deutsche Übersetzungen
- HACS-Metadaten und Icon

## 0.1.0 (2026-02-22)
- Initiale Version
- Image-Entity für Cover-Art aus `media_artist` + `media_title`
- Provider: iTunes Search API
