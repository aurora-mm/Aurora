import os
import sys
import re
from bs4 import BeautifulSoup

def update_html_file(file_path):
    """
    Opens the file at file_path, updates all <div class="text"> and <div class="abstract">
    to have text-align: justify, and removes (year) patterns from <h1> text.
    Writes changes back to the original file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Set text-align: justify for divs with class="text" or class="abstract"
    for div_tag in soup.find_all("div", class_=["text", "abstract"]):
        style_attr = div_tag.get("style", "")
        if "text-align:" in style_attr:
            style_attr = re.sub(r"text-align\s*:\s*[^;]+;", "text-align: justify;", style_attr)
        else:
            if style_attr.strip() and not style_attr.strip().endswith(";"):
                style_attr += ";"
            style_attr += " text-align: justify;"

        div_tag["style"] = style_attr.strip()

    # Remove (YYYY) from the text of all <h1> tags
    for h1_tag in soup.find_all("h1"):
        original_text = h1_tag.get_text()
        updated_text = re.sub(r"\(\d{4}\)", "", original_text)
        updated_text = re.sub(r"\s+", " ", updated_text).strip()
        h1_tag.string = updated_text

    # Write changes back to the same file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(soup))


def process_html_in_folder(folder_path):
    """
    Walks the folder_path recursively, and processes each .html file.
    """
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.lower().endswith(".html"):
                full_path = os.path.join(root, file_name)
                update_html_file(full_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_folder>")
        sys.exit(1)

    folder_path = sys.argv[1]
    process_html_in_folder(folder_path)

if __name__ == "__main__":
    main()
