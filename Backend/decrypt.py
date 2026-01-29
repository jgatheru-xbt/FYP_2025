# decrypt_simulated.py
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
try:
    from .safe_zone import _verify_safety_path, SAFE_ZONE_NAME
except ImportError:
    from safe_zone import _verify_safety_path, SAFE_ZONE_NAME

ENCRYPTED_DIRNAME = "encrypted"
DECRYPTED_DIRNAME = "decrypted"
KEYFILE_NAME = "sim_key.bin"

def decrypt_file(enc_path: Path, out_path: Path, key: bytes):
    """
    Decrypts a file after verifying that both source and destination paths are
    safely within the designated test directory.
    """
    # CRITICAL SAFETY CHECK: Do not operate outside the safe zone.
    if not _verify_safety_path(enc_path) or not _verify_safety_path(out_path):
        raise PermissionError(f"Operation denied: Path is outside the '{SAFE_ZONE_NAME}' directory.")

    data = enc_path.read_bytes()
    nonce = data[:12]
    ct = data[12:]
    aesgcm = AESGCM(key)
    pt = aesgcm.decrypt(nonce, ct, associated_data=None)
    out_path.write_bytes(pt)

def batch_decrypt(encrypted_dir: str):
    root = Path(encrypted_dir).resolve()

    # CRITICAL SAFETY CHECK: Ensure the operation is within the safe zone.
    if not _verify_safety_path(root):
        raise PermissionError(f"Operation denied: The path '{root}' is outside the designated '{SAFE_ZONE_NAME}' directory.")

    key_path = root / KEYFILE_NAME
    if not key_path.exists():
        raise FileNotFoundError("Key file not found")
    key = base64.b64decode(key_path.read_bytes())
    dec_dir = root.parent / DECRYPTED_DIRNAME
    dec_dir.mkdir(parents=True, exist_ok=True)

    for enc_file in root.glob("*.encrypted"):
        out_file = dec_dir / (enc_file.stem + ".restored")
        try:
            decrypt_file(enc_file, out_file, key)
            print(f"Decrypted: {enc_file} -> {out_file}")
        except Exception as e:
            print(f"Failed to decrypt {enc_file}: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python decrypt_simulated.py <path_to_encrypted_dir>")
        sys.exit(1)
    batch_decrypt(sys.argv[1])
