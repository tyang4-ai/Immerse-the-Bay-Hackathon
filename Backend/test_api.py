import requests
import json
from data.generate_test_ecg import generate_synthetic_ecg

# 1. Test health endpoint
response = requests.get('http://localhost:5000/health')
print(response.json())

# 2. Generate test ECG
ecg_data = generate_synthetic_ecg(heart_rate_bpm=72)

# 3. Send to analyze endpoint
response = requests.post(
    'http://localhost:5000/api/ecg/analyze',
    json={'ecg_signal': ecg_data.tolist()}
)

# 4. Print results
print(json.dumps(response.json(), indent=2))