import os
import random
import string
from pathlib import Path
from typing import Union

# Define the safe directory name
SAFE_ZONE_NAME = "Ransomware_Test"
SAFE_ZONE_PATH = Path(os.getcwd()) / SAFE_ZONE_NAME

def _verify_safety_path(path: Union[str, Path]) -> bool:
    """
    Verifies that the given path is strictly within the SAFE_ZONE_PATH.

    Args:
        path: The file or directory path to verify.

    Returns:
        True if the path is within the safe zone, False otherwise.
    """
    try:
        # Resolve the path to an absolute path to prevent traversal attacks (e.g., ../)
        resolved_path = Path(path).resolve()
        # Check if the resolved path is a subpath of the safe zone
        return SAFE_ZONE_PATH.resolve() in resolved_path.parents or resolved_path == SAFE_ZONE_PATH.resolve()
    except Exception as e:
        print(f"Error during path verification: {e}")
        return False

def populate_safe_zone():
    """
    Creates a realistic directory structure with dummy files inside the SAFE_ZONE_PATH.
    """
    if not _verify_safety_path(SAFE_ZONE_PATH):
        print(f"Safety check failed: Cannot populate outside of {SAFE_ZONE_PATH.resolve()}")
        return

    SAFE_ZONE_PATH.mkdir(exist_ok=True)

    # A more realistic file structure
    structure = {
        "Documents": {
            "Work": ["report.docx", "presentation.pptx", "data.xlsx"],
            "Personal": ["resume.pdf", "letter.txt"],
        },
        "Images": {
            "Vacation": ["photo1.jpg", "photo2.jpg", "photo3.png"],
            "Family": ["family_gathering.jpg"],
        },
        "Projects": {
            "Project_Alpha": ["main.py", "utils.py", "requirements.txt"],
            "Project_Beta": ["index.html", "style.css", "script.js"],
        },
        "Archives": ["backup_2023.zip", "old_files.tar.gz"],
    }

    # Lorem ipsum text for dummy content
    lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."

    def create_files(base_path, items):
        for item in items:
            if isinstance(items, dict):
                dir_path = base_path / item
                dir_path.mkdir(exist_ok=True)
                create_files(dir_path, items[item])
            else:
                file_path = base_path / item
                try:
                    if file_path.suffix.lower() in ['.txt', '.html', '.css', '.js', '.py']:
                        file_path.write_text(lorem_ipsum, encoding='utf-8')
                    elif file_path.suffix.lower() in ['.jpg', '.png']:
                        # Create a small random image-like file
                        file_path.write_bytes(os.urandom(random.randint(1024, 4096)))
                    else:
                        # For other files, just write some random bytes
                        file_path.write_bytes(os.urandom(random.randint(100, 512)))
                except IOError as e:
                    print(f"Failed to create dummy file {file_path}: {e}")

    create_files(SAFE_ZONE_PATH, structure)
    print("\nSafe zone population complete.")

if __name__ == "__main__":
    print("Populating the safe zone with dummy files and folders...")
    populate_safe_zone()
    print("\nVerification test:")
    print(f"Is '{SAFE_ZONE_PATH}' safe? -> {_verify_safety_path(SAFE_ZONE_PATH)}")
    print(f"Is '{SAFE_ZONE_PATH / 'Documents'}' safe? -> {_verify_safety_path(SAFE_ZONE_PATH / 'Documents')}")
    print(f"Is '{Path.cwd()}' safe? -> {_verify_safety_path(Path.cwd())}")
    print(f"Is '{Path.cwd().parent}' safe? -> {_verify_safety_path(Path.cwd().parent)}")
