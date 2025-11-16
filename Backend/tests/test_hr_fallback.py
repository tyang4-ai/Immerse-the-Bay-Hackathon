"""
Test script for heart rate fallback leads

Tests the multi-lead fallback system with corrupted leads
"""

import requests
import json
import numpy as np

def generate_clean_ecg():
    """Generate clean ECG with all leads"""
    np.random.seed(42)
    ecg_signal = np.random.randn(4096, 12) * 0.05

    # Add R-peaks
    sampling_rate = 400
    heart_rate = 72
    rr_interval_samples = int(60 / heart_rate * sampling_rate)

    for i in range(0, 4096, rr_interval_samples):
        if i + 50 < 4096:
            ecg_signal[i:i+50, :] += np.random.randn(50, 12) * 0.3
            # Strong signal in all leads
            ecg_signal[i:i+50, 1] += 1.0  # Lead II
            ecg_signal[i:i+50, 6] += 0.8  # V1
            ecg_signal[i:i+50, 10] += 0.9  # V5

    return ecg_signal

def corrupt_lead(ecg_signal, lead_index):
    """Corrupt a specific lead with noise/flatline"""
    ecg_corrupted = ecg_signal.copy()
    # Make the lead flat (dead lead)
    ecg_corrupted[:, lead_index] = np.random.randn(4096) * 0.001
    return ecg_corrupted

def test_heart_rate_fallback():
    """Test heart rate fallback system"""
    print("=" * 80)
    print("HEART RATE FALLBACK TEST")
    print("=" * 80)

    clean_ecg = generate_clean_ecg()

    # Test 1: Clean signal (should use Lead II)
    print("\n[TEST 1] Clean signal - All leads functional")
    print("-" * 80)

    response1 = requests.post('http://localhost:5000/api/ecg/analyze', json={
        'ecg_signal': clean_ecg.tolist(),
        'output_mode': 'clinical_expert'
    })

    if response1.status_code == 200:
        result1 = response1.json()
        hr = result1['heart_rate']

        print(f"[OK] Status: {response1.status_code}")
        print(f"Heart Rate: {hr['bpm']} BPM")
        print(f"Lead Used: {hr['lead_used']}")
        print(f"Lead Quality: {hr['lead_quality']:.2f}")
        print(f"Fallback Triggered: {hr['fallback_triggered']}")
        print(f"R-peak Count: {hr['r_peak_count']}")

        if hr['lead_used'] == 'II' and not hr['fallback_triggered']:
            print("[OK] Using primary lead II as expected")
        else:
            print(f"[WARNING] Expected Lead II, got {hr['lead_used']}")
    else:
        print(f"[FAIL] Status: {response1.status_code}")

    # Test 2: Corrupt Lead II (should fallback to V1)
    print("\n" + "=" * 80)
    print("[TEST 2] Corrupted Lead II - Should fallback to V1")
    print("-" * 80)

    corrupted_ii = corrupt_lead(clean_ecg, 1)  # Corrupt Lead II

    response2 = requests.post('http://localhost:5000/api/ecg/analyze', json={
        'ecg_signal': corrupted_ii.tolist(),
        'output_mode': 'clinical_expert'
    })

    if response2.status_code == 200:
        result2 = response2.json()
        hr = result2['heart_rate']

        print(f"[OK] Status: {response2.status_code}")
        print(f"Heart Rate: {hr['bpm']} BPM")
        print(f"Lead Used: {hr['lead_used']}")
        print(f"Lead Quality: {hr['lead_quality']:.2f}")
        print(f"Fallback Triggered: {hr['fallback_triggered']}")

        if hr['lead_used'] != 'II' and hr['fallback_triggered']:
            print(f"[OK] Fallback triggered, using {hr['lead_used']}")
        else:
            print(f"[WARNING] Fallback should have triggered")
    else:
        print(f"[FAIL] Status: {response2.status_code}")

    # Test 3: Corrupt Lead II and V1 (should fallback to V5)
    print("\n" + "=" * 80)
    print("[TEST 3] Corrupted Lead II and V1 - Should fallback to V5")
    print("-" * 80)

    corrupted_ii_v1 = corrupt_lead(corrupted_ii, 6)  # Also corrupt V1

    response3 = requests.post('http://localhost:5000/api/ecg/analyze', json={
        'ecg_signal': corrupted_ii_v1.tolist(),
        'output_mode': 'clinical_expert'
    })

    if response3.status_code == 200:
        result3 = response3.json()
        hr = result3['heart_rate']

        print(f"[OK] Status: {response3.status_code}")
        print(f"Heart Rate: {hr['bpm']} BPM")
        print(f"Lead Used: {hr['lead_used']}")
        print(f"Lead Quality: {hr['lead_quality']:.2f}")
        print(f"Fallback Triggered: {hr['fallback_triggered']}")

        if hr['lead_used'] in ['V5', 'I', 'aVF'] and hr['fallback_triggered']:
            print(f"[OK] Deep fallback to {hr['lead_used']}")
        else:
            print(f"[WARNING] Expected deeper fallback")
    else:
        print(f"[FAIL] Status: {response3.status_code}")

    # Test 4: Quality comparison across all leads
    print("\n" + "=" * 80)
    print("[TEST 4] Lead quality comparison")
    print("-" * 80)

    # Test with progressively corrupted leads
    test_cases = [
        ("All leads clean", clean_ecg),
        ("Lead II corrupted", corrupt_lead(clean_ecg, 1)),
        ("II + V1 corrupted", corrupt_lead(corrupt_lead(clean_ecg, 1), 6)),
        ("II + V1 + V5 corrupted", corrupt_lead(corrupt_lead(corrupt_lead(clean_ecg, 1), 6), 10)),
    ]

    print(f"\n{'Scenario':<25} {'Lead Used':<12} {'Quality':<10} {'Fallback':<10} {'BPM':<8}")
    print("-" * 75)

    for scenario, ecg_data in test_cases:
        response = requests.post('http://localhost:5000/api/ecg/analyze', json={
            'ecg_signal': ecg_data.tolist(),
            'output_mode': 'clinical_expert'
        })

        if response.status_code == 200:
            hr = response.json()['heart_rate']
            fallback_str = "YES" if hr['fallback_triggered'] else "NO"
            print(f"{scenario:<25} {hr['lead_used']:<12} {hr['lead_quality']:<10.2f} {fallback_str:<10} {hr['bpm']:<8.1f}")
        else:
            print(f"{scenario:<25} ERROR: {response.status_code}")

    # Test 5: Response structure validation
    print("\n" + "=" * 80)
    print("[TEST 5] Response structure validation")
    print("-" * 80)

    response5 = requests.post('http://localhost:5000/api/ecg/analyze', json={
        'ecg_signal': clean_ecg.tolist(),
        'output_mode': 'clinical_expert'
    })

    if response5.status_code == 200:
        result5 = response5.json()
        hr = result5['heart_rate']

        required_fields = ['bpm', 'rr_intervals_ms', 'beat_timestamps', 'r_peak_count',
                          'lead_used', 'lead_quality', 'fallback_triggered']

        print("Heart rate response fields:")
        for field in required_fields:
            if field in hr:
                print(f"  [OK] {field}: {hr[field]}")
            else:
                print(f"  [MISSING] {field}")

    print("\n" + "=" * 80)
    print("All heart rate fallback tests complete!")
    print("=" * 80)


if __name__ == '__main__':
    # Check server is running
    try:
        health_check = requests.get('http://localhost:5000/health')
        if health_check.status_code == 200:
            print("[OK] Server is running")
            test_heart_rate_fallback()
        else:
            print(f"[ERROR] Server health check failed: {health_check.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server at http://localhost:5000")
        print("Please start the Flask server first: python ecg_api.py")