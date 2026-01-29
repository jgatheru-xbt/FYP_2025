import os
import sys
from pathlib import Path
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization, hashes
import secrets
import threading
import inspect

# Handle both relative and absolute imports
# Try relative import first (when run as module), fall back to sys.path (when run as script)
try:
    from .scanner import scan_for_files, generate_key, save_key, drop_ransom_notes, _verify_safety_path, SAFE_ZONE_NAME
except ImportError:
    # Add Backend directory to path so we can import scanner directly
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from scanner import scan_for_files, generate_key, save_key, drop_ransom_notes, _verify_safety_path, SAFE_ZONE_NAME

# Configuration from scanner.py
ENCRYPTED_DIRNAME = "encrypted"
KEYFILE_NAME = "sim_key.bin"
TEST_MODE = True

def encrypt_file_aesgcm(src: Path, dest: Path, key: bytes):
    """
    Encrypt src -> dest using AES-GCM, after verifying paths are safe.
    dest will contain: nonce(12) + ciphertext + tag (all binary).
    """
    # CRITICAL SAFETY CHECK: Do not operate outside the safe zone.
    if not _verify_safety_path(src) or not _verify_safety_path(dest):
        raise PermissionError(f"Operation denied: Path is outside the '{SAFE_ZONE_NAME}' directory.")
    
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    data = src.read_bytes()
    ct = aesgcm.encrypt(nonce, data, associated_data=None)
    # write nonce + ciphertext (ct already includes tag)
    dest.write_bytes(nonce + ct)

def encrypt_file_rsa(src: Path, dest: Path, key: bytes):
    """
    Encrypt src -> dest using RSA hybrid encryption, after verifying paths are safe.
    dest will contain: encrypted_key_length(4) + encrypted_key + nonce(12) + ciphertext
    """
    # CRITICAL SAFETY CHECK: Do not operate outside the safe zone.
    if not _verify_safety_path(src) or not _verify_safety_path(dest):
        raise PermissionError(f"Operation denied: Path is outside the '{SAFE_ZONE_NAME}' directory.")

    # Generate random AES key for actual file encryption
    aes_key = secrets.token_bytes(32)
    
    # Load RSA public key from bytes
    public_key = serialization.load_pem_public_key(key)
    
    # Encrypt the AES key with RSA
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Encrypt file content with AES-GCM
    aesgcm = AESGCM(aes_key)
    nonce = secrets.token_bytes(12)
    data = src.read_bytes()
    ciphertext = aesgcm.encrypt(nonce, data, None)
    
    # Write everything to destination
    key_length = len(encrypted_key).to_bytes(4, byteorder='big')
    dest.write_bytes(key_length + encrypted_key + nonce + ciphertext)

def encrypt_file_chacha20(src: Path, dest: Path, key: bytes):
    """
    Encrypt src -> dest using ChaCha20-Poly1305, after verifying paths are safe.
    dest will contain: nonce(12) + ciphertext + tag (16 bytes).
    """
    # CRITICAL SAFETY CHECK: Do not operate outside the safe zone.
    if not _verify_safety_path(src) or not _verify_safety_path(dest):
        raise PermissionError(f"Operation denied: Path is outside the '{SAFE_ZONE_NAME}' directory.")

    chacha = ChaCha20Poly1305(key)
    nonce = secrets.token_bytes(12)
    data = src.read_bytes()
    ct = chacha.encrypt(nonce, data, associated_data=None)
    
    # Write nonce + ciphertext (includes tag)
    dest.write_bytes(nonce + ct)

def ensure_encrypted_dir(root: Path):
    """Create and return the encrypted directory."""
    enc_dir = root / ENCRYPTED_DIRNAME
    enc_dir.mkdir(parents=True, exist_ok=True)
    return enc_dir

def _call_generate_key_safely(algorithm):
    """
    Call scanner.generate_key handling both 0-arg and 1-arg signatures.
    """
    try:
        sig = inspect.signature(generate_key)
        params = sig.parameters
        if len(params) >= 1:
            return generate_key(algorithm)
        else:
            return generate_key()
    except Exception:
        # last-resort attempt: try both calling patterns
        try:
            return generate_key(algorithm)
        except TypeError:
            return generate_key()

def simulate_encrypt_folder(folder: str, test_mode=True, algorithm: str = "AES", stop_event: threading.Event = None, progress_callback=None, allowed_ext=None, drop_ransom_note: bool = False, ransom_note_content: str = ""):
    """
    Simulate encrypting files in `folder`. algorithm: "AES", "RSA", or "ChaCha20".
    stop_event (threading.Event) can be used to cancel the operation from another thread.
    progress_callback(done:int, total:int, elapsed:float) -> None : optional callback to report progress.
    allowed_ext: set of extensions to target (e.g. {'.txt', '.pdf'}), or None for all files.
    drop_ransom_note: if True, drop ransom note files in all directories.
    ransom_note_content: the content of the ransom note to drop.
    """
    root = Path(folder).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError("Folder path invalid")

    # CRITICAL SAFETY CHECK: Ensure the root folder is within the safe zone.
    if not _verify_safety_path(root):
        raise PermissionError(f"Operation denied: The path '{root}' is outside the designated '{SAFE_ZONE_NAME}' directory.")

    # safety confirmation (unless test_mode is False and you supplied a special flag)
    if not test_mode:
        print("WARNING: test_mode is False. This can modify files! Aborting by default for safety.")
        return

    enc_dir = ensure_encrypted_dir(root)
    key_path = enc_dir / KEYFILE_NAME

    # Drop ransom notes if requested
    if drop_ransom_note and ransom_note_content:
        drop_ransom_notes(root, ransom_note_content)

    # generate key and save (call safely)
    try:
        key = _call_generate_key_safely(algorithm)
    except Exception as e:
        print(f"[Error] generate_key failed: {e}")
        return

    save_key(key, key_path)
    print(f"Encryption key saved to: {key_path}")

    # Pass allowed_ext to scan_for_files
    files = list(scan_for_files(root, allowed_ext=allowed_ext))
    total_files = len(files)
    print(f"Found {total_files} target files to encrypt (copies).")

    # report initial progress (0 done)
    start_ts = time.time()
    try:
        if callable(progress_callback):
            progress_callback(0, total_files, 0.0)
    except Exception:
        pass

    # choose encryption function
    algo = algorithm.lower()
    if algo.startswith("aes"):
        encrypt_fn = encrypt_file_aesgcm
    elif algo.startswith("rsa"):
        encrypt_fn = encrypt_file_rsa
    elif "chacha" in algo:
        encrypt_fn = encrypt_file_chacha20
    else:
        print(f"[Error] Unknown algorithm '{algorithm}', defaulting to AES-GCM.")
        encrypt_fn = encrypt_file_aesgcm

    print("Encrypted files:")
    done = 0
    for i, f in enumerate(files):
        # check for cancellation
        if stop_event is not None and stop_event.is_set():
            print("Encryption cancelled by user.")
            return

        rel = f.relative_to(root)
        dest = enc_dir / (str(rel).replace(os.sep, "__") + ".encrypted")
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            encrypt_fn(f, dest, key)
            done += 1
            elapsed = time.time() - start_ts
            print(f"-> {dest}")
            # report progress
            try:
                if callable(progress_callback):
                    progress_callback(done, total_files, elapsed)
            except Exception:
                pass
        except Exception as e:
            print(f"Failed to encrypt {f}: {e}")

    print("\nSimulation complete. Originals remain unchanged.")
    print(f"Encrypted copies are in: {enc_dir}")
    print("To decrypt, use the stored key file and the corresponding decrypt script.")



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python encrypt.py <sandbox_folder> [--algorithm=ALGO] [--all-files]")
        sys.exit(1)
    
    folder = sys.argv[1]
    algorithm = "AES"
    all_files_mode = False
    
    # Parse command line args
    for arg in sys.argv[2:]:
        if arg.startswith("--algorithm="):
            algorithm = arg.split("=")[1].strip()
        elif arg == "--all-files":
            all_files_mode = True
    
    start_time = time.time()
    # If --all-files is set, pass None (scan all files); otherwise pass default (ALLOWED_EXT from scanner)
    # Get ALLOWED_EXT from scanner module
    from scanner import ALLOWED_EXT as DEFAULT_EXT
    allowed_ext = None if all_files_mode else DEFAULT_EXT
    simulate_encrypt_folder(folder, test_mode=TEST_MODE, algorithm=algorithm, allowed_ext=allowed_ext)
    end_time = time.time()
    
    elapsed = end_time - start_time
    print(f"Total time taken: {elapsed:.3f} seconds ({int(elapsed * 1000)} ms)")