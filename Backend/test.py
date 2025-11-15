import numpy as np
import sys
sys.path.append('data')
from generate_test_ecg import generate_synthetic_ecg
from ecg_heartrate_analyzer import ECGHeartRateAnalyzer

# Generate synthetic ECG with realistic R-peaks (72 BPM, 10.24 seconds)
fake_ecg = generate_synthetic_ecg(heart_rate_bpm=72)
print(f"Generated ECG shape: {fake_ecg.shape}")  # Should be (4096, 12)

# Analyze it
analyzer = ECGHeartRateAnalyzer()
result = analyzer.analyze(fake_ecg)

print(f"Detected BPM: {result['bpm']}")  # Should be ~72
print(f"Beat count: {result['r_peak_count']}")  # Should be ~12
