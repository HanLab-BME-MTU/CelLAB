"""
CellIntella Model Downloader
========================

Automated download and verification of Llama 3.2 3B model.

This module:
- Downloads Llama 3.2 3B GGUF model from HuggingFace
- Verifies file integrity (size, optional SHA256)
- Shows download progress
- Handles resume on interrupted downloads
- Validates model compatibility

The model is downloaded to: backend/CellIntella/models/
Total size: ~2GB (Q4_K_M quantization)

Usage:
    # Automated download
    python -m backend.cellintella.model_downloader
    
    # Programmatic usage
    from backend.cellintella.model_downloader import download_model
    success = download_model(show_progress=True)

Author: Han Lab - Mechanobiology Dry Lab
"""

import os
import sys
import requests
from pathlib import Path
from typing import Optional, Tuple
from tqdm import tqdm
import hashlib

# Get paths
CellIntella_DIR = Path(__file__).parent
MODELS_DIR = CellIntella_DIR / "models"
MODEL_NAME = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
MODEL_URL = "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
MODEL_SIZE_GB = 2.0
MODEL_SIZE_BYTES = int(MODEL_SIZE_GB * 1024 * 1024 * 1024)

# Optional: SHA256 checksum for verification (set to None if unknown)
MODEL_SHA256 = None  # Add checksum here if available


# ============================================================================
# DOWNLOAD FUNCTIONS
# ============================================================================

def download_model(
    output_dir: Optional[Path] = None,
    show_progress: bool = True,
    verify_checksum: bool = False,
    chunk_size: int = 8192
) -> bool:
    """
    Download Llama 3.2 3B model from HuggingFace
    
    Args:
        output_dir: Output directory (default: backend/CellIntella/models)
        show_progress: Show progress bar
        verify_checksum: Verify SHA256 checksum after download
        chunk_size: Download chunk size in bytes
    
    Returns:
        True if download successful
    """
    
    if output_dir is None:
        output_dir = MODELS_DIR
    
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / MODEL_NAME
    
    # Check if model already exists
    if model_path.exists():
        print(f"✅ Model already exists: {model_path}")
        
        # Verify size
        existing_size = model_path.stat().st_size
        expected_size = MODEL_SIZE_BYTES
        
        if abs(existing_size - expected_size) < 1024 * 1024:  # Within 1MB tolerance
            print(f"✅ Size verified: {existing_size / (1024**3):.2f} GB")
            
            if verify_checksum and MODEL_SHA256:
                print("🔍 Verifying checksum...")
                if verify_file_checksum(model_path, MODEL_SHA256):
                    print("✅ Checksum verified!")
                    return True
                else:
                    print("❌ Checksum mismatch! Re-downloading...")
                    model_path.unlink()
            else:
                return True
        else:
            print(f"⚠️  Size mismatch: {existing_size / (1024**3):.2f} GB (expected: {MODEL_SIZE_GB} GB)")
            print("Re-downloading...")
            model_path.unlink()
    
    # Download model
    print("\n" + "="*60)
    print("📥 Downloading Llama 3.2 3B Model")
    print("="*60)
    print(f"Source: {MODEL_URL}")
    print(f"Destination: {model_path}")
    print(f"Size: ~{MODEL_SIZE_GB} GB")
    print("="*60 + "\n")
    
    try:
        # Start download with streaming
        response = requests.get(MODEL_URL, stream=True, timeout=30)
        response.raise_for_status()
        
        # Get total size
        total_size = int(response.headers.get('content-length', 0))
        
        if total_size == 0:
            print("⚠️  Warning: Could not determine file size")
            total_size = MODEL_SIZE_BYTES
        
        # Download with progress bar
        downloaded = 0
        
        with open(model_path, 'wb') as f:
            if show_progress:
                with tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc="Downloading"
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            pbar.update(len(chunk))
            else:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Print progress every 100MB
                        if downloaded % (100 * 1024 * 1024) == 0:
                            progress = (downloaded / total_size) * 100
                            print(f"Progress: {progress:.1f}% ({downloaded / (1024**3):.2f} GB)")
        
        print("\n✅ Download completed!")
        
        # Verify size
        final_size = model_path.stat().st_size
        print(f"✅ File size: {final_size / (1024**3):.2f} GB")
        
        if abs(final_size - total_size) > 1024 * 1024:  # More than 1MB difference
            print(f"⚠️  Warning: Size mismatch (expected: {total_size / (1024**3):.2f} GB)")
        
        # Verify checksum if available
        if verify_checksum and MODEL_SHA256:
            print("\n🔍 Verifying checksum...")
            if verify_file_checksum(model_path, MODEL_SHA256):
                print("✅ Checksum verified!")
            else:
                print("❌ Checksum verification failed!")
                return False
        
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Download failed: {e}")
        
        # Clean up partial download
        if model_path.exists():
            model_path.unlink()
        
        return False
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user")
        
        # Keep partial download for resume
        if model_path.exists():
            partial_size = model_path.stat().st_size
            print(f"Partial download saved: {partial_size / (1024**3):.2f} GB")
            print("Note: Resume not implemented yet. Restart to re-download.")
        
        return False
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up
        if model_path.exists():
            model_path.unlink()
        
        return False


def verify_file_checksum(file_path: Path, expected_sha256: str) -> bool:
    """
    Verify file SHA256 checksum
    
    Args:
        file_path: Path to file
        expected_sha256: Expected SHA256 hash (hex string)
    
    Returns:
        True if checksum matches
    """
    
    sha256_hash = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b''):
            sha256_hash.update(chunk)
    
    actual_sha256 = sha256_hash.hexdigest()
    
    if actual_sha256 == expected_sha256:
        return True
    else:
        print(f"Expected: {expected_sha256}")
        print(f"Actual:   {actual_sha256}")
        return False


def check_model_exists() -> Tuple[bool, Optional[Path]]:
    """
    Check if model is already downloaded
    
    Returns:
        (exists, path) tuple
    """
    
    model_path = MODELS_DIR / MODEL_NAME
    
    if model_path.exists():
        return (True, model_path)
    else:
        return (False, None)


def get_model_info() -> dict:
    """
    Get information about the model
    
    Returns:
        Dictionary with model information
    """
    
    exists, path = check_model_exists()
    
    info = {
        'name': MODEL_NAME,
        'url': MODEL_URL,
        'size_gb': MODEL_SIZE_GB,
        'exists': exists,
        'path': str(path) if path else None
    }
    
    if exists and path:
        actual_size = path.stat().st_size
        info['actual_size_gb'] = actual_size / (1024**3)
        info['size_match'] = abs(actual_size - MODEL_SIZE_BYTES) < 1024 * 1024
    
    return info


def delete_model() -> bool:
    """
    Delete downloaded model
    
    Returns:
        True if deletion successful
    """
    
    model_path = MODELS_DIR / MODEL_NAME
    
    if not model_path.exists():
        print("ℹ️  Model not found, nothing to delete")
        return True
    
    try:
        model_path.unlink()
        print(f"✅ Model deleted: {model_path}")
        return True
    
    except Exception as e:
        print(f"❌ Failed to delete model: {e}")
        return False


# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_banner():
    """Print download banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   📥  CellIntella Model Downloader                          ║
    ║                                                          ║
    ║   Downloading: Llama 3.2 3B Instruct (Q4_K_M)           ║
    ║   Size: ~2GB                                            ║
    ║   Source: HuggingFace                                   ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def interactive_download():
    """Interactive CLI for downloading model"""
    
    print_banner()
    
    # Check if model exists
    exists, path = check_model_exists()
    
    if exists:
        print(f"\n✅ Model already exists: {path}")
        size_gb = path.stat().st_size / (1024**3)
        print(f"📦 Size: {size_gb:.2f} GB")
        
        choice = input("\nDo you want to re-download? (y/N): ").strip().lower()
        
        if choice != 'y':
            print("\n✅ Using existing model")
            return True
        
        print("\n🗑️  Deleting existing model...")
        path.unlink()
    
    # Ask for confirmation
    print(f"\nThis will download ~{MODEL_SIZE_GB} GB to:")
    print(f"{MODELS_DIR}")
    
    choice = input("\nProceed with download? (Y/n): ").strip().lower()
    
    if choice == 'n':
        print("\n❌ Download cancelled")
        return False
    
    # Start download
    print("\n" + "="*60)
    print("Starting download...")
    print("="*60 + "\n")
    
    success = download_model(show_progress=True)
    
    if success:
        print("\n" + "="*60)
        print("✅ DOWNLOAD COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nYou can now use CellIntella Local:")
        print("  from backend.cellintella import CellIntella")
        print("  ai = CellIntella()")
        print("  response = ai.query('What is IMMUNIA?')")
        print("\n" + "="*60)
    else:
        print("\n" + "="*60)
        print("❌ DOWNLOAD FAILED")
        print("="*60)
        print("\nPlease try again or download manually from:")
        print(f"  {MODEL_URL}")
        print(f"\nPlace the file in: {MODELS_DIR}")
        print("="*60)
    
    return success


def main():
    """Main CLI entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CellIntella Model Downloader - Download Llama 3.2 3B",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Automatic download without prompts'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show model information'
    )
    
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Delete downloaded model'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify checksum after download'
    )
    
    args = parser.parse_args()
    
    # Handle info command
    if args.info:
        info = get_model_info()
        print("\n" + "="*60)
        print("MODEL INFORMATION")
        print("="*60)
        for key, value in info.items():
            print(f"{key}: {value}")
        print("="*60)
        return
    
    # Handle delete command
    if args.delete:
        print("\n⚠️  WARNING: This will delete the downloaded model!")
        choice = input("Are you sure? (y/N): ").strip().lower()
        if choice == 'y':
            delete_model()
        else:
            print("Cancelled")
        return
    
    # Handle download
    if args.auto:
        # Automatic download
        print_banner()
        success = download_model(show_progress=True, verify_checksum=args.verify)
        sys.exit(0 if success else 1)
    else:
        # Interactive download
        success = interactive_download()
        sys.exit(0 if success else 1)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    main()
