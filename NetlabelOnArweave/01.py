import os
import re
import sys
import zipfile
import tempfile
import shutil
import requests
from mutagen.flac import FLAC

# The source link
REMOTE_ZIP_URL = (
    "https://permagate.io/IvkTHQGYtMUWCGtpkFsGTZefQQS9GkNj56QA-q3-8v4/02-Aurora2024-ReflectAndImprove.zip"
)


def unzip_file(zip_path, extract_to):
    """Unzip a ZIP file to a specified directory."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


def download_file(url, destination):
    """Download a file from a URL to a local destination."""
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(destination, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def check_filename_pattern(filename):
    """
    Check if filename matches the pattern.
    Return None if it is correct, or an error string if not.
    """
    pattern = r'^\d{2}\.\s*(.+?)\s*-\s*(.+?)\.flac$'
    if not re.match(pattern, filename):
        return f"Filename does not match 'NN. Artist - Title.flac' pattern: {filename}"
    return None


def check_cover_png_existence(folder_path):
    """
    Check if Cover.png exists in the folder path.
    """
    cover_path = os.path.join(folder_path, "Cover.png")
    if not os.path.isfile(cover_path):
        return "Cover.png not found in folder"
    return None


def check_flac_metadata(file_path):
    """
    Check a FLAC file's required metadata and audio parameters.
    Returns a list of problems found. Empty list if all OK.
    """
    problems = []
    try:
        flac_file = FLAC(file_path)
    except Exception as e:
        problems.append(f"Could not read FLAC metadata: {e}")
        return problems

    # Audio properties checks
    sample_rate = flac_file.info.sample_rate
    if sample_rate != 44100:
        problems.append(f"Sample rate is {sample_rate}, expected 44100")

    channels = flac_file.info.channels
    if channels != 2:
        problems.append(f"Channels are {channels}, expected 2")

    bits_per_sample = flac_file.info.bits_per_sample
    if bits_per_sample != 24:
        problems.append(f"Bits per sample is {bits_per_sample}, expected 24")

    # Check for embedded pictures
    pictures = flac_file.pictures
    if not pictures or all(p.type != 3 for p in pictures):
        problems.append("No embedded front cover found")

    flac_keys_lower = {k.lower(): k for k in flac_file.keys()}

    # Tags (VorbisComments in FLAC) – check presence
    needed_tags = {
        'artist': "Artist (ARTIST)",
        'title': "Title (TITLE)",
        'album': "Album (ALBUM)",
        'date': "Date (DATE)",
        'genre': "Genre (GENRE)",
        'albumartist': "Album Artist (ALBUMARTIST)",
        'tracknumber': "Track Number (TRACKNUMBER)"
    }

    for needed_key, desc in needed_tags.items():
        # Do we have a matching key (case-insensitive) in the FLAC?
        if needed_key not in flac_keys_lower:
            problems.append(f"{desc} is missing")
        else:
            real_key = flac_keys_lower[needed_key]
            if needed_key == 'albumartist':
                if (flac_file[real_key][0].lower() != "various artists"):
                    problems.append(
                        f"albumartist is '{flac_file[real_key][0]}', "
                        "expected 'Various Artists'"
                    )
    if ('totaltracks' not in flac_keys_lower) and ('tracktotal' not in flac_keys_lower):
        problems.append("Total track count is missing (expected TOTALTRACKS or TRACKTOTAL)")

    return problems


def compare_directories(me_dir, remote_dir):
    """
    Compare FLAC files in me_dir with those in remote_dir.
    For each matching FLAC, check the naming pattern, presence of cover, tags, etc.
    Prints out messages about what needs to be corrected.
    """
    # Gather FLAC files in me_dir
    me_flac_files = [
        f for f in os.listdir(me_dir)
        if f.lower().endswith('.flac') and os.path.isfile(os.path.join(me_dir, f))
    ]
    # For each FLAC file in me_dir, see if it exists in remote_dir
    for flac_file in me_flac_files:
        me_path = os.path.join(me_dir, flac_file)
        _report_problems_for_file(me_dir, flac_file, me_path)

    # Check that Cover.png is present in me_dir
    cover_problem = check_cover_png_existence(me_dir)
    if cover_problem:
        print(cover_problem)


def _report_problems_for_file(folder_path, filename, file_full_path):
    """Helper function to centralize the checks for a given FLAC file."""
    # Check filename pattern
    filename_problem = check_filename_pattern(filename)
    if filename_problem:
        print(f"- {filename_problem}")

    # Check FLAC metadata
    flac_problems = check_flac_metadata(file_full_path)
    for prob in flac_problems:
        print(f"- {filename}: {prob}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <local_zip_path>")
        sys.exit(1)

    me_zip = sys.argv[1]

    if not os.path.isfile(me_zip):
        print(f"ERROR: The file '{me_zip}' does not exist.")
        sys.exit(1)

    # Create temporary directories
    temp_dir_me = tempfile.mkdtemp(prefix="me_zip_")
    temp_dir_remote = tempfile.mkdtemp(prefix="remote_zip_")

    try:
        # Unzip ZIP
        unzip_file(me_zip, temp_dir_me)

        # Download the source ZIP
        remote_zip_path = os.path.join(temp_dir_remote, "downloaded.zip")
        print("Downloading remote ZIP...")
        download_file(REMOTE_ZIP_URL, remote_zip_path)

        # Unzip the source ZIP
        remote_extracted_dir = os.path.join(temp_dir_remote, "extracted_remote")
        os.makedirs(remote_extracted_dir, exist_ok=True)
        unzip_file(remote_zip_path, remote_extracted_dir)

        # Compare directories
        print("Comparing files...")
        compare_directories(temp_dir_me, remote_extracted_dir)

    finally:
        # Clean up
        shutil.rmtree(temp_dir_me, ignore_errors=True)
        shutil.rmtree(temp_dir_remote, ignore_errors=True)

if __name__ == "__main__":
    main()
