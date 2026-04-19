# Advanced Image Metadata Editor

A powerful command-line tool for viewing, editing, and removing hidden EXIF metadata from images.

## Features

- View metadata in categories (basic info, camera tech data, GPS location)
- Edit date/time, camera make, camera model
- Add or change GPS coordinates (decimal degrees)
- Clear all metadata completely (remove EXIF)
- Automatic rollback – restores original metadata if save fails
- Colored interactive interface with typewriter effect
- Supports JPEG, PNG, TIFF (JPEG recommended for full EXIF support)

## Requirements

- Python 3.6 or higher
- Libraries: `Pillow`, `piexif`, `colorama`

Install with pip:

```command line
pip install Pillow piexif colorama
```

## Installation
run:

```command line
python change_metadata.py
```

## Main Menu
```terminal
--- File: photo.jpg ---
1. View Metadata
2. Edit Metadata
3. Select New File
```

## Edit Menu
```terminal
--- Metadata Edit Menu ---
1. Change Date & Time
2. Edit Camera Model
3. Edit Camera Make
4. Add/Change GPS Location
5. Clear All Metadata (Remove EXIF)
6. Return to Main Menu
```
Date format: YYYY:MM:DD HH:MM:SS (example: 2025:03:21 14:30:00)

GPS input: Latitude (-90 to 90) and Longitude (-180 to 180) as decimal numbers.

## Notes
EXIF metadata only (no XMP/IPTC support)
PNG and other formats may lack EXIF; JPEG is recommended



## Author:
## DanyByte
