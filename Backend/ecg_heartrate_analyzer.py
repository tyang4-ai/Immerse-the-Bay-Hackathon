import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

class ECGHeartRateAnalyzer:
    def __init__(self, sampling_rate=400):
        self.fs = sampling_rate

    def bandpass_filter(self, signal, lowcut=0.5, highcut=40):
        nyquist = 0.5 * self.fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(2, [low, high], btype='band')
        return filtfilt(b, a, signal)

    def detect_r_peaks(self, ecg_signal):
        """
        Args:
            ecg_signal: (4096, 12) array or 1D array

        Returns:
            List of R-peak sample indices
        """
        # Use lead II for detection
        if len(ecg_signal.shape) > 1:
            signal = ecg_signal[:, 1]  # Lead II
        else:
            signal = ecg_signal

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
        Complete analysis in one call

        Returns:
            dict: {
                'bpm': float,
                'rr_intervals_ms': list,
                'beat_timestamps': list,
                'r_peak_count': int
            }
        """
        r_peaks = self.detect_r_peaks(ecg_signal)
        bpm, rr_intervals = self.calculate_bpm(r_peaks)
        timestamps = self.get_beat_timestamps(r_peaks)

        return {
            'bpm': round(bpm, 1),
            'rr_intervals_ms': [round(rr, 1) for rr in rr_intervals],
            'beat_timestamps': [round(t, 2) for t in timestamps],
            'r_peak_count': len(r_peaks)
        }