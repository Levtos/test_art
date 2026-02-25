# Changelog

## 0.2.8 (2026-02-25)
- `Platform.SENSOR` zu `PLATFORMS` hinzugefügt – Sensor-Entity wurde nie geladen, da sie fehlte
- `available`-Property korrigiert: gibt jetzt `False` zurück wenn Quelle den State `unavailable`/`unknown` hat (statt immer `True`)
- `state`-Property korrigiert: gibt `None` zurück wenn kein Source-State vorhanden (HA setzt dann automatisch `unavailable`)
- `media_image_hash` verbessert: beinhaltet jetzt `last_updated`-Zeitstempel, damit der Browser-Cache invalidiert wird wenn das Cover nach dem Platzhalter nachgeladen wird

## 0.2.7 (2026-02-25)
- `media_player`-Wrapper robuster gemacht, damit die Entität zuverlässig erzeugt wird (reduzierte Attribut-Spiegelung + defensivere Source-Attribut-Lesezugriffe)
- Universal-Proxy-Verhalten beibehalten: Steuerung bleibt auf dem Source-Player, Cover kommt aus dem Coordinator
- MusicBrainz User-Agent auf `0.2.7` aktualisiert

## 0.2.6 (2026-02-25)
- Universellen `media_player`-Wrapper für Cover-Art dokumentiert (Entity `media_player.*_cover`)
- Merge-Konflikte für häufig parallel geänderte Doku-Dateien reduziert (`.gitattributes` mit `merge=union` für README/CHANGELOG)
- MusicBrainz User-Agent auf `0.2.6` aktualisiert

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
