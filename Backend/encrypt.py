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
import psutil
import numpy as np
from scipy.stats import entropy
from collections import Counter

# Handle both relative and absolute imports
try:
    from .scanner import scan_for_files, generate_key, save_key, drop_ransom_notes, _verify_safety_path, SAFE_ZONE_NAME
except ImportError:
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from scanner import scan_for_files, generate_key, save_key, drop_ransom_notes, _verify_safety_path, SAFE_ZONE_NAME

# Configuration from scanner.py
ENCRYPTED_DIRNAME = "encrypted"
KEYFILE_NAME = "sim_key.bin"
TEST_MODE = True

def _calculate_entropy(data: bytes) -> float:
    """Calculate the entropy of a byte string."""
    if not data:
        return 0.0
    value, counts = np.unique(list(data), return_counts=True)
    return entropy(counts, base=2)

def encrypt_file_aesgcm(src: Path, dest: Path, key: bytes):
    """Encrypt src -> dest using AES-GCM."""
    if not _verify_safety_path(src) or not _verify_safety_path(dest):
        raise PermissionError(f"Operation denied: Path is outside the '{SAFE_ZONE_NAME}' directory.")
    
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    data = src.read_bytes()
    ct = aesgcm.encrypt(nonce, data, associated_data=None)
    dest.write_bytes(nonce + ct)
    return data # Return original data for metrics

def encrypt_file_rsa(src: Path, dest: Path, key: bytes):
    """Encrypt src -> dest using RSA hybrid encryption."""
    if not _verify_safety_path(src) or not _verify_safety_path(dest):
        raise PermissionError(f"Operation denied: Path is outside the '{SAFE_ZONE_NAME}' directory.")

    aes_key = secrets.token_bytes(32)
    public_key = serialization.load_pem_public_key(key)
    
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    aesgcm = AESGCM(aes_key)
    nonce = secrets.token_bytes(12)
    data = src.read_bytes()
    ciphertext = aesgcm.encrypt(nonce, data, None)
    
    key_length = len(encrypted_key).to_bytes(4, byteorder='big')
    dest.write_bytes(key_length + encrypted_key + nonce + ciphertext)
    return data

def encrypt_file_chacha20(src: Path, dest: Path, key: bytes):
    """Encrypt src -> dest using ChaCha20-Poly1305."""
    if not _verify_safety_path(src) or not _verify_safety_path(dest):
        raise PermissionError(f"Operation denied: Path is outside the '{SAFE_ZONE_NAME}' directory.")

    chacha = ChaCha20Poly1305(key)
    nonce = secrets.token_bytes(12)
    data = src.read_bytes()
    ct = chacha.encrypt(nonce, data, associated_data=None)
    dest.write_bytes(nonce + ct)
    return data

def ensure_encrypted_dir(root: Path):
    """Create and return the encrypted directory."""
    enc_dir = root / ENCRYPTED_DIRNAME
    enc_dir.mkdir(parents=True, exist_ok=True)
    return enc_dir

def _call_generate_key_safely(algorithm):
    """Call scanner.generate_key handling both 0-arg and 1-arg signatures."""
    try:
        sig = inspect.signature(generate_key)
        params = sig.parameters
        if len(params) >= 1:
            return generate_key(algorithm)
        else:
            return generate_key()
    except Exception:
        try:
            return generate_key(algorithm)
        except TypeError:
            return generate_key()

def simulate_encrypt_folder(folder: str, test_mode=True, algorithm: str = "AES", stop_event: threading.Event = None, progress_callback=None, allowed_ext=None, drop_ransom_note: bool = False, ransom_note_content: str = ""):
    """Simulate encrypting files and return detailed metrics."""
    root = Path(folder).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError("Folder path invalid")

    if not _verify_safety_path(root):
        raise PermissionError(f"Operation denied: The path '{root}' is outside the designated '{SAFE_ZONE_NAME}' directory.")

    if not test_mode:
        print("WARNING: test_mode is False. This can modify files! Aborting by default for safety.")
        return None

    enc_dir = ensure_encrypted_dir(root)
    key_path = enc_dir / KEYFILE_NAME

    if drop_ransom_note and ransom_note_content:
        drop_ransom_notes(root, ransom_note_content)

    try:
        key = _call_generate_key_safely(algorithm)
    except Exception as e:
        print(f"[Error] generate_key failed: {e}")
        return None
    save_key(key, key_path)
    print(f"Encryption key saved to: {key_path}")

    files = list(scan_for_files(root, allowed_ext=allowed_ext))
    total_files = len(files)
    print(f"Found {total_files} target files to encrypt.")

    # Metrics Initialization
    process = psutil.Process(os.getpid())
    start_ts = time.time()
    cpu_usages = []
    mem_usages = []
    total_bytes_processed = 0
    file_sizes = []
    file_types = []
    entropy_before = []
    entropy_after = []
    done = 0
    failed_files = 0

    if callable(progress_callback):
        progress_callback(0, total_files, 0.0)

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
    for i, f in enumerate(files):
        if stop_event is not None and stop_event.is_set():
            print("Encryption cancelled by user.")
            break

        rel = f.relative_to(root)
        dest = enc_dir / (str(rel).replace(os.sep, "__") + ".encrypted")
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Record metrics per file
            cpu_usages.append(process.cpu_percent())
            mem_usages.append(process.memory_info().rss)
            
            file_size = f.stat().st_size
            file_sizes.append(file_size)
            total_bytes_processed += file_size
            file_types.append(f.suffix.lower() if f.suffix else ".none")

            original_data = f.read_bytes()
            entropy_before.append(_calculate_entropy(original_data))
            
            encrypt_fn(f, dest, key)
            
            encrypted_data = dest.read_bytes()
            entropy_after.append(_calculate_entropy(encrypted_data))

            done += 1
            elapsed = time.time() - start_ts
            print(f"-> {dest}")
            if callable(progress_callback):
                progress_callback(done, total_files, elapsed)
        except Exception as e:
            failed_files += 1
            print(f"Failed to encrypt {f}: {e}")

    elapsed = time.time() - start_ts

    # Final Metrics Calculation
    encryption_speed = done / elapsed if elapsed > 0 else 0
    throughput = (total_bytes_processed / (1024 * 1024)) / elapsed if elapsed > 0 else 0
    avg_file_size = np.mean(file_sizes) if file_sizes else 0
    peak_cpu_usage = max(cpu_usages) if cpu_usages else 0
    peak_mem_overhead = (max(mem_usages) - mem_usages[0]) / (1024*1024) if mem_usages else 0
    avg_entropy_increase = np.mean(np.array(entropy_after) - np.array(entropy_before)) if entropy_before else 0
    survival_rate = (failed_files / total_files) * 100 if total_files > 0 else 0
    
    file_type_counts = Counter(file_types)
    file_type_distribution = {ft: (count / total_files) * 100 for ft, count in file_type_counts.items()} if total_files > 0 else {}

    print("\nSimulation complete. Originals remain unchanged.")
    
    simulation_metrics = {
        "algorithm": algorithm,
        "elapsed_time": elapsed,
        "total_files": total_files,
        "encrypted_files": done,
        "failed_files": failed_files,
        "encryption_speed_fps": encryption_speed,
        "throughput_mbps": throughput,
        "average_file_size_bytes": avg_file_size,
        "peak_cpu_usage_pct": peak_cpu_usage,
        "peak_memory_overhead_mb": peak_mem_overhead,
        "average_entropy_increase": avg_entropy_increase,
        "survival_rate_pct": survival_rate,
        "file_type_distribution_pct": file_type_distribution
    }

    return simulation_metrics

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python encrypt.py <sandbox_folder> [--algorithm=ALGO] [--all-files]")
        sys.exit(1)
    
    folder = sys.argv[1]
    algorithm = "AES"
    all_files_mode = False
    
    for arg in sys.argv[2:]:
        if arg.startswith("--algorithm="):
            algorithm = arg.split("=")[1].strip()
        elif arg == "--all-files":
            all_files_mode = True
    
    # Get ALLOWED_EXT from scanner module
    from scanner import ALLOWED_EXT as DEFAULT_EXT
    allowed_ext = None if all_files_mode else DEFAULT_EXT
    
    metrics = simulate_encrypt_folder(folder, test_mode=TEST_MODE, algorithm=algorithm, allowed_ext=allowed_ext)
    
    if metrics:
        print("\n--- Simulation Metrics ---")
        for key, value in metrics.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  - {sub_key}: {sub_value:.2f}%")
            elif isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
        print("--------------------------")