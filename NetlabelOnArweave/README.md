# Overview

This repository demonstrates how to replicate the Aurora Compilations netlabel - built with Faircamp - for learning purposes. The guide provides the complete workflow for setting up and releasing music on Arweave.

# Prerequisites

* Faircamp, version 1.2 or higher.
* Python: see `requirements.txt` for dependencies.
* Release materials: mastered and tagged FLAC files and cover artwork, provided both as separate files and bundled in a ZIP per release.
* ArDrive wallet with sufficient AR or Turbo tokens.
* Internet Archive account.

# Workflow

1. Unzip the `AuroraSkeleton1.zip` and `AuroraSkeleton2.zip` files into a folder of your choice.
2. Replace the `music.placeholder` files in each folder (e.g., `Compilations/02. Aurora 2024 - Reflect And Improve/music.placeholder`) with the actual FLAC files available via the label's website.
3. New release setup:
   * Create a new folder for the release (e.g., `Compilations/22. Aurora 2027 - New Black Gold`).
   * Add mastered and tagged FLAC files along with cover artwork (as `Cover.png` and embedded in the files).
   * Add and modify `release.eno` accordingly (it’s easiest to copy the previous release’s `release.eno` into the folder and adjust it per your needs). Refer to the Faircamp documentation for further options.
   * Upload the ZIP file(s) to both ArDrive and Internet Archive.
   * Update the links in `release.eno`: `release_download_access:` tag for ArDrive, `link:` tag for Internet Archive. Upload an MP3 reel/preview to Internet Archive.
4. Run Faircamp: `faircamp --no-clean-urls`
