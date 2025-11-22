#!/usr/bin/env python3
"""
Foto-Organizer: Benennt Fotos nach ISO-Datumsformat um und sortiert sie in Ordnerstruktur
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS

def get_exif_date(image_path):
    """
    Extrahiert das Aufnahmedatum aus den EXIF-Daten
    """
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if exif_data is not None:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                
                # Suche nach DateTimeOriginal (Aufnahmedatum)
                if tag == "DateTimeOriginal":
                    # Format: "2024:11:22 14:30:45"
                    date_obj = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    return date_obj
                
                # Fallback auf DateTime
                if tag == "DateTime":
                    date_obj = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    return date_obj
        
        # Wenn keine EXIF-Daten, verwende Datei-Änderungsdatum
        mtime = os.path.getmtime(image_path)
        return datetime.fromtimestamp(mtime)
        
    except Exception as e:
        print(f"Warnung: Konnte Datum nicht aus {image_path} lesen: {e}")
        # Fallback: Datei-Änderungsdatum
        mtime = os.path.getmtime(image_path)
        return datetime.fromtimestamp(mtime)

def is_already_processed(filename):
    """
    Prüft ob eine Datei bereits das ISO-Datumsformat hat
    Format: YYYY-MM-DD_HHMMSS_... oder NO_DATE_...
    """
    import re
    # Pattern: Startet mit YYYY-MM-DD_HHMMSS oder NO_DATE_
    pattern = r'^(\d{4}-\d{2}-\d{2}_\d{6}_|NO_DATE_)'
    return re.match(pattern, filename) is not None

def extract_date_from_filename(filename):
    """
    Versucht Datum aus dem Dateinamen zu extrahieren
    Unterstützte Formate:
    - YYYYMMDD (z.B. 20200405)
    - YYYY-MM-DD
    - YYYY_MM_DD
    - IMG_YYYYMMDD
    - und weitere Varianten
    """
    import re

    # Entferne Dateiendung für die Suche
    name_without_ext = Path(filename).stem

    # Verschiedene Datumsmuster
    patterns = [
        # YYYYMMDD (z.B. 20200405, IMG_20200405, VID_20200405)
        (r'(\d{4})(\d{2})(\d{2})', '%Y%m%d'),
        # YYYY-MM-DD
        (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),
        # YYYY_MM_DD
        (r'(\d{4})_(\d{2})_(\d{2})', '%Y_%m_%d'),
        # DD-MM-YYYY oder DD_MM_YYYY
        (r'(\d{2})[-_](\d{2})[-_](\d{4})', '%d-%m-%Y'),
    ]

    for pattern, date_format in patterns:
        match = re.search(pattern, name_without_ext)
        if match:
            try:
                # Extrahiere die gefundenen Gruppen
                if date_format in ['%Y%m%d', '%Y-%m-%d', '%Y_%m_%d']:
                    year, month, day = match.groups()
                    date_str = f"{year}{month}{day}"
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                elif date_format in ['%d-%m-%Y']:
                    day, month, year = match.groups()
                    date_str = f"{year}{month}{day}"
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                else:
                    continue

                # Validiere Datum (z.B. kein 20209999)
                if 1900 <= date_obj.year <= 2100:
                    return date_obj
            except ValueError:
                # Ungültiges Datum, weitermachen
                continue

    return None

def get_video_date(file_path):
    """
    Versucht das Erstelldatum aus Video-Metadaten zu extrahieren
    """
    try:
        import subprocess
        import json

        # Versuche ffprobe zu verwenden (falls installiert)
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', str(file_path)],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            if 'format' in data and 'tags' in data['format']:
                tags = data['format']['tags']
                # Suche nach creation_time oder ähnlichen Tags
                for key in ['creation_time', 'date', 'DATE', 'datetime']:
                    if key in tags:
                        date_str = tags[key]
                        # Verschiedene Datumsformate versuchen
                        for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                            try:
                                return datetime.strptime(date_str.split('.')[0].replace('Z', ''), fmt.replace('.%f', ''))
                            except:
                                continue
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass

    return None

def organize_photos(source_dir, target_dir, folder_structure="year_month", dry_run=True, copy_files=True):
    """
    Organisiert Fotos in Ordnerstruktur mit ISO-Datumsformat

    Args:
        source_dir: Quellverzeichnis mit Fotos
        target_dir: Zielverzeichnis für organisierte Fotos
        folder_structure: "year_month" (2024/2024-11), "year_only" (2024/), "year_month_day" (2024/2024-11/2024-11-22)
        dry_run: Wenn True, nur Vorschau ohne Änderungen
        copy_files: Wenn True, kopieren statt verschieben
    """

    # Unterstützte Bild- und Videoformate
    image_formats = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.raw', '.cr2', '.nef', '.arw', '.dng', '.tiff', '.tif', '.gif', '.bmp', '.webp'}
    video_formats = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.m4v', '.mpg', '.mpeg', '.3gp', '.mts', '.m2ts'}
    other_formats = {'.xcf', '.psd', '.ai', '.svg', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'}

    supported_formats = image_formats | video_formats | other_formats

    source_path = Path(source_dir).resolve()
    target_path = Path(target_dir).resolve()

    if not source_path.exists():
        print(f"Fehler: Quellverzeichnis {source_dir} existiert nicht!")
        return

    # Warnung bei überlappenden Verzeichnissen
    try:
        if source_path == target_path:
            print(f"\n⚠️  WARNUNG: Quell- und Zielverzeichnis sind identisch!")
            print(f"   Bereits verarbeitete Dateien werden übersprungen.\n")
        elif target_path.is_relative_to(source_path):
            print(f"\n⚠️  WARNUNG: Zielverzeichnis liegt innerhalb des Quellverzeichnisses!")
            print(f"   Bereits verarbeitete Dateien werden übersprungen.\n")
        elif source_path.is_relative_to(target_path):
            print(f"\n⚠️  WARNUNG: Quellverzeichnis liegt innerhalb des Zielverzeichnisses!")
            print(f"   Bereits verarbeitete Dateien werden übersprungen.\n")
    except (ValueError, AttributeError):
        # is_relative_to gibt es erst ab Python 3.9
        if str(target_path).startswith(str(source_path)) or str(source_path).startswith(str(target_path)):
            print(f"\n⚠️  WARNUNG: Quell- und Zielverzeichnis überlappen!")
            print(f"   Bereits verarbeitete Dateien werden übersprungen.\n")
    
    # Sammle alle Bilddateien (als set um Duplikate zu vermeiden)
    image_files_set = set()
    for ext in supported_formats:
        image_files_set.update(source_path.rglob(f"*{ext}"))
        image_files_set.update(source_path.rglob(f"*{ext.upper()}"))

    # Konvertiere set zurück zu Liste
    image_files = list(image_files_set)
    
    print(f"\n{'='*70}")
    print(f"Gefundene Bilder: {len(image_files)}")
    print(f"Quelle: {source_dir}")
    print(f"Ziel: {target_dir}")
    print(f"Ordnerstruktur: {folder_structure}")
    print(f"Modus: {'DRY RUN (Vorschau)' if dry_run else 'LIVE (Dateien werden geändert)'}")
    print(f"Aktion: {'Kopieren' if copy_files else 'Verschieben'}")
    print(f"{'='*70}\n")
    
    processed = 0
    skipped = 0
    errors = 0
    
    for file_path in image_files:
        try:
            original_name = file_path.stem
            extension = file_path.suffix.lower()
            date_taken = None

            # Prüfe ob Datei bereits im ISO-Format ist
            file_already_in_iso_format = is_already_processed(file_path.name)

            # PRIORITÄT 1: Versuche Datum aus Dateinamen zu extrahieren
            date_from_filename = extract_date_from_filename(file_path.name)

            if date_from_filename:
                # Datum im Dateinamen gefunden - verwende dieses
                date_taken = date_from_filename
                print(f"[INFO] Datum aus Dateiname extrahiert: {file_path.name} -> {date_taken.strftime('%Y-%m-%d')}")
            # PRIORITÄT 2: Versuche Datum zu extrahieren basierend auf Dateityp
            elif extension in image_formats:
                # Bildformate: EXIF-Daten
                date_taken = get_exif_date(file_path)
            elif extension in video_formats:
                # Videoformate: Metadaten (ffprobe) oder Datei-Änderungsdatum
                date_taken = get_video_date(file_path)
                if date_taken is None:
                    # Fallback: Datei-Änderungsdatum
                    mtime = os.path.getmtime(file_path)
                    date_taken = datetime.fromtimestamp(mtime)
            else:
                # Andere Formate: Nur Datei-Änderungsdatum
                mtime = os.path.getmtime(file_path)
                date_taken = datetime.fromtimestamp(mtime)

            # Erstelle neuen Dateinamen im ISO-Format
            # Format: YYYY-MM-DD_HHMMSS_original.ext oder NO_DATE_original.ext
            if file_already_in_iso_format:
                # Datei ist bereits im ISO-Format, behalte den Namen
                new_filename = file_path.name
            elif date_taken:
                new_filename = f"{date_taken.strftime('%Y-%m-%d_%H%M%S')}_{original_name}{extension}"
            else:
                # Kein Datum verfügbar - verwende NO_DATE Präfix
                new_filename = f"NO_DATE_{original_name}{extension}"
            
            # Erstelle Ordnerstruktur
            if date_taken:
                if folder_structure == "year_month":
                    folder = target_path / str(date_taken.year) / date_taken.strftime("%Y-%m")
                elif folder_structure == "year_only":
                    folder = target_path / str(date_taken.year)
                elif folder_structure == "year_month_day":
                    folder = target_path / str(date_taken.year) / date_taken.strftime("%Y-%m") / date_taken.strftime("%Y-%m-%d")
                else:
                    folder = target_path
            else:
                # Dateien ohne Datum: in gleichen Ordner wie Fotos aus ursprünglichem Ordner
                # Berechne relativen Pfad vom Quellverzeichnis
                try:
                    relative_parent = file_path.parent.relative_to(source_path)
                    folder = target_path / relative_parent
                except ValueError:
                    folder = target_path

            new_path = folder / new_filename

            # Prüfe ob Zieldatei bereits existiert
            if new_path.exists():
                # Vergleiche Dateigröße um echte Duplikate zu erkennen
                if new_path.stat().st_size == file_path.stat().st_size:
                    print(f"[ÜBERSPRUNGEN] {file_path.name} - existiert bereits im Ziel: {new_path.relative_to(target_path)}")
                    skipped += 1
                    continue
                else:
                    # Dateien haben gleichen Namen aber unterschiedliche Größe
                    # Füge Nummer hinzu um Überschreiben zu vermeiden
                    counter = 1
                    base_filename = new_filename
                    while new_path.exists():
                        name_without_ext = Path(base_filename).stem
                        new_filename = f"{name_without_ext}_{counter}{extension}"
                        new_path = folder / new_filename
                        counter += 1
                    print(f"[WARNUNG] {file_path.name} - Datei mit gleichem Namen aber anderer Größe existiert. Speichere als: {new_filename}")

            if dry_run:
                print(f"[VORSCHAU] {file_path.name} -> {new_path.relative_to(target_path)}")
            else:
                # Erstelle Zielordner
                folder.mkdir(parents=True, exist_ok=True)

                # Kopiere oder verschiebe Datei
                if copy_files:
                    shutil.copy2(file_path, new_path)
                    print(f"[KOPIERT] {file_path.name} -> {new_path.relative_to(target_path)}")
                else:
                    shutil.move(str(file_path), str(new_path))
                    print(f"[VERSCHOBEN] {file_path.name} -> {new_path.relative_to(target_path)}")

            processed += 1

        except Exception as e:
            print(f"[FEHLER] Konnte {file_path.name} nicht verarbeiten: {e}")
            errors += 1
    
    print(f"\n{'='*70}")
    print(f"Zusammenfassung:")
    print(f"  Verarbeitet: {processed}")
    print(f"  Übersprungen: {skipped}")
    print(f"  Fehler: {errors}")
    print(f"{'='*70}\n")
    
    if dry_run:
        print("Dies war eine VORSCHAU. Führe das Script mit --execute aus, um die Änderungen durchzuführen.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Organisiert Fotos nach ISO-Datumsformat und Ordnerstruktur",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Vorschau (Dry Run)
  python photo_organizer.py /pfad/zu/fotos /pfad/zu/ziel

  # Fotos kopieren und organisieren
  python photo_organizer.py /pfad/zu/fotos /pfad/zu/ziel --execute
  
  # Fotos verschieben statt kopieren
  python photo_organizer.py /pfad/zu/fotos /pfad/zu/ziel --execute --move
  
  # Andere Ordnerstruktur
  python photo_organizer.py /pfad/zu/fotos /pfad/zu/ziel --structure year_only
  
Ordnerstrukturen:
  year_month      -> 2024/2024-11/2024-11-22_143045_IMG1234.jpg
  year_only       -> 2024/2024-11-22_143045_IMG1234.jpg
  year_month_day  -> 2024/2024-11/2024-11-22/2024-11-22_143045_IMG1234.jpg
        """
    )
    
    parser.add_argument("source", help="Quellverzeichnis mit Fotos")
    parser.add_argument("target", help="Zielverzeichnis für organisierte Fotos")
    parser.add_argument(
        "--structure",
        choices=["year_month", "year_only", "year_month_day"],
        default="year_month",
        help="Ordnerstruktur (Standard: year_month)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Führt die Änderungen durch (ohne diesen Parameter: nur Vorschau)"
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Dateien verschieben statt kopieren (Vorsicht!)"
    )
    
    args = parser.parse_args()
    
    organize_photos(
        source_dir=args.source,
        target_dir=args.target,
        folder_structure=args.structure,
        dry_run=not args.execute,
        copy_files=not args.move
    )

if __name__ == "__main__":
    main()
