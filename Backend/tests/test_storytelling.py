"""
Test script for storytelling mode in ECG API

Tests the new storytelling mode with different regions
"""

import requests
import json
import numpy as np

# Generate synthetic ECG data (RBBB pattern)
def generate_rbbb_ecg():
    """Generate synthetic ECG with RBBB characteristics"""
    np.random.seed(42)

    # Base ECG with RBBB pattern (wide QRS, rsR' in V1)
    ecg_signal = np.random.randn(4096, 12) * 0.05

    # Add R-peaks at regular intervals (72 BPM)
    sampling_rate = 400  # Hz
    heart_rate = 72  # BPM
    rr_interval_samples = int(60 / heart_rate * sampling_rate)

    for i in range(0, 4096, rr_interval_samples):
        if i + 50 < 4096:
            # Wide QRS for RBBB (>120ms)
            ecg_signal[i:i+50, :] += np.random.randn(50, 12) * 0.3
            # Strong signal in Lead II
            ecg_signal[i:i+50, 1] += 1.0

    return ecg_signal.tolist()


def test_storytelling_mode():
    """Test storytelling mode API"""
    print("=" * 80)
    print("STORYTELLING MODE TEST")
    print("=" * 80)

    # Generate test ECG data
    ecg_data = generate_rbbb_ecg()

    # Test 1: Default storytelling (most affected region)
    print("\n[TEST 1] Storytelling mode - Default region (most affected)")
    print("-" * 80)

    response1 = requests.post('http://localhost:5000/api/ecg/analyze', json={
        'ecg_signal': ecg_data,
        'output_mode': 'storytelling'
    })

    if response1.status_code == 200:
        result1 = response1.json()

        print(f"[OK] Status: {response1.status_code}")
        print(f"Top Condition: {result1['top_condition']}")
        print(f"Confidence: {result1['confidence']:.1%}")
        print(f"Processing Time: {result1['processing_time_ms']:.2f}ms")
        print(f"Output Mode: {result1['metadata']['output_mode']}")

        if 'storytelling_journey' in result1.get('llm_interpretation', {}):
            journey = result1['llm_interpretation']['storytelling_journey']
            print(f"\n[Storytelling Journey]")
            print(f"Location: {journey['location_name']} ({journey['current_location']})")
            print(f"\nNarrative:")
            print(f"  {journey['narrative'][:200]}...")
            print(f"\nMedical Insight:")
            print(f"  {journey['medical_insight']}")
            print(f"\nAtmosphere:")
            print(f"  {journey['atmosphere']}")
            print(f"\nWaypoints ({len(journey['waypoints'])}):")
            for wp in journey['waypoints']:
                print(f"  - {wp['region']}: {wp['teaser']}")
            print(f"\nCondition Context:")
            print(f"  Pathology: {journey['condition_context']['primary_pathology']}")
            print(f"  Severity: {journey['condition_context']['severity_level']}")
            print(f"  Urgency: {journey['condition_context']['urgency']}")
        else:
            print("[ERROR] No storytelling_journey in response!")
            print(f"Response keys: {list(result1.get('llm_interpretation', {}).keys())}")
    else:
        print(f"[FAIL] Status: {response1.status_code}")
        print(f"Error: {response1.json()}")

    # Test 2: Focused storytelling (specific region)
    print("\n" + "=" * 80)
    print("[TEST 2] Storytelling mode - Focused on SA Node")
    print("-" * 80)

    response2 = requests.post('http://localhost:5000/api/ecg/analyze', json={
        'ecg_signal': ecg_data,
        'output_mode': 'storytelling',
        'region_focus': 'sa_node'
    })

    if response2.status_code == 200:
        result2 = response2.json()

        print(f"[OK] Status: {response2.status_code}")
        print(f"Region Focus: {result2['metadata']['region_focus']}")

        if 'storytelling_journey' in result2.get('llm_interpretation', {}):
            journey = result2['llm_interpretation']['storytelling_journey']
            print(f"\n[Storytelling Journey]")
            print(f"Location: {journey['location_name']} ({journey['current_location']})")
            print(f"\nNarrative:")
            print(f"  {journey['narrative']}")
    else:
        print(f"[FAIL] Status: {response2.status_code}")
        print(f"Error: {response2.json()}")

    # Test 3: Multiple regions journey
    print("\n" + "=" * 80)
    print("[TEST 3] Journey through multiple regions")
    print("-" * 80)

    regions_to_visit = ['sa_node', 'av_node', 'rbbb', 'lbbb', 'rv', 'lv']

    for region in regions_to_visit:
        response = requests.post('http://localhost:5000/api/ecg/analyze', json={
            'ecg_signal': ecg_data,
            'output_mode': 'storytelling',
            'region_focus': region
        })

        if response.status_code == 200:
            result = response.json()
            journey = result['llm_interpretation']['storytelling_journey']
            cache_hit = result['metadata']['cache_hit']
            cache_status = "[CACHED]" if cache_hit else "[FRESH]"

            print(f"\n{cache_status} {journey['location_name']}:")
            print(f"  Severity: {journey['condition_context']['severity_level']}")
            print(f"  Urgency: {journey['condition_context']['urgency']}")
            print(f"  Processing: {result['processing_time_ms']:.2f}ms")
        else:
            print(f"\n[ERROR] {region}: {response.status_code}")

    # Test 4: Compare modes
    print("\n" + "=" * 80)
    print("[TEST 4] Compare output modes")
    print("-" * 80)

    modes = ['clinical_expert', 'patient_education', 'storytelling']

    for mode in modes:
        response = requests.post('http://localhost:5000/api/ecg/analyze', json={
            'ecg_signal': ecg_data,
            'output_mode': mode
        })

        if response.status_code == 200:
            result = response.json()
            llm = result.get('llm_interpretation', {})

            print(f"\n{mode.upper()}:")
            print(f"  Response keys: {list(llm.keys())}")
            print(f"  Processing time: {result['processing_time_ms']:.2f}ms")
            print(f"  Cache hit: {result['metadata']['cache_hit']}")
        else:
            print(f"\n{mode.upper()}: ERROR {response.status_code}")

    print("\n" + "=" * 80)
    print("All storytelling tests complete!")
    print("=" * 80)


if __name__ == '__main__':
    # Check server is running
    try:
        health_check = requests.get('http://localhost:5000/health')
        if health_check.status_code == 200:
            print("[OK] Server is running")
            test_storytelling_mode()
        else:
            print(f"[ERROR] Server health check failed: {health_check.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server at http://localhost:5000")
        print("Please start the Flask server first: python ecg_api.py")