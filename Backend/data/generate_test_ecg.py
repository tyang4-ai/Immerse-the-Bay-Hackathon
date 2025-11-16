#!/usr/bin/env python3
"""
Generate synthetic 12-lead ECG data for testing the backend API.

Usage:
    python generate_test_ecg.py

Output:
    - synthetic_ecg.json: API-ready JSON file with ECG data
    - Can be used with: curl -X POST http://localhost:5000/api/ecg/predict -d @synthetic_ecg.json
"""

import numpy as np
import json


def generate_synthetic_ecg(duration_sec=10.24, sampling_rate=400, num_leads=12, heart_rate_bpm=72):
    """
    Generate realistic synthetic 12-lead ECG for testing.

    Parameters:
        duration_sec (float): Duration in seconds (default: 10.24 for 4096 samples)
        sampling_rate (int): Samples per second (default: 400 Hz)
        num_leads (int): Number of ECG leads (default: 12)
        heart_rate_bpm (int): Heart rate in beats per minute (default: 72)

    Returns:
        numpy.ndarray: ECG signal of shape (num_samples, num_leads)
    """
    num_samples = int(duration_sec * sampling_rate)
    t = np.linspace(0, duration_sec, num_samples)

    # Heart rate parameters
    beat_period = 60.0 / heart_rate_bpm  # seconds per beat
    beat_freq = 1.0 / beat_period

    ecg_signals = []

    for lead_idx in range(num_leads):
        # Initialize signal
        signal = np.zeros(num_samples)

        # Generate beats
        num_beats = int(duration_sec / beat_period)

        for beat in range(num_beats):
            beat_start = beat * beat_period

            # P wave (atrial depolarization) - ~100ms duration
            p_center = beat_start + 0.08
            p_width = 0.04
            p_amplitude = 0.15 + 0.05 * (lead_idx / num_leads)
            signal += p_amplitude * np.exp(-((t - p_center) ** 2) / (2 * p_width ** 2))

            # QRS complex (ventricular depolarization) - ~80ms duration
            qrs_center = beat_start + 0.16
            # Q wave (negative)
            q_width = 0.015
            q_amplitude = -0.1
            signal += q_amplitude * np.exp(-((t - (qrs_center - 0.02)) ** 2) / (2 * q_width ** 2))

            # R wave (large positive spike)
            r_width = 0.02
            r_amplitude = 1.0 + 0.3 * (lead_idx / num_leads)  # Vary by lead
            signal += r_amplitude * np.exp(-((t - qrs_center) ** 2) / (2 * r_width ** 2))

            # S wave (negative)
            s_width = 0.02
            s_amplitude = -0.2
            signal += s_amplitude * np.exp(-((t - (qrs_center + 0.03)) ** 2) / (2 * s_width ** 2))

            # T wave (ventricular repolarization) - ~150ms duration
            t_center = beat_start + 0.35
            t_width = 0.06
            t_amplitude = 0.3 + 0.1 * (lead_idx / num_leads)
            signal += t_amplitude * np.exp(-((t - t_center) ** 2) / (2 * t_width ** 2))

        # Add baseline wander (low frequency noise)
        baseline_freq = 0.5  # Hz
        baseline_amplitude = 0.05
        baseline_wander = baseline_amplitude * np.sin(2 * np.pi * baseline_freq * t)
        signal += baseline_wander

        # Add high frequency noise
        noise_amplitude = 0.02
        noise = noise_amplitude * np.random.randn(num_samples)
        signal += noise

        ecg_signals.append(signal)

    # Transpose to shape (num_samples, num_leads)
    ecg_array = np.array(ecg_signals).T

    return ecg_array


def save_as_json(ecg_signal, filename="synthetic_ecg.json"):
    """
    Save ECG signal as JSON in the format expected by the Flask API.

    Parameters:
        ecg_signal (numpy.ndarray): ECG data of shape (num_samples, num_leads)
        filename (str): Output JSON filename
    """
    # Convert to Python list (JSON serializable)
    ecg_list = ecg_signal.tolist()

    # Create API request format
    data = {
        "ecg_signal": ecg_list,
        "patient_id": "synthetic_test_001",
        "timestamp": 1700000000
    }

    # Save to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Synthetic ECG saved to: {filename}")
    print(f"Shape: {ecg_signal.shape}")
    print(f"Value range: [{ecg_signal.min():.3f}, {ecg_signal.max():.3f}]")
    print(f"\nUsage:")
    print(f"  curl -X POST http://localhost:5000/api/ecg/predict \\")
    print(f"       -H 'Content-Type: application/json' \\")
    print(f"       -d @{filename}")


def main():
    """Generate multiple test ECG files with different conditions."""
    print("=" * 60)
    print("Synthetic ECG Generator")
    print("=" * 60)

    # 1. Normal ECG (72 BPM)
    print("\n[1/3] Generating normal ECG (72 BPM)...")
    normal_ecg = generate_synthetic_ecg(heart_rate_bpm=72)
    save_as_json(normal_ecg, "synthetic_ecg_normal.json")

    # 2. Bradycardia (50 BPM)
    print("\n[2/3] Generating bradycardia ECG (50 BPM)...")
    brady_ecg = generate_synthetic_ecg(heart_rate_bpm=50)
    save_as_json(brady_ecg, "synthetic_ecg_bradycardia.json")

    # 3. Tachycardia (110 BPM)
    print("\n[3/3] Generating tachycardia ECG (110 BPM)...")
    tachy_ecg = generate_synthetic_ecg(heart_rate_bpm=110)
    save_as_json(tachy_ecg, "synthetic_ecg_tachycardia.json")

    print("\n" + "=" * 60)
    print("All synthetic ECG files generated!")
    print("=" * 60)
    print("\nTest files created:")
    print("  - synthetic_ecg_normal.json (72 BPM)")
    print("  - synthetic_ecg_bradycardia.json (50 BPM)")
    print("  - synthetic_ecg_tachycardia.json (110 BPM)")
    print("\nNote: These are synthetic signals for testing only.")
    print("      For real ECG data, download from Zenodo (see README.md)")


if __name__ == "__main__":
    main()
