import os

def update_files(folder, old_gateway="https://permagate.io/"):
    # Prompt the user to enter the desired gateway.
    desired_gateway = input("Enter the desired gateway (e.g., https://your-gateway.example/): ").strip()

    # Walk through the folder recursively.
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".html") or file.endswith(".eno"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if old_gateway in content:
                    updated_content = content.replace(old_gateway, desired_gateway)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(updated_content)
                    print(f"Updated {filepath}")


def main():
    folder = input("Enter the folder path to process: ").strip()
    if not os.path.isdir(folder):
        print("Invalid folder path. Exiting.")
        return
    update_files(folder)

if __name__ == "__main__":
    main()
