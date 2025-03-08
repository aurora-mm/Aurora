import argparse
import re

def remove_cover_references(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"^\s*cover:\s*'[^']*',?\s*$", re.MULTILINE)
    new_content = pattern.sub("", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    parser = argparse.ArgumentParser(
        description="Remove all cover: references from a browser.js file."
    )
    parser.add_argument("browser_js_path", help="Path to browser.js")
    args = parser.parse_args()

    remove_cover_references(args.browser_js_path)
    print(f"Removed cover references from {args.browser_js_path}")

if __name__ == "__main__":
    main()
