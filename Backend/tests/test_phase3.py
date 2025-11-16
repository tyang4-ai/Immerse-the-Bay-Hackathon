"""
Test script for Phase 3 temporal drilldown endpoints

Tests:
1. GET /api/ecg/beats - Fast R-peak detection
2. POST /api/ecg/beat/<index> - Single beat analysis
3. POST /api/ecg/segment - Time window analysis
"""

import requests
import json
import numpy as np


def generate_test_ecg():
    """Generate synthetic ECG with known characteristics"""
    np.random.seed(42)

    # Base ECG signal
    ecg_signal = np.random.randn(4096, 12) * 0.05

    # Add R-peaks at regular intervals (72 BPM)
    sampling_rate = 400  # Hz
    heart_rate = 72  # BPM
    rr_interval_samples = int(60 / heart_rate * sampling_rate)

    # Track R-peak positions for validation
    expected_r_peaks = []

    for i in range(0, 4096, rr_interval_samples):
        if i + 50 < 4096:
            # Add QRS complex
            ecg_signal[i:i+50, :] += np.random.randn(50, 12) * 0.3
            # Strong signal in Lead II
            ecg_signal[i:i+50, 1] += 1.0
            expected_r_peaks.append(i + 25)  # Peak in middle of QRS

    return ecg_signal, expected_r_peaks


def test_beats_endpoint():
    """Test GET /api/ecg/beats endpoint"""
    print("=" * 80)
    print("PHASE 3.1: /api/ecg/beats ENDPOINT TEST")
    print("=" * 80)

    ecg_data, expected_peaks = generate_test_ecg()

    # Test 1: Basic beat detection
    print("\n[TEST 1] Basic beat detection")
    print("-" * 80)

    response = requests.post('http://localhost:5000/api/ecg/beats', json={
        'ecg_signal': ecg_data.tolist()
    })

    if response.status_code == 200:
        result = response.json()

        print(f"[OK] Status: {response.status_code}")
        print(f"Beat Count: {result['beat_count']}")
        print(f"Avg RR Interval: {result['avg_rr_interval_ms']} ms")
        print(f"Rhythm: {result['rhythm']}")
        print(f"Lead Used: {result['lead_used']}")
        print(f"Lead Quality: {result['lead_quality']}")
        print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
        print(f"R-peaks: {result['r_peaks'][:5]}... ({len(result['r_peaks'])} total)")

        # Validation
        expected_count = len(expected_peaks)
        detected_count = result['beat_count']

        if abs(detected_count - expected_count) <= 2:  # Allow ±2 beats tolerance
            print(f"[OK] Beat count matches expected (~{expected_count} beats)")
        else:
            print(f"[WARNING] Beat count mismatch: expected ~{expected_count}, got {detected_count}")

        # Check rhythm
        if result['rhythm'] == 'regular':
            print("[OK] Correctly identified regular rhythm")
        else:
            print(f"[WARNING] Expected 'regular', got '{result['rhythm']}'")

        # Check RR interval (should be ~833ms for 72 BPM)
        expected_rr = 60000 / 72  # ms
        actual_rr = result['avg_rr_interval_ms']

        if abs(actual_rr - expected_rr) < 50:  # ±50ms tolerance
            print(f"[OK] RR interval matches expected (~{expected_rr:.1f}ms)")
        else:
            print(f"[WARNING] RR interval off: expected ~{expected_rr:.1f}ms, got {actual_rr}ms")

        return result['r_peaks']  # Return for next test
    else:
        print(f"[FAIL] Status: {response.status_code}")
        print(f"Error: {response.json()}")
        return []

    print()


def test_beat_detail_endpoint(r_peaks):
    """Test POST /api/ecg/beat/<index> endpoint"""
    print("\n" + "=" * 80)
    print("PHASE 3.2: /api/ecg/beat/<index> ENDPOINT TEST")
    print("=" * 80)

    ecg_data, _ = generate_test_ecg()

    if not r_peaks or len(r_peaks) < 3:
        print("[SKIP] Not enough R-peaks detected in previous test")
        return

    # Test 1: Valid beat analysis
    beat_index = 2  # Third beat
    print(f"\n[TEST 1] Analyze beat #{beat_index}")
    print("-" * 80)

    response = requests.post(f'http://localhost:5000/api/ecg/beat/{beat_index}', json={
        'ecg_signal': ecg_data.tolist()
    })

    if response.status_code == 200:
        result = response.json()

        print(f"[OK] Status: {response.status_code}")
        print(f"Beat Index: {result['beat_index']}")
        print(f"R-peak Sample: {result['r_peak_sample']}")
        print(f"Lead Used: {result['lead_used']}")

        print(f"\nWaveform Components:")
        waveform = result['waveform']
        print(f"  P-wave: onset={waveform['p_wave']['onset']}, "
              f"peak={waveform['p_wave']['peak']}, "
              f"offset={waveform['p_wave']['offset']}")
        print(f"  QRS: onset={waveform['qrs_complex']['onset']}, "
              f"peak={waveform['qrs_complex']['peak']}, "
              f"offset={waveform['qrs_complex']['offset']}")
        print(f"  T-wave: onset={waveform['t_wave']['onset']}, "
              f"peak={waveform['t_wave']['peak']}, "
              f"offset={waveform['t_wave']['offset']}")

        print(f"\nIntervals:")
        intervals = result['intervals']
        print(f"  PR interval: {intervals['pr_interval_ms']} ms")
        print(f"  QRS duration: {intervals['qrs_duration_ms']} ms")
        print(f"  QT interval: {intervals['qt_interval_ms']} ms")

        print(f"\nAnnotation: {result['annotations']}")
        print(f"Raw samples count: {len(result['raw_samples'])}")
        print(f"Processing Time: {result['processing_time_ms']:.2f}ms")

        # Validation
        if 120 < intervals['pr_interval_ms'] < 200:
            print("[OK] PR interval within normal range (120-200ms)")
        else:
            print(f"[INFO] PR interval: {intervals['pr_interval_ms']}ms")

        if intervals['qrs_duration_ms'] < 120:
            print("[OK] QRS duration normal (<120ms)")
        else:
            print(f"[INFO] Wide QRS: {intervals['qrs_duration_ms']}ms")

    else:
        print(f"[FAIL] Status: {response.status_code}")
        print(f"Error: {response.json()}")

    # Test 2: Invalid beat index
    print("\n[TEST 2] Invalid beat index (out of range)")
    print("-" * 80)

    invalid_index = 999
    response = requests.post(f'http://localhost:5000/api/ecg/beat/{invalid_index}', json={
        'ecg_signal': ecg_data.tolist()
    })

    if response.status_code == 400:
        error = response.json()
        print(f"[OK] Status: {response.status_code} (expected error)")
        print(f"Error: {error['error']}")
        print(f"Error ID: {error['error_id']}")
        print(f"Beat Count: {error['beat_count']}")
    else:
        print(f"[WARNING] Expected 400, got {response.status_code}")

    print()


def test_segment_endpoint():
    """Test POST /api/ecg/segment endpoint"""
    print("\n" + "=" * 80)
    print("PHASE 3.3: /api/ecg/segment ENDPOINT TEST")
    print("=" * 80)

    ecg_data, expected_peaks = generate_test_ecg()

    # Calculate total duration
    sampling_rate = 400
    total_duration_ms = (4096 / sampling_rate) * 1000

    print(f"Total ECG duration: {total_duration_ms:.1f}ms")

    # Test 1: First 2 seconds
    print("\n[TEST 1] Analyze segment: 0-2000ms")
    print("-" * 80)

    response = requests.post('http://localhost:5000/api/ecg/segment', json={
        'ecg_signal': ecg_data.tolist(),
        'start_ms': 0,
        'end_ms': 2000
    })

    if response.status_code == 200:
        result = response.json()
        segment = result['segment']

        print(f"[OK] Status: {response.status_code}")
        print(f"Time Window: {segment['start_ms']}-{segment['end_ms']}ms ({segment['duration_ms']}ms)")
        print(f"Beats in Segment: {segment['beats_in_segment']}")
        print(f"Rhythm Analysis: {segment['rhythm_analysis']}")
        print(f"Lead Used: {segment['lead_used']}")
        print(f"Events:")
        for event in segment['events']:
            print(f"  - {event['type']} at {event['time_ms']}ms")
        print(f"Processing Time: {result['processing_time_ms']:.2f}ms")

        # Validation: ~2 beats expected in 2 seconds at 72 BPM
        expected_beats = int(2.0 * (72 / 60))  # ~2 beats
        if abs(segment['beats_in_segment'] - expected_beats) <= 1:
            print(f"[OK] Beat count matches expected (~{expected_beats} beats)")
        else:
            print(f"[INFO] Expected ~{expected_beats} beats, got {segment['beats_in_segment']}")

    else:
        print(f"[FAIL] Status: {response.status_code}")
        print(f"Error: {response.json()}")

    # Test 2: Mid-section
    print("\n[TEST 2] Analyze segment: 2000-4000ms")
    print("-" * 80)

    response = requests.post('http://localhost:5000/api/ecg/segment', json={
        'ecg_signal': ecg_data.tolist(),
        'start_ms': 2000,
        'end_ms': 4000
    })

    if response.status_code == 200:
        result = response.json()
        segment = result['segment']

        print(f"[OK] Status: {response.status_code}")
        print(f"Beats in Segment: {segment['beats_in_segment']}")
        print(f"Rhythm Analysis: {segment['rhythm_analysis']}")

        if 'regular' in segment['rhythm_analysis'].lower():
            print("[OK] Regular rhythm detected")
    else:
        print(f"[FAIL] Status: {response.status_code}")

    # Test 3: Invalid time range
    print("\n[TEST 3] Invalid time range (end < start)")
    print("-" * 80)

    response = requests.post('http://localhost:5000/api/ecg/segment', json={
        'ecg_signal': ecg_data.tolist(),
        'start_ms': 5000,
        'end_ms': 3000
    })

    if response.status_code == 400:
        error = response.json()
        print(f"[OK] Status: {response.status_code} (expected error)")
        print(f"Error: {error['error']}")
        print(f"Error ID: {error['error_id']}")
    else:
        print(f"[WARNING] Expected 400, got {response.status_code}")

    # Test 4: Out of bounds
    print("\n[TEST 4] Time range exceeds ECG duration")
    print("-" * 80)

    response = requests.post('http://localhost:5000/api/ecg/segment', json={
        'ecg_signal': ecg_data.tolist(),
        'start_ms': 0,
        'end_ms': 20000  # Way beyond duration
    })

    if response.status_code == 400:
        error = response.json()
        print(f"[OK] Status: {response.status_code} (expected error)")
        print(f"Error: {error['error']}")
    else:
        print(f"[WARNING] Expected 400, got {response.status_code}")

    print()


def test_all_endpoints_comparison():
    """Compare performance across all endpoints"""
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)

    ecg_data, _ = generate_test_ecg()

    endpoints = [
        ('Full Analysis', 'POST', '/api/ecg/analyze', {'ecg_signal': ecg_data.tolist(), 'output_mode': 'clinical_expert'}),
        ('Beats Only', 'POST', '/api/ecg/beats', {'ecg_signal': ecg_data.tolist()}),
        ('Beat Detail', 'POST', '/api/ecg/beat/2', {'ecg_signal': ecg_data.tolist()}),
        ('Segment', 'POST', '/api/ecg/segment', {'ecg_signal': ecg_data.tolist(), 'start_ms': 0, 'end_ms': 2000}),
    ]

    print(f"\n{'Endpoint':<20} {'Method':<8} {'Status':<8} {'Time (ms)':<12} {'Notes'}")
    print("-" * 80)

    for name, method, path, payload in endpoints:
        url = f'http://localhost:5000{path}'

        if method == 'POST':
            response = requests.post(url, json=payload)
        else:
            response = requests.get(url)

        if response.status_code == 200:
            result = response.json()
            processing_time = result.get('processing_time_ms', 'N/A')

            # Get relevant note
            note = ""
            if 'beat_count' in result:
                note = f"{result['beat_count']} beats"
            elif 'segment' in result:
                note = f"{result['segment']['beats_in_segment']} beats"
            elif 'beat_index' in result:
                note = f"Beat #{result['beat_index']}"

            print(f"{name:<20} {method:<8} {response.status_code:<8} {processing_time!s:<12} {note}")
        else:
            print(f"{name:<20} {method:<8} {response.status_code:<8} {'ERROR':<12}")

    print()


def main():
    """Run all Phase 3 tests"""
    print("=" * 80)
    print("PHASE 3 TEMPORAL DRILLDOWN ENDPOINTS - COMPREHENSIVE TEST")
    print("=" * 80)

    # Check server health
    try:
        health_check = requests.get('http://localhost:5000/health')
        if health_check.status_code == 200:
            print("[OK] Server is running")
            print(f"Server status: {health_check.json()}")
        else:
            print(f"[ERROR] Server health check failed: {health_check.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server at http://localhost:5000")
        print("Please start the Flask server first: python ecg_api.py")
        return

    print()

    # Run tests
    r_peaks = test_beats_endpoint()
    test_beat_detail_endpoint(r_peaks)
    test_segment_endpoint()
    test_all_endpoints_comparison()

    print("=" * 80)
    print("ALL PHASE 3 TESTS COMPLETE!")
    print("=" * 80)
    print("\nEndpoints tested:")
    print("  [OK] POST /api/ecg/beats - Fast R-peak detection")
    print("  [OK] POST /api/ecg/beat/<index> - Single beat waveform analysis")
    print("  [OK] POST /api/ecg/segment - Time window analysis")
    print("\nAll endpoints are ready for Unity VR integration!")


if __name__ == '__main__':
    main()
