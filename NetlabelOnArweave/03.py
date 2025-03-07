import argparse
import json
import os
import subprocess
import urllib.parse
from bs4 import BeautifulSoup

# Change to your local path to ardrive binary
ARDRIVE_BIN = "/Users/lrf/.nvm/versions/node/v23.4.0/bin/ardrive"

def fetch_ardrive_data(folder_id):
    """
    Runs ardrive list-folder --parent-folder-id <folder_id> --all
    to retrieve JSON describing just that folder (and subfolders).
    """
    env = os.environ.copy()
    env["PATH"] = os.path.dirname(ARDRIVE_BIN) + ":" + env.get("PATH", "")

    command = [
        ARDRIVE_BIN,
        "list-folder",
        "--parent-folder-id", folder_id,
        "--all"
    ]
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"Error running ardrive command:\n{result.stderr}")

    return json.loads(result.stdout)

def build_file_map(file_list, base_prefix=None):
    """
    Given a list of file objects (each with 'path' and 'dataTxId'),
    build a dict mapping 'relative_path' -> 'dataTxId'.

    If base_prefix is specified, we remove that from the start of the path
    (e.g. '/Aurora Compilations/aurora-2025-threshold/').
    Otherwise, we only strip leading slashes.
    """
    mapping = {}
    for item in file_list:
        # Skip anything that isn't a file
        if item.get("entityType") != "file":
            continue

        data_tx_id = item.get("dataTxId")
        full_path = item.get("path", "")
        if not data_tx_id or not full_path:
            continue

        if base_prefix and full_path.startswith(base_prefix):
            rel_path = full_path[len(base_prefix):]
        else:
            rel_path = full_path

        # Strip leading slash if present
        rel_path = rel_path.lstrip("/\\")

        # Convert backslashes to forward slashes
        rel_path = rel_path.replace("\\", "/")

        # Save in dict
        mapping[rel_path] = data_tx_id
    return mapping

def parse_dictionary_file(dict_path, base_prefix=None):
    """
    Parse a two-column dictionary file:
      (column1 = path, column2 = dataTxId)
    Returns a dict with key=path, value=dataTxId.
    Applies the same base_prefix stripping and slash cleanup as in build_file_map.
    """
    mapping = {}
    with open(dict_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            # Split from the right, in case paths contain spaces
            try:
                path_part, txid_part = line.rsplit(" ", 1)
            except ValueError:
                # If there's some malformed line that doesn't contain at least one space
                continue

            if base_prefix and path_part.startswith(base_prefix):
                rel_path = path_part[len(base_prefix):]
            else:
                rel_path = path_part

            # Strip leading slash if present
            rel_path = rel_path.lstrip("/\\")

            # Convert backslashes to forward slashes
            rel_path = rel_path.replace("\\", "/")

            mapping[rel_path] = txid_part
    return mapping

def process_index_html(html_path, file_map):
    """
    Parses a single index.html file, finds all <source> tags within <audio> tags,
    and replaces the 'src' with the corresponding 'https://permagate.io/<dataTxId>'.
    """

    folder_name = os.path.basename(os.path.dirname(html_path))
    is_subfolder_numeric = folder_name.isdigit()

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    changed = False
    for audio_tag in soup.find_all("audio"):
        for source_tag in audio_tag.find_all("source"):
            src_value = source_tag.get("src", "").strip()
            if not src_value:
                continue

            # Attempt a direct lookup in file_map
            decoded_src = urllib.parse.unquote(src_value)
            stripped_src = decoded_src.lstrip("/\\")
            data_tx_id = file_map.get(stripped_src)

            if not data_tx_id and is_subfolder_numeric:
                candidate = f"{folder_name}/{decoded_src.lstrip('/\\')}"
                data_tx_id = file_map.get(candidate)

            if data_tx_id:
                print(f"Replacing {stripped_src} -> {data_tx_id}")
                new_src = f"https://permagate.io/{data_tx_id}"
                source_tag["src"] = new_src
                changed = True

    if changed:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

def main():
    parser = argparse.ArgumentParser(
        description="Update <audio><source> tags in index.html to point to https://permagate.io/<dataTxId> from ArDrive or a local dictionary."
    )
    parser.add_argument("local_folder", help="Local folder where we search for index.html files")
    parser.add_argument("ardrive_folder_id", nargs="?", default=None,
                        help="ArDrive folder ID to fetch (list-files) data from (optional if --dictionary is used)")
    parser.add_argument("--base-prefix", default=None,
                        help="If your file paths all start with a prefix like '/Aurora Compilations/aurora-2025-threshold', specify it here to strip it out.")
    parser.add_argument("--dictionary", default=None,
                        help="Path to a dictionary text file (two columns: path dataTxId). If provided, we'll skip ArDrive fetching and use this mapping.")

    args = parser.parse_args()

    if not os.path.isdir(args.local_folder):
        print(f"Error: '{args.local_folder}' is not a valid directory.")
        return

    # If a dictionary file is provided, parse it.
    # Otherwise, if we have an ardrive_folder_id, fetch data from ArDrive.
    # If neither is provided, we can't proceed.
    if args.dictionary:
        print(f"Using dictionary file: {args.dictionary}")
        if not os.path.isfile(args.dictionary):
            print(f"Error: dictionary file '{args.dictionary}' not found.")
            return

        file_map = parse_dictionary_file(args.dictionary, base_prefix=args.base_prefix)
        print(f"Built a file map from dictionary with {len(file_map)} entries.")

    else:
        # We expect an ardrive_folder_id in this case
        if not args.ardrive_folder_id:
            print("Error: you must provide either --dictionary or ardrive_folder_id.")
            return

        print(f"Fetching file data for folder ID: {args.ardrive_folder_id}")
        file_data = fetch_ardrive_data(args.ardrive_folder_id)
        print(f"Retrieved {len(file_data)} JSON entries from ArDrive.")

        file_map = build_file_map(file_data, base_prefix=args.base_prefix)
        print(f"Built a file map with {len(file_map)} entries.")

    # Find and process all 'index.html' in local_folder
    index_html_paths = []
    for root, dirs, files in os.walk(args.local_folder):
        for name in files:
            if name.lower() == "index.html":
                index_html_paths.append(os.path.join(root, name))

    print(f"Found {len(index_html_paths)} index.html file(s) to process.")
    for html_file in index_html_paths:
        print(f"Processing {html_file} ...")
        process_index_html(html_file, file_map)
        print("Done.")

if __name__ == "__main__":
    main()
