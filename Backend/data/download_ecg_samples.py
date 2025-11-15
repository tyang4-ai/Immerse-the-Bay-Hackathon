#!/usr/bin/env python3
"""
Download ECG Sample Data

This script downloads a small subset of ECG samples from the Zenodo dataset
for testing purposes. The full dataset is 160MB and exceeds GitHub's file size limit.

Full dataset: https://doi.org/10.5281/zenodo.3625006
Paper: https://www.nature.com/articles/s41467-020-15432-4

Usage:
    python download_ecg_samples.py

This will create:
    - ecg_samples.hdf5: 10 sample ECG recordings (~500KB)
    - sample_annotations.csv: Corresponding annotations
"""

import requests
import numpy as np
import h5py
import pandas as pd
import sys
from pathlib import Path

# Zenodo record ID for the ECG dataset
ZENODO_RECORD_ID = "3625006"
ZENODO_API_BASE = "https://zenodo.org/api/records"

def download_full_dataset(output_path="ecg_tracings_full.hdf5"):
    """
    Download the full ECG dataset from Zenodo (160MB).
    WARNING: This file is too large for GitHub (<100MB limit).
    """
    print(f"Downloading full ECG dataset from Zenodo...")
    print(f"Record ID: {ZENODO_RECORD_ID}")
    print(f"This may take several minutes (160MB download)...")

    # Get record metadata
    record_url = f"{ZENODO_API_BASE}/{ZENODO_RECORD_ID}"
    response = requests.get(record_url)

    if response.status_code != 200:
        print(f"Error: Could not fetch record metadata (status {response.status_code})")
        return False

    record_data = response.json()

    # Find the HDF5 file
    files = record_data.get('files', [])
    hdf5_file = None

    for f in files:
        if f['key'] == 'ecg_tracings.hdf5':
            hdf5_file = f
            break

    if not hdf5_file:
        print("Error: ecg_tracings.hdf5 not found in Zenodo record")
        return False

    download_url = hdf5_file['links']['self']
    file_size = hdf5_file['size']

    print(f"File size: {file_size / 1024 / 1024:.1f} MB")
    print(f"Download URL: {download_url}")

    # Download with progress
    response = requests.get(download_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(output_path, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                progress = (downloaded / total_size) * 100
                print(f"\rProgress: {progress:.1f}% ({downloaded / 1024 / 1024:.1f} MB)", end='')

    print(f"\n✓ Downloaded to {output_path}")
    return True

def create_sample_dataset(input_path="ecg_tracings_full.hdf5",
                         output_path="ecg_samples.hdf5",
                         num_samples=10):
    """
    Extract a small subset of ECG samples for testing.

    Args:
        input_path: Path to full HDF5 file
        output_path: Path for sample HDF5 file
        num_samples: Number of samples to extract (default: 10)
    """
    print(f"\nExtracting {num_samples} samples...")

    if not Path(input_path).exists():
        print(f"Error: {input_path} not found. Run download_full_dataset() first.")
        return False

    # Read full dataset
    with h5py.File(input_path, 'r') as f_in:
        full_data = f_in['tracings'][:]
        print(f"Full dataset shape: {full_data.shape}")

        # Select diverse samples (evenly spaced)
        indices = np.linspace(0, len(full_data) - 1, num_samples, dtype=int)
        sample_data = full_data[indices]

        print(f"Sample indices: {indices}")
        print(f"Sample data shape: {sample_data.shape}")

        # Write sample dataset
        with h5py.File(output_path, 'w') as f_out:
            f_out.create_dataset('tracings', data=sample_data, compression='gzip')
            f_out.attrs['description'] = f"{num_samples} sample ECG recordings from Zenodo record {ZENODO_RECORD_ID}"
            f_out.attrs['source'] = "https://doi.org/10.5281/zenodo.3625006"
            f_out.attrs['original_indices'] = indices

    file_size = Path(output_path).stat().st_size
    print(f"✓ Created {output_path} ({file_size / 1024:.1f} KB)")
    return True

def create_sample_annotations(annotations_dir="../automatic-ecg-diagnosis/data/annotations",
                              indices=None,
                              output_path="sample_annotations.csv"):
    """
    Extract annotations for the sample ECG recordings.
    """
    gold_standard_path = Path(annotations_dir) / "gold_standard.csv"

    if not gold_standard_path.exists():
        print(f"Warning: {gold_standard_path} not found. Skipping annotations.")
        return False

    # Read full annotations
    df_full = pd.read_csv(gold_standard_path)
    print(f"\nFull annotations shape: {df_full.shape}")

    if indices is None:
        indices = np.linspace(0, len(df_full) - 1, 10, dtype=int)

    # Extract sample annotations
    df_sample = df_full.iloc[indices].reset_index(drop=True)
    df_sample.to_csv(output_path, index=False)

    print(f"✓ Created {output_path}")
    print(f"Sample annotations:\n{df_sample}")
    return True

def main():
    """
    Main workflow: Download full dataset, create sample subset.
    """
    print("=" * 60)
    print("ECG Sample Data Downloader")
    print("=" * 60)

    # Step 1: Download full dataset
    full_dataset_path = "ecg_tracings_full.hdf5"

    if not Path(full_dataset_path).exists():
        print("\n[Step 1/3] Downloading full dataset from Zenodo...")
        success = download_full_dataset(full_dataset_path)
        if not success:
            print("\n❌ Download failed. Please check your internet connection.")
            print(f"Manual download: https://zenodo.org/record/{ZENODO_RECORD_ID}")
            return 1
    else:
        print(f"\n[Step 1/3] Full dataset already exists: {full_dataset_path}")

    # Step 2: Create sample subset
    sample_dataset_path = "ecg_samples.hdf5"
    print(f"\n[Step 2/3] Creating sample dataset...")
    success = create_sample_dataset(
        input_path=full_dataset_path,
        output_path=sample_dataset_path,
        num_samples=10
    )

    if not success:
        return 1

    # Step 3: Extract sample annotations
    print(f"\n[Step 3/3] Extracting sample annotations...")
    indices = np.linspace(0, 826, 10, dtype=int)  # 827 total samples
    create_sample_annotations(indices=indices)

    print("\n" + "=" * 60)
    print("✓ Sample data created successfully!")
    print("=" * 60)
    print(f"\nFiles created:")
    print(f"  - {sample_dataset_path} (~500 KB) - 10 sample ECG recordings")
    print(f"  - sample_annotations.csv - Gold standard annotations")
    print(f"\nNote: {full_dataset_path} (160 MB) is too large for GitHub.")
    print(f"      Add it to .gitignore if you don't want to upload it.")
    print(f"\nUsage in Python:")
    print(f"    import h5py")
    print(f"    with h5py.File('{sample_dataset_path}', 'r') as f:")
    print(f"        ecg_data = f['tracings'][:]")
    print(f"        print(ecg_data.shape)  # (10, 4096, 12)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
