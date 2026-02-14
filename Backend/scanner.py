# safe_ransomware_simulator_scanner.py
import os
# import sys
# import json
# import shutil
from pathlib import Path
from getpass import getpass
from time import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import base64
try:
    from .safe_zone import _verify_safety_path, SAFE_ZONE_NAME
except ImportError:
    from safe_zone import _verify_safety_path, SAFE_ZONE_NAME

# ---------- Configuration ----------
ALLOWED_EXT = {'.txt', '.pdf', '.docx', '.png', '.jpg'}   # file types to target
ENCRYPTED_DIRNAME = "encrypted"   # encrypted copies placed here (inside chosen folder)
KEYFILE_NAME = "sim_key.bin"      # saved in same folder as encrypted copies
TEST_MODE = True                  # SAFE DEFAULT: True => creates copies in encrypted/, keeps originals
# -----------------------------------

def generate_key():
    """Generate a random 32-byte key for AES-256-GCM."""
    return AESGCM.generate_key(bit_length=256)

def save_key(key: bytes, path: Path):
    """Save key bytes (base64) to a file - simple storage for simulator."""
    path.write_bytes(base64.b64encode(key))

def load_key(path: Path) -> bytes:
    return base64.b64decode(path.read_bytes())

def scan_for_files(root: Path, allowed_ext: set = ALLOWED_EXT):
    """
    Args:
        root (Path): The starting directory for the scan.
        allowed_ext (set): A set of lowercase file extensions to target.
                        If None, all files are yielded.
    
    Raises:
        PermissionError: If the root path is outside the designated safe zone.
    """
    # CRITICAL SAFETY CHECK: Ensure the operation is within the safe zone.
    if not _verify_safety_path(root):
        raise PermissionError(f"Operation denied: The path '{root}' is outside the designated '{SAFE_ZONE_NAME}' directory.")

    for dirpath, _, filenames in os.walk(root):
        # Skip the encrypted directory to avoid re-encrypting copies
        if ENCRYPTED_DIRNAME in Path(dirpath).parts:
            continue
        
        for fname in filenames:
            fpath = Path(dirpath) / fname
            # If allowed_ext is None, accept all files; otherwise, check extension
            if allowed_ext is None or fpath.suffix.lower() in allowed_ext:
                print(f"Found file: {fname} in (./{os.path.relpath(dirpath, root)})")
                yield fpath



def drop_ransom_notes(root: Path, ransom_note_content: str):
    # CRITICAL SAFETY CHECK: Ensure the operation is within the safe zone.
    if not _verify_safety_path(root):
        raise PermissionError(f"Operation denied: The path '{root}' is outside the designated '{SAFE_ZONE_NAME}' directory.")

    visited_dirs = set()
    for dirpath, _, _ in os.walk(root):
        # Skip the encrypted directory
        if ENCRYPTED_DIRNAME in Path(dirpath).parts:
            continue
        
        # Create README.txt in this directory if not already visited
        if dirpath not in visited_dirs:
            readme_path = Path(dirpath) / "README.txt"
            try:
                # Final safety check on the exact file path before writing
                if not _verify_safety_path(readme_path):
                    print(f"Skipped dropping ransom note at unauthorized path: {readme_path}")
                    continue
                
                readme_path.write_text(ransom_note_content)
                print(f"Dropped ransom note: {readme_path}")
                visited_dirs.add(dirpath)
            except Exception as e:
                print(f"Failed to drop ransom note in {dirpath}: {e}")


# Note: This script is for educational purposes only. Always ensure you have backups of important data.