# ECG Test Data

This directory contains test ECG data for backend development and testing.

---

## Quick Start

**Option 1: Use synthetic test data (recommended for initial development)**

```python
# Generate synthetic ECG for testing
import numpy as np

# Create synthetic 12-lead ECG (4096 samples × 12 leads)
ecg_signal = np.random.randn(4096, 12) * 0.5
print(ecg_signal.shape)  # (4096, 12)
```

**Option 2: Download real ECG dataset from Zenodo**

The full ECG dataset is available at Zenodo but is **160MB** (too large for GitHub).

### Manual Download Instructions:

1. **Go to Zenodo:** https://zenodo.org/record/3625006
2. **Download file:** `ecg_tracings.hdf5` (160 MB)
3. **Place in:** `Backend/automatic-ecg-diagnosis/data/`
4. **Verify:**
   ```bash
   ls -lh Backend/automatic-ecg-diagnosis/data/ecg_tracings.hdf5
   # Should show ~160 MB file
   ```

### Using the Downloaded Dataset:

```python
import h5py
import numpy as np

# Load ECG tracings
with h5py.File('Backend/automatic-ecg-diagnosis/data/ecg_tracings.hdf5', 'r') as f:
    ecg_data = np.array(f['tracings'])
    print(f"Dataset shape: {ecg_data.shape}")  # (827, 4096, 12)

# Use first ECG for testing
test_ecg = ecg_data[0]  # Shape: (4096, 12)
print(f"Test ECG shape: {test_ecg.shape}")
```

---

## Dataset Details

**Source:** Zenodo Record 3625006
**Paper:** "Automatic diagnosis of the 12-lead ECG using a deep neural network"
**Link:** https://www.nature.com/articles/s41467-020-15432-4

### Data Format:

- **Shape:** `(827, 4096, 12)`
  - 827 different patients
  - 4096 samples per ECG (10.24 seconds at 400 Hz)
  - 12 leads: DI, DII, DIII, AVL, AVF, AVR, V1, V2, V3, V4, V5, V6

- **Sampling Rate:** 400 Hz
- **Scale:** 1e-4V (multiply by 1000 to get mV)
- **Padding:** Signals padded with zeros to 4096 samples

### Annotations:

Annotations are available in `Backend/automatic-ecg-diagnosis/data/annotations/`:

- `gold_standard.csv` - Expert consensus annotations
- `cardiologist1.csv`, `cardiologist2.csv` - Individual cardiologist annotations
- `dnn.csv` - Deep neural network predictions

**Conditions (6 total):**
1. 1st degree AV block (1dAVb)
2. Right bundle branch block (RBBB)
3. Left bundle branch block (LBBB)
4. Sinus bradycardia (SB)
5. Atrial fibrillation (AF)
6. Sinus tachycardia (ST)

---

## Synthetic ECG Generator

For initial development, use the included synthetic ECG generator:

```python
# generate_test_ecg.py
import numpy as np
import json

def generate_synthetic_ecg(duration_sec=10.24, sampling_rate=400, num_leads=12):
    """
    Generate synthetic 12-lead ECG for testing.

    Args:
        duration_sec: Duration in seconds (default: 10.24)
        sampling_rate: Samples per second (default: 400 Hz)
        num_leads: Number of ECG leads (default: 12)

    Returns:
        numpy array of shape (num_samples, num_leads)
    """
    num_samples = int(duration_sec * sampling_rate)

    # Generate base signal with realistic characteristics
    t = np.linspace(0, duration_sec, num_samples)

    ecg_signals = []
    for lead_idx in range(num_leads):
        # Simulate ECG components
        # P wave (atrial depolarization)
        p_wave = 0.1 * np.sin(2 * np.pi * 1.2 * t)

        # QRS complex (ventricular depolarization)
        heart_rate = 72  # BPM
        beat_freq = heart_rate / 60.0
        qrs = 0.8 * np.sin(2 * np.pi * beat_freq * t) * np.exp(-((t % (1/beat_freq)) - 0.1)**2 / 0.01)

        # T wave (ventricular repolarization)
        t_wave = 0.2 * np.sin(2 * np.pi * 0.8 * t)

        # Baseline noise
        noise = np.random.randn(num_samples) * 0.05

        # Combine components with lead-specific variation
        lead_signal = p_wave + qrs + t_wave + noise
        lead_signal *= (1.0 + 0.2 * lead_idx / num_leads)  # Vary amplitude by lead

        ecg_signals.append(lead_signal)

    return np.array(ecg_signals).T  # Shape: (num_samples, num_leads)

def save_as_json(ecg_signal, filename="test_ecg.json"):
    """Save ECG signal as JSON for API testing"""
    data = {
        "ecg_signal": ecg_signal.tolist()
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {filename}")

if __name__ == "__main__":
    # Generate synthetic ECG
    ecg = generate_synthetic_ecg()
    print(f"Generated ECG shape: {ecg.shape}")

    # Save for API testing
    save_as_json(ecg, "synthetic_ecg.json")
```

---

## Testing Backend API

### 1. Using Synthetic Data:

```bash
cd Backend/data
python -c "
import numpy as np
import json

# Generate test ECG
ecg = np.random.randn(4096, 12) * 0.5

# Save as JSON
with open('test_ecg.json', 'w') as f:
    json.dump({'ecg_signal': ecg.tolist()}, f)

print('Created test_ecg.json')
"

# Test API
curl -X POST http://localhost:5000/api/ecg/predict \
  -H "Content-Type: application/json" \
  -d @test_ecg.json
```

### 2. Using Real Data (after downloading):

```python
import h5py
import numpy as np
import requests
import json

# Load real ECG
with h5py.File('../automatic-ecg-diagnosis/data/ecg_tracings.hdf5', 'r') as f:
    ecg = np.array(f['tracings'][0])  # First patient

# Send to API
data = {"ecg_signal": ecg.tolist()}
response = requests.post(
    "http://localhost:5000/api/ecg/predict",
    json=data
)

print(json.dumps(response.json(), indent=2))
```

---

## File Structure

```
Backend/data/
├── README.md                    # This file
├── download_ecg_samples.py      # Script to download from Zenodo (optional)
├── generate_test_ecg.py         # Generate synthetic ECG for testing
└── (test files you create)

Backend/automatic-ecg-diagnosis/data/
├── README.md                    # Original dataset documentation
├── attributes.csv               # Patient demographics (sex, age)
├── annotations/
│   ├── gold_standard.csv       # Expert annotations
│   ├── cardiologist1.csv
│   ├── cardiologist2.csv
│   └── ...
└── ecg_tracings.hdf5           # DOWNLOAD MANUALLY (160 MB, not in git)
```

---

## .gitignore Recommendations

Add to `.gitignore`:

```
# ECG dataset files (too large for GitHub)
**/ecg_tracings.hdf5
**/ecg_tracings_full.hdf5
**/ecg_samples.hdf5

# Test data files
**/test_ecg.json
**/synthetic_ecg.json
```

---

## Citation

If using the real dataset, please cite:

```bibtex
@article{ribeiro_automatic_2020,
  title = {Automatic Diagnosis of the 12-Lead {{ECG}} Using a Deep Neural Network},
  author = {Ribeiro, Ant{\^o}nio H. and Ribeiro, Manoel Horta and Paix{\~a}o, Gabriela M. M. and Oliveira, Derick M. and Gomes, Paulo R. and Canazart, J{\'e}ssica A. and Ferreira, Milton P. S. and Andersson, Carl R. and Macfarlane, Peter W. and Meira Jr., Wagner and Sch{\"o}n, Thomas B. and Ribeiro, Antonio Luiz P.},
  year = {2020},
  volume = {11},
  pages = {1760},
  doi = {https://doi.org/10.1038/s41467-020-15432-4},
  journal = {Nature Communications},
  number = {1}
}
```

---

## Troubleshooting

**Issue:** Can't download from Zenodo

**Solution:** The dataset is very large (160MB). Alternative options:
1. Use synthetic test data (recommended for development)
2. Use the dummy data in `Backend/dummy_data/` (already includes sample responses)
3. Download manually from browser: https://zenodo.org/record/3625006

**Issue:** HDF5 file not found

**Solution:**
```bash
# Check if file exists
ls -lh Backend/automatic-ecg-diagnosis/data/ecg_tracings.hdf5

# If missing, download from Zenodo (see instructions above)
```

**Issue:** Python h5py module not found

**Solution:**
```bash
pip install h5py
```

---

## For Hackathon Development

**Recommended approach:**

1. **Start with dummy data** in `Backend/dummy_data/` - No download needed!
2. **Use synthetic ECG** for backend testing - Generate with numpy
3. **Download real data** (optional) - Only if you need actual ECG signals

The dummy data already contains complete API responses with realistic values, so you can develop the Unity frontend immediately without any downloads.
