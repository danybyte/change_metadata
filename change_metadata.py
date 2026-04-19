import os
import sys
import time
from datetime import datetime

try:
    from PIL import Image
    import piexif
    from colorama import init, Fore, Style
except ImportError as e:
    print(f"Error: Required library not installed - {e}")
    print("Please run the following commands:")
    print("pip install Pillow piexif colorama")
    sys.exit(1)

init(autoreset=True)

def typewriter_print(text, delay=0.03, color=None):
    """Print text with typewriter effect and optional color"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def color_print(text, color):
    """Print colored text"""
    color_map = {
        'green': Fore.GREEN,
        'yellow': Fore.YELLOW,
        'red': Fore.RED,
        'blue': Fore.BLUE,
        'magenta': Fore.MAGENTA,
        'cyan': Fore.CYAN,
        'white': Fore.WHITE
    }
    print(f"{color_map.get(color, Fore.WHITE)}{text}{Style.RESET_ALL}")

def success_msg(text):
    color_print(f"✔ {text}", 'green')

def warning_msg(text):
    color_print(f"⚠ {text}", 'yellow')

def error_msg(text):
    color_print(f"✖ {text}", 'red')

def section_title(text):
    color_print(f"\n--- {text} ---", 'cyan')

def decimal_to_dms_rational(decimal, is_lat=True):
    """
    Convert decimal degrees to rational tuples suitable for EXIF GPS
    Returns: ((deg_num, deg_den), (min_num, min_den), (sec_num, sec_den))
    """
    negative = decimal < 0
    decimal = abs(decimal)
    degrees = int(decimal)
    minutes_full = (decimal - degrees) * 60
    minutes = int(minutes_full)
    seconds = (minutes_full - minutes) * 60
    sec_num = int(round(seconds * 1000))
    sec_den = 1000
    return (
        (degrees, 1),
        (minutes, 1),
        (sec_num, sec_den)
    ), negative

def dms_rational_to_decimal(degrees_tuple, minutes_tuple, seconds_tuple, ref):
    """
    Convert EXIF rational tuples to decimal degrees
    """
    deg = degrees_tuple[0] / degrees_tuple[1] if degrees_tuple[1] != 0 else 0
    min_val = minutes_tuple[0] / minutes_tuple[1] if minutes_tuple[1] != 0 else 0
    sec = seconds_tuple[0] / seconds_tuple[1] if seconds_tuple[1] != 0 else 0
    decimal = deg + (min_val / 60.0) + (sec / 3600.0)
    if ref in ('S', 'W'):
        decimal = -decimal
    return decimal

def format_gps_coordinate(decimal, is_lat=True):
    """Convert decimal to readable DMS string"""
    negative = decimal < 0
    decimal = abs(decimal)
    deg = int(decimal)
    minutes_full = (decimal - deg) * 60
    minutes = int(minutes_full)
    seconds = (minutes_full - minutes) * 60
    direction = ''
    if is_lat:
        direction = 'N' if not negative else 'S'
    else:
        direction = 'E' if not negative else 'W'
    return f"{deg}° {minutes}' {seconds:.2f}\" {direction}"

# ---------- Core program functions ----------
def load_exif(image_path):
    """Load EXIF metadata from image file"""
    try:
        exif_dict = piexif.load(image_path)
        return exif_dict
    except Exception as e:
        error_msg(f"Error reading metadata: {e}")
        return None

def display_metadata(exif_dict):
    """Display categorized metadata"""
    if not exif_dict:
        warning_msg("This image contains no metadata.")
        return

    section_title("Basic Image Information")
    ifd0 = exif_dict.get("0th", {})
    interesting_0th = {
        piexif.ImageIFD.Make: "Camera Make",
        piexif.ImageIFD.Model: "Camera Model",
        piexif.ImageIFD.DateTime: "Date & Time",
        piexif.ImageIFD.ImageDescription: "Image Description",
        piexif.ImageIFD.Software: "Software",
        piexif.ImageIFD.Artist: "Artist",
    }
    for tag_id, label in interesting_0th.items():
        if tag_id in ifd0:
            value = ifd0[tag_id]
            if isinstance(value, bytes):
                value = value.decode('utf-8', errors='ignore')
            color_print(f"  {label}: {value}", 'white')
    section_title("Technical Camera Information (Exif)")
    exif = exif_dict.get("Exif", {})
    interesting_exif = {
        piexif.ExifIFD.DateTimeOriginal: "Original Date & Time",
        piexif.ExifIFD.DateTimeDigitized: "Digitized Date & Time",
        piexif.ExifIFD.ExposureTime: "Exposure Time",
        piexif.ExifIFD.FNumber: "F Number",
        piexif.ExifIFD.ISOSpeedRatings: "ISO",
        piexif.ExifIFD.FocalLength: "Focal Length",
    }
    for tag_id, label in interesting_exif.items():
        if tag_id in exif:
            value = exif[tag_id]
            if isinstance(value, bytes):
                value = value.decode('utf-8', errors='ignore')
            if isinstance(value, tuple) and len(value) == 2:
                if value[1] != 0:
                    value = f"{value[0]}/{value[1]}"
            color_print(f"  {label}: {value}", 'white')
    section_title("Location Information (GPS)")
    gps = exif_dict.get("GPS", {})
    if gps:
        try:
            lat_ref = gps.get(piexif.GPSIFD.GPSLatitudeRef, b'N').decode()
            lat = gps.get(piexif.GPSIFD.GPSLatitude)
            lon_ref = gps.get(piexif.GPSIFD.GPSLongitudeRef, b'E').decode()
            lon = gps.get(piexif.GPSIFD.GPSLongitude)
            if lat and lon:
                lat_dec = dms_rational_to_decimal(lat[0], lat[1], lat[2], lat_ref)
                lon_dec = dms_rational_to_decimal(lon[0], lon[1], lon[2], lon_ref)
                color_print(f"  Latitude: {format_gps_coordinate(lat_dec, is_lat=True)}", 'white')
                color_print(f"  Longitude: {format_gps_coordinate(lon_dec, is_lat=False)}", 'white')
            else:
                color_print("  (Incomplete GPS data)", 'yellow')
        except Exception as e:
            color_print(f"  Error displaying GPS: {e}", 'red')
    else:
        color_print("  (No location data)", 'yellow')

def edit_datetime(exif_dict):
    """Edit photo date and time"""
    try:
        new_datetime = input("Enter new date and time (format YYYY:MM:DD HH:MM:SS): ").strip()
        datetime.strptime(new_datetime, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        error_msg("Invalid date format. Please follow the requested format exactly.")
        return exif_dict, False
    if "0th" not in exif_dict:
        exif_dict["0th"] = {}
    exif_dict["0th"][piexif.ImageIFD.DateTime] = new_datetime

    if "Exif" not in exif_dict:
        exif_dict["Exif"] = {}
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = new_datetime
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = new_datetime

    success_msg("Date and time updated successfully.")
    return exif_dict, True

def edit_camera_make(exif_dict):
    """Edit camera manufacturer"""
    new_make = input("Enter new camera make: ").strip()
    if "0th" not in exif_dict:
        exif_dict["0th"] = {}
    exif_dict["0th"][piexif.ImageIFD.Make] = new_make
    success_msg("Camera make updated successfully.")
    return exif_dict, True

def edit_camera_model(exif_dict):
    """Edit camera model"""
    new_model = input("Enter new camera model: ").strip()
    if "0th" not in exif_dict:
        exif_dict["0th"] = {}
    exif_dict["0th"][piexif.ImageIFD.Model] = new_model
    success_msg("Camera model updated successfully.")
    return exif_dict, True

def edit_gps(exif_dict):
    """Add or change GPS location"""
    try:
        lat = float(input("Enter latitude (-90 to 90): "))
        lon = float(input("Enter longitude (-180 to 180): "))
    except ValueError:
        error_msg("Please enter valid numbers.")
        return exif_dict, False

    if not (-90 <= lat <= 90):
        error_msg("Latitude must be between -90 and 90.")
        return exif_dict, False
    if not (-180 <= lon <= 180):
        error_msg("Longitude must be between -180 and 180.")
        return exif_dict, False
    lat_dms, lat_neg = decimal_to_dms_rational(lat, is_lat=True)
    lon_dms, lon_neg = decimal_to_dms_rational(lon, is_lat=False)

    if "GPS" not in exif_dict:
        exif_dict["GPS"] = {}

    gps = exif_dict["GPS"]
    gps[piexif.GPSIFD.GPSLatitudeRef] = 'S' if lat_neg else 'N'
    gps[piexif.GPSIFD.GPSLatitude] = lat_dms
    gps[piexif.GPSIFD.GPSLongitudeRef] = 'W' if lon_neg else 'E'
    gps[piexif.GPSIFD.GPSLongitude] = lon_dms

    success_msg("Location saved successfully.")
    return exif_dict, True

def clear_all_metadata(image_path):
    """Completely remove EXIF metadata from file"""
    try:
        piexif.remove(image_path)
        success_msg("All metadata removed successfully.")
    except Exception as e:
        error_msg(f"Error removing metadata: {e}")

def save_exif_with_rollback(image_path, original_exif, modified_exif):
    """Save metadata with rollback capability on error"""
    try:
        exif_bytes = piexif.dump(modified_exif)
        piexif.insert(exif_bytes, image_path)
        return True
    except Exception as e:
        error_msg(f"Error saving metadata: {e}")
        warning_msg("Attempting to restore file to previous state...")
        try:
            exif_bytes_orig = piexif.dump(original_exif)
            piexif.insert(exif_bytes_orig, image_path)
            success_msg("Restoration successful.")
        except Exception as e2:
            error_msg(f"Restoration failed: {e2}")
        return False

def edit_menu(exif_dict, image_path):
    """Metadata editing submenu"""
    if exif_dict is None:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    while True:
        section_title("Metadata Edit Menu")
        print("1. Change Date & Time")
        print("2. Edit Camera Model")
        print("3. Edit Camera Make")
        print("4. Add/Change GPS Location")
        print("5. Clear All Metadata (Remove EXIF)")
        print("6. Return to Main Menu")

        choice = input("Your choice: ").strip()
        if choice == '6':
            break

        modified = False
        import copy
        backup_exif = copy.deepcopy(exif_dict)

        if choice == '1':
            exif_dict, modified = edit_datetime(exif_dict)
        elif choice == '2':
            exif_dict, modified = edit_camera_model(exif_dict)
        elif choice == '3':
            exif_dict, modified = edit_camera_make(exif_dict)
        elif choice == '4':
            exif_dict, modified = edit_gps(exif_dict)
        elif choice == '5':
            confirm = input("Are you sure? This will remove all metadata (y/n): ").strip().lower()
            if confirm == 'y':
                clear_all_metadata(image_path)
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
                modified = True
                break
            else:
                continue
        else:
            warning_msg("Invalid option")
            continue

        if modified:
            if save_exif_with_rollback(image_path, backup_exif, exif_dict):
                success_msg("Changes saved successfully.")
            else:
                exif_dict = backup_exif
        else:
            warning_msg("No changes were made.")

    return exif_dict

def main_menu(image_path):
    """Main menu for a single image file"""
    exif_dict = load_exif(image_path)
    if exif_dict is None:
        warning_msg("Image file is valid but no metadata found or reading encountered an error.")
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    while True:
        section_title(f"File: {os.path.basename(image_path)}")
        print("1. View Metadata")
        print("2. Edit Metadata")
        print("3. Select New File")

        choice = input("Your choice: ").strip()

        if choice == '1':
            display_metadata(exif_dict)
        elif choice == '2':
            exif_dict = edit_menu(exif_dict, image_path)
        elif choice == '3':
            break
        else:
            warning_msg("Invalid option. Please enter 1, 2, or 3.")

def main():
    """Main program function"""
    typewriter_print("Welcome to Advanced Image Metadata Editor!", delay=0.03, color='cyan')
    print()
    typewriter_print("This program allows you to view, edit, and remove hidden information from photos.", delay=0.02, color='white')
    print()

    while True:
        color_print("\nEnter 'exit' to quit.", 'yellow')
        image_path = input("Image file path: ").strip()

        if image_path.lower() == 'exit':
            typewriter_print("Thank you for using the program. Goodbye!", delay=0.03, color='magenta')
            break

        image_path = image_path.strip('"\'')

        if not os.path.isfile(image_path):
            error_msg("File does not exist. Please enter a valid path.")
            continue
        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception as e:
            error_msg(f"File is not a valid image or is corrupted: {e}")
            continue
        main_menu(image_path)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        typewriter_print("Program terminated by Ctrl+C. Goodbye!", delay=0.03, color='magenta')
        sys.exit(0)
