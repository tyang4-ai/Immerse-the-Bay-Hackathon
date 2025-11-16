import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

class ECGHeartRateAnalyzer:
    def __init__(self, sampling_rate=400):
        self.fs = sampling_rate

        # Lead priority order: (lead_index, lead_name)
        # Lead II is gold standard for R-peak detection
        # V1, V5 have strong ventricular signals
        # I and aVF are limb lead backups
        self.LEAD_PRIORITY = [
            (1, "II"),      # Lead II - best for R-peak detection
            (6, "V1"),      # Lead V1 - good QRS visibility
            (10, "V5"),     # Lead V5 - strong ventricular signal
            (0, "I"),       # Lead I - limb lead backup
            (7, "aVF")      # Lead aVF - inferior view backup
        ]

    def bandpass_filter(self, signal, lowcut=0.5, highcut=40):
        nyquist = 0.5 * self.fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(2, [low, high], btype='band')
        return filtfilt(b, a, signal)

    def assess_signal_quality(self, signal, r_peaks):
        """
        Assess ECG signal quality for R-peak detection

        Args:
            signal: 1D ECG signal
            r_peaks: Detected R-peak indices

        Returns:
            float: Quality score (0.0 = poor, 1.0 = excellent)
        """
        if len(r_peaks) < 2:
            return 0.0

        # 1. SNR estimate (signal-to-noise ratio)
        signal_power = np.var(signal)
        if signal_power < 0.001:  # Flat/dead lead
            return 0.0

        # 2. Rhythm regularity (coefficient of variation of RR intervals)
        rr_intervals = np.diff(r_peaks)
        if len(rr_intervals) < 2:
            return 0.3

        rr_mean = np.mean(rr_intervals)
        rr_std = np.std(rr_intervals)
        cv = rr_std / rr_mean if rr_mean > 0 else 1.0

        # Regular rhythm has low CV (<0.15), irregular rhythm has high CV (>0.5)
        regularity_score = max(0.0, 1.0 - cv)

        # 3. Reasonable heart rate check (30-200 BPM)
        hr_per_interval = 60 / (rr_intervals / self.fs)
        hr_median = np.median(hr_per_interval)

        if 30 <= hr_median <= 200:
            hr_score = 1.0
        elif 20 <= hr_median <= 250:
            hr_score = 0.5
        else:
            hr_score = 0.0

        # 4. Sufficient peak count (at least 4 for 10 seconds of data)
        peak_density = len(r_peaks) / (len(signal) / self.fs)  # peaks per second
        if 0.3 <= peak_density <= 3.5:  # 18-210 BPM range
            density_score = 1.0
        else:
            density_score = 0.5

        # Combined quality score (weighted average)
        quality = (
            0.3 * regularity_score +
            0.3 * hr_score +
            0.2 * density_score +
            0.2 * min(1.0, signal_power / 0.1)  # SNR component
        )

        return min(1.0, max(0.0, quality))

    def detect_r_peaks_single_lead(self, signal):
        """
        Detect R-peaks in a single ECG lead using Pan-Tompkins algorithm

        Args:
            signal: 1D ECG signal

        Returns:
            ndarray: R-peak sample indices
        """
        # Pan-Tompkins algorithm
        filtered = self.bandpass_filter(signal)
        differentiated = np.diff(filtered)
        squared = differentiated ** 2

        # Moving window integration
        window_size = int(0.150 * self.fs)
        integrated = np.convolve(squared, np.ones(window_size)/window_size, mode='same')

        # Find peaks
        min_distance = int(0.2 * self.fs)  # 200ms = max 300 BPM
        peaks, _ = find_peaks(
            integrated,
            distance=min_distance,
            prominence=np.std(integrated) * 0.5
        )

        return peaks

    def detect_r_peaks(self, ecg_signal):
        """
        Detect R-peaks with multi-lead fallback

        Tries leads in priority order: II → V1 → V5 → I → aVF
        Uses the lead with highest signal quality

        Args:
            ecg_signal: (4096, 12) array or 1D array

        Returns:
            tuple: (r_peaks, lead_used, lead_quality, fallback_triggered)
        """
        # Handle 1D input (single lead)
        if len(ecg_signal.shape) == 1:
            r_peaks = self.detect_r_peaks_single_lead(ecg_signal)
            quality = self.assess_signal_quality(ecg_signal, r_peaks)
            return r_peaks, "unknown", quality, False

        # Multi-lead fallback logic
        best_peaks = None
        best_quality = 0.0
        best_lead_name = None
        best_lead_index = None
        fallback_triggered = False

        for lead_index, lead_name in self.LEAD_PRIORITY:
            if lead_index >= ecg_signal.shape[1]:
                continue  # Skip if lead doesn't exist

            signal = ecg_signal[:, lead_index]

            # Detect R-peaks
            r_peaks = self.detect_r_peaks_single_lead(signal)

            # Assess quality
            quality = self.assess_signal_quality(signal, r_peaks)

            # Track best lead
            if quality > best_quality:
                best_quality = quality
                best_peaks = r_peaks
                best_lead_name = lead_name
                best_lead_index = lead_index

            # Early exit if quality is excellent (>0.8) for primary lead (II)
            if lead_name == "II" and quality > 0.8:
                return r_peaks, lead_name, quality, False

            # If we've moved past Lead II, fallback was triggered
            if lead_name != "II":
                fallback_triggered = True

        # Return best result
        if best_peaks is not None:
            return best_peaks, best_lead_name, best_quality, fallback_triggered
        else:
            # Extreme fallback: return empty peaks
            return np.array([]), "none", 0.0, True

    def calculate_bpm(self, r_peak_indices):
        if len(r_peak_indices) < 2:
            return 60.0, []

        rr_intervals_samples = np.diff(r_peak_indices)
        rr_intervals_ms = (rr_intervals_samples / self.fs) * 1000

        hr_per_interval = 60000 / rr_intervals_ms
        median_bpm = np.median(hr_per_interval)

        return float(median_bpm), rr_intervals_ms.tolist()

    def get_beat_timestamps(self, r_peak_indices):
        return (r_peak_indices / self.fs).tolist()

    def analyze(self, ecg_signal):
        """
        Complete analysis in one call with multi-lead fallback

        Returns:
            dict: {
                'bpm': float,
                'rr_intervals_ms': list,
                'beat_timestamps': list,
                'r_peak_count': int,
                'lead_used': str,
                'lead_quality': float,
                'fallback_triggered': bool
            }
        """
        r_peaks, lead_used, lead_quality, fallback_triggered = self.detect_r_peaks(ecg_signal)
        bpm, rr_intervals = self.calculate_bpm(r_peaks)
        timestamps = self.get_beat_timestamps(r_peaks)

        return {
            'bpm': round(bpm, 1),
            'rr_intervals_ms': [round(rr, 1) for rr in rr_intervals],
            'beat_timestamps': [round(t, 2) for t in timestamps],
            'r_peak_count': len(r_peaks),
            'lead_used': lead_used,
            'lead_quality': round(lead_quality, 2),
            'fallback_triggered': fallback_triggered
        }