# Foto-Organizer

Ein intelligentes Python-Tool zum automatischen Organisieren und Umbenennen von Fotos, Videos und anderen Mediendateien nach Aufnahmedatum in einer übersichtlichen Ordnerstruktur.

## Features

✅ **Intelligente Datumserkennung** aus Dateinamen (z.B. `IMG_20200405`)
✅ **EXIF-Daten** (Aufnahmedatum) aus Fotos
✅ **Video-Metadaten** (via ffprobe)
✅ **ISO-Format**: `YYYY-MM-DD_HHMMSS_originalname.ext`
✅ **Unterstützt**: Fotos, Videos, GIMP-Projekte, PDFs, etc.
✅ **Duplikat-Vermeidung** bei wiederholter Ausführung
✅ **Dry-Run Modus** zur Vorschau
✅ **Kopieren oder Verschieben** möglich
✅ **Flexible Ordnerstrukturen** (Jahr/Monat/Tag)  

## Installation

### Voraussetzungen

- Python 3.7 oder höher
- Pip (Python Package Manager)

### Windows

1. Python installieren (falls noch nicht vorhanden):
   - Download von https://www.python.org/downloads/
   - Bei Installation "Add Python to PATH" aktivieren

2. Benötigte Pakete installieren:
```bash
pip install -r requirements.txt
```

3. Optional: FFmpeg für Video-Metadaten installieren:
```bash
winget install FFmpeg
```

### Linux/Mac

```bash
pip3 install -r requirements.txt
```

**macOS - FFmpeg installieren**:
```bash
brew install ffmpeg
```

**Linux (Debian/Ubuntu) - FFmpeg installieren**:
```bash
sudo apt install ffmpeg
```

## Verwendung

### 1. Vorschau (Dry Run) - EMPFOHLEN!

**Führe immer zuerst eine Vorschau aus**, um zu sehen, was passieren wird:

```bash
python photo_organizer.py "C:\Meine Fotos" "D:\Organisierte Fotos"
```

### 2. Fotos kopieren und organisieren

Wenn die Vorschau gut aussieht, kopiere die Fotos:

```bash
python photo_organizer.py "C:\Meine Fotos" "D:\Organisierte Fotos" --execute
```

### 3. Fotos verschieben (Original wird gelöscht)

⚠️ **Vorsicht**: Originale werden verschoben/gelöscht!

```bash
python photo_organizer.py "C:\Meine Fotos" "D:\Organisierte Fotos" --execute --move
```

## Ordnerstrukturen

### Standard: year_month (empfohlen)
```
2024/
  2024-11/
    2024-11-22_143045_IMG1234.jpg
    2024-11-22_150312_IMG1235.jpg
  2024-12/
    2024-12-01_120000_IMG1236.jpg
```

### year_only (einfacher)
```
2024/
  2024-11-22_143045_IMG1234.jpg
  2024-11-22_150312_IMG1235.jpg
  2024-12-01_120000_IMG1236.jpg
```

### year_month_day (detailliert)
```
2024/
  2024-11/
    2024-11-22/
      2024-11-22_143045_IMG1234.jpg
      2024-11-22_150312_IMG1235.jpg
    2024-11-23/
      2024-11-23_100000_IMG1236.jpg
```

Struktur ändern mit `--structure`:

```bash
python photo_organizer.py "C:\Meine Fotos" "D:\Organisierte Fotos" --structure year_only --execute
```

## Unterstützte Formate

### Bilder
- **JPG/JPEG** - Standard Fotos
- **PNG** - Screenshots, Grafiken
- **HEIC/HEIF** - iPhone Fotos (neuere Modelle)
- **RAW-Formate** - CR2 (Canon), NEF (Nikon), ARW (Sony), DNG
- **TIFF/TIF** - Professionelle Fotos
- **GIF/BMP/WEBP** - Weitere Formate

### Videos
- **MP4/M4V** - Standard Videos
- **MOV** - Apple/QuickTime Videos
- **AVI/WMV** - Windows Videos
- **MKV** - Matroska Videos
- **MPG/MPEG** - MPEG Videos
- **3GP** - Smartphone Videos
- **MTS/M2TS** - AVCHD Videos (Camcorder)

### Andere Dateitypen
- **XCF** - GIMP Projekte
- **PSD** - Photoshop Dateien
- **AI/SVG** - Vektorgrafiken
- **PDF** - Dokumente
- **DOC/DOCX, XLS/XLSX** - Office Dokumente
- **TXT** - Textdateien

## Sicherheitshinweise

### ✅ Empfohlener Workflow

1. **Backup erstellen** - Sichere deine Fotos vorher!
2. **Dry-Run testen** - Ohne `--execute` Parameter
3. **Erst kopieren** - Standard ohne `--move`
4. **Ergebnis prüfen** - Kontrolliere das Zielverzeichnis
5. **Original löschen** - Erst wenn alles ok ist

### ⚠️ Wichtig

- Das Script überschreibt keine Dateien
- Bereits verarbeitete Dateien (ISO-Format) werden automatisch übersprungen
- Bei Namenskonflikten wird eine Nummer angehängt (nur bei unterschiedlicher Dateigröße)
- Ohne EXIF-Daten wird das Datei-Änderungsdatum verwendet
- Original-Dateinamen bleiben teilweise erhalten

## Intelligente Datumserkennung

Das Tool priorisiert Datumsquellen in folgender Reihenfolge:

### 1. Datum aus Dateinamen (höchste Priorität)
Erkennt automatisch Datumsmuster im Dateinamen:
- `IMG_20200405_1234.jpg` → 2020-04-05
- `VID-2019-12-25.mp4` → 2019-12-25
- `20200405_foto.jpg` → 2020-04-05
- `05-04-2020_scan.pdf` → 2020-04-05

### 2. EXIF-Daten (bei Fotos)
Liest Aufnahmedatum aus Foto-Metadaten:
- DateTimeOriginal
- DateTime

### 3. Video-Metadaten (bei Videos)
Nutzt ffprobe um Metadaten auszulesen:
- creation_time
- date

### 4. Datei-Änderungsdatum (Fallback)
Als letzter Ausweg wird das Datei-Änderungsdatum verwendet.

## Duplikat-Vermeidung

Das Tool ist intelligent genug, um wiederholte Ausführungen zu handhaben:

- **Bereits verarbeitet**: Dateien mit ISO-Format (`YYYY-MM-DD_HHMMSS_...`) werden übersprungen
- **Identische Datei**: Wird übersprungen (gleicher Name + gleiche Dateigröße)
- **Namenskonflikt**: Erhält Suffix `_1`, `_2`, etc. (nur bei unterschiedlicher Größe)
- **Warnung**: Bei überlappenden Quell-/Zielverzeichnissen

## Beispiele

### Für Nextcloud/PhotoPrism

Organisiere Fotos und kopiere sie direkt in dein Nextcloud-Verzeichnis:

```bash
python photo_organizer.py "C:\Users\Name\Pictures" "C:\Users\Name\Nextcloud\Fotos" --execute
```

### Von Smartphone importieren

Wenn Smartphone als Laufwerk verbunden:

```bash
python photo_organizer.py "E:\DCIM\Camera" "D:\Meine Fotos\2024" --execute
```

### Mehrere Ordner verarbeiten

Du kannst das Script mehrmals ausführen:

```bash
python photo_organizer.py "C:\Alte Fotos\Urlaub" "D:\Organisiert" --execute
python photo_organizer.py "C:\Alte Fotos\Familie" "D:\Organisiert" --execute
python photo_organizer.py "C:\Downloads" "D:\Organisiert" --execute
```

## Fehlerbehebung

### "ModuleNotFoundError: No module named 'PIL'"

```bash
pip install Pillow
```

### "Konnte Datum nicht lesen"

Das Script verwendet dann das Datei-Änderungsdatum als Fallback.

### Fotos haben falsches Datum

**Lösung 1**: Benenne die Datei mit dem richtigen Datum um:
```
IMG_20200405_foto.jpg
```
Das Tool erkennt das Datum automatisch aus dem Dateinamen!

**Lösung 2**: Überprüfe die EXIF-Daten deiner Fotos. Manche bearbeiteten Fotos verlieren die Original-Metadaten.

### HEIC-Dateien funktionieren nicht

Für HEIC-Support unter Windows:

```bash
pip install pillow-heif
```

## Hilfe

Alle Optionen anzeigen:

```bash
python photo_organizer.py --help
```

## Tipps

- 📱 **Smartphones**: Schalte "EXIF-Daten speichern" in der Kamera-App ein
- 🖼️ **Bearbeitung**: Nutze Software, die EXIF-Daten erhält (z.B. Luminar Neo)
- 💾 **Backup**: 3-2-1 Regel: 3 Kopien, 2 verschiedene Medien, 1 extern
- 🔄 **Regelmäßig**: Führe das Script monatlich aus für neue Fotos

## Integration mit PhotoPrism

Nach der Organisation kannst du die Fotos einfach in PhotoPrism importieren:

1. Fotos in den PhotoPrism-Originals-Ordner kopieren
2. In PhotoPrism: Settings → Library → Index
3. PhotoPrism erkennt die Ordnerstruktur automatisch

Die ISO-Datumsnamen helfen PhotoPrism bei der chronologischen Sortierung!

## Lizenz

MIT License - Copyright (c) 2024 [Baum64](https://github.com/Baum64)

## Autor

[Baum64](https://github.com/Baum64)

## Beiträge

Pull Requests und Issues sind willkommen!

## Changelog

### Version 1.0.0 (2024)
- ✨ Intelligente Datumserkennung aus Dateinamen
- ✨ Unterstützung für Videos und andere Dateitypen
- ✨ Video-Metadaten via ffprobe
- ✨ Duplikat-Vermeidung bei wiederholter Ausführung
- ✨ Warnung bei überlappenden Verzeichnissen
- ✨ EXIF-Daten Extraktion für Fotos
- ✨ Flexible Ordnerstrukturen
- ✨ Dry-Run Modus
