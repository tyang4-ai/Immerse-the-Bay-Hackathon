import requests
import json

print("=" * 80)
print("HoloHuman XR Backend API Test")
print("=" * 80)

# Test 1: Health check
print("\n[Test 1] Health Check Endpoint")
print("-" * 80)
try:
    response = requests.get('http://localhost:5000/health')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("[OK] Health check passed!")
    else:
        print("[FAIL] Health check failed!")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 2: ECG analysis
print("\n[Test 2] ECG Analysis Endpoint")
print("-" * 80)
try:
    with open('data/synthetic_ecg_normal.json', 'r') as f:
        ecg_data = json.load(f)

    print(f"Sending ECG data with {len(ecg_data['ecg_signal'])} leads...")

    response = requests.post(
        'http://localhost:5000/api/ecg/analyze',
        json=ecg_data,
        headers={'Content-Type': 'application/json'}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()

        print("\n[Results Summary]")
        print(f"  Top Condition: {result.get('top_condition', 'N/A')}")
        print(f"  Confidence: {result.get('confidence', 'N/A'):.2%}")
        print(f"  Processing Time: {result.get('processing_time_ms', 'N/A'):.2f} ms")

        print("\n[Heart Rate Analysis]")
        hr = result.get('heart_rate', {})
        print(f"  BPM: {hr.get('bpm', 'N/A'):.1f}")
        print(f"  R-Peak Count: {hr.get('r_peak_count', 'N/A')}")

        print("\n[Top 3 Predictions]")
        predictions = result.get('predictions', {})
        sorted_preds = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:3]
        for condition, prob in sorted_preds:
            print(f"  {condition}: {prob:.1%}")

        print("\n[Most Affected Regions]")
        regions = result.get('region_health', {})
        sorted_regions = sorted(regions.items(), key=lambda x: x[1].get('severity', 0), reverse=True)[:3]
        for region_name, region_data in sorted_regions:
            severity = region_data.get('severity', 0)
            delay = region_data.get('activation_delay_ms', 0)
            print(f"  {region_name}: severity={severity:.3f}, delay={delay}ms")

        print("\n[Clinical Interpretation Available]")
        llm = result.get('llm_interpretation', {})
        print(f"  Differential Diagnosis: {'YES' if 'differential_diagnosis' in llm else 'NO'}")
        print(f"  Risk Assessment: {'YES' if 'risk_assessment' in llm else 'NO'}")
        print(f"  Recommended Workup: {'YES' if 'recommended_workup' in llm else 'NO'}")
        print(f"  Treatment Considerations: {'YES' if 'treatment_considerations' in llm else 'NO'}")
        print(f"  VR Visualization Strategy: {'YES' if 'vr_visualization_strategy' in llm else 'NO'}")

        print("\n[OK] ECG analysis completed successfully!")

        # Optionally save full response
        with open('test_api_response.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("\n[SAVED] Full response saved to: test_api_response.json")

    else:
        print(f"[FAIL] ECG analysis failed!")
        print(f"Response: {response.text}")

except FileNotFoundError:
    print("[ERROR] Could not find data/synthetic_ecg_normal.json")
    print("        Make sure you're running this from the Backend directory")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "=" * 80)
print("Testing Complete!")
print("=" * 80)
