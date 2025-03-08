# Overview

This repository demonstrates how to replicate the [Aurora Compilations](https://aurora-compilations.org) netlabel - built with [Faircamp](https://simonrepp.com/faircamp) - for learning purposes. The guide provides the complete workflow for setting up a netlabel and releasing music using a combination of [Arweave](https://arweave.org) and Faircamp. If you're already familiar with generating a Faircamp static website and want to substitute Aurora Compilations website with your own website (most likely), you can skip ahead to step 4 in the workflow. The first three steps are specifically tailored to the Aurora Compilations setup.

# Prerequisites

* Faircamp, version 1.2 or higher.
* Python: see `requirements.txt` for dependencies (`pip install -r path/to/requirements.txt`).
* Mastered and tagged FLAC files and cover artwork, provided both as separate files and bundled in a ZIP per release.
* [ArDrive](https://ardrive.io) CLI.
* Arweave wallet with sufficient AR or Turbo tokens.
* (Optional, Aurora-only) [Internet Archive](https://archive.org) account.

# Workflow

1. Unzip the `AuroraSkeleton1.zip` and `AuroraSkeleton2.zip` files into a folder of your choice.
2. Replace the `music.placeholder` files in each folder (e.g., `Compilations/02. Aurora 2024 - Reflect And Improve/music.placeholder`) with the actual FLAC files available via the label's website.
3. New release setup:
   * Create a new folder for the release (e.g., `Compilations/22. Aurora 2027 - New Black Gold`).
   * Add mastered and tagged FLAC files along with cover artwork (provided as `Cover.png` and embedded in the files).
   * Add and modify `release.eno` accordingly. It’s easiest to copy the previous release’s `release.eno` into the folder and adjust it as needed (refer to [the Faircamp manual](https://simonrepp.com/faircamp/manual) for further options).
   * Run `01.py` on all your ZIP files (`python 01.py file.zip`). This script checks whether the files conform to the standards; proceed only if there are no errors.
   * Upload the ZIP file(s) to both ArDrive and Internet Archive.
   * Update the links in `release.eno`: `release_download_access:` tag for ArDrive, `link:` tag for Internet Archive.
   * Upload an MP3 reel/preview to Internet Archive.
4. Run Faircamp: `faircamp --no-clean-urls`. You should get a folder `.faircamp_build`. Rename this folder to `build`.
5. (Optional, Aurora-only) Run `02.py` to adjust HTML alignment and headers (`python 02.py /path/to/build`).
6. Upload `build` contents to ArDrive:
   * For a new release, upload only the contents of the `build` root and the corresponding release folder (e.g., `aurora-2027-new-black-gold`).
   * If you’ve added an artist other than "Various Artists" (for Aurora), upload the corresponding artist folder as well. ArDrive's Turbo feature allows free uploads of small files, making it easy to update static website content as needed.
7. Ensure that all files are uploaded correctly - they should appear lit green in ArDrive. Do not proceed until you are sure.
8. Run `03.py` to fetch Arweave transactions from ArDrive and match them with the relative paths in the static website:
   * This step is critical for enabling correct music playback: `python 03.py build/aurora-2027-new-black-gold ardrive-folder-id --base-prefix '/Aurora Compilations/aurora-2027-new-black-gold'`.
   * Change the variable `ARDRIVE_BIN` before running the script.
   * If you provide `--dictionary /path/to/dictionary.txt`, the script will skip ArDrive fetching.
10. (Optional) If you notice that the Arweave gateway is down, run `05.py` to change the gateway name in either the `build` folder or in the Faircamp manifests.
11. Verify that everything works correctly in the `build` folder.
12. Upload the changed files (all `index.html` files) from the `build` folder to ArDrive.
13. Generate the Arweave manifest for the drive you are using on ArDrive. Preview the manifest to ensure your website is functioning correctly. If you use a Deno script as a proxy to map your domain name to Arweave (see [Permaweb Cookbook](https://cookbook.arweave.dev)), update the transaction ID in that script with the transaction ID of the newly generated manifest.

These steps complete the workflow, ensuring that your Faircamp website is properly built, verified, and deployed on Arweave.
