import glob
import os
from PIL import Image as PILImage
directory = 'Music_Library'
jpg_pattern = os.path.join(directory, "**/*.jpg")
jpeg_pattern = os.path.join(directory, "**/*.jpeg")
png_pattern = os.path.join(directory, "**/*.png")

# Suchen der Dateien
jpg_files = glob.glob(jpg_pattern, recursive=True)
jpeg_files = glob.glob(jpeg_pattern, recursive=True)
png_files = glob.glob(png_pattern, recursive=True)

# Listen vereinigen
all_files = jpg_files + jpeg_files + png_files

# Filtern: Nur Pfade behalten, die "_passend" NICHT im Namen haben
filtered_files = [f for f in all_files if "_passend" not in os.path.basename(f)]

print(filtered_files)



for file_path in filtered_files:
    try:
        # Bild öffnen
        with PILImage.open(file_path) as img:
            # Bild auf 90x90 skalieren
            # LANCZOS sorgt für eine hohe Qualität beim Runterskalieren
            img_resized = img.resize((200, 200), PILImage.Resampling.LANCZOS)
            
            # Pfad und Dateiname aufteilen (z.B. 'pfad/bild' und '.jpg')
            base_path, extension = os.path.splitext(file_path)
            
            # Neuen Namen generieren: pfad/bild_passend.jpg
            new_file_path = f"{base_path}_passend{extension}"
            
            # Speichern
            img_resized.save(new_file_path)
            print(f"Gespeichert: {new_file_path}")
            
    except Exception as e:
        print(f"Fehler beim Verarbeiten von {file_path}: {e}")