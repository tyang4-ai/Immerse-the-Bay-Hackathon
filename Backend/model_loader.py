import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import os
import json

from logger import model_logger


class ECGModelLoader:
    def __init__(self, model_path='model/model.hdf5'):
        self.model_path = model_path
        self.model = None
        self.simulation_mode = False  # Fallback mode flag
        self.condition_names = [
            '1st_degree_AV_block',
            'RBBB',
            'LBBB',
            'sinus_bradycardia',
            'atrial_fibrillation',
            'sinus_tachycardia'
        ]

        # Fallback predictions (used when model not loaded)
        self.fallback_predictions = self._load_fallback_data()

    def _load_fallback_data(self):
        """Load canned predictions from dummy_data for fallback mode"""
        fallback_path = 'dummy_data/sample_normal.json'

        try:
            if os.path.exists(fallback_path):
                with open(fallback_path, 'r') as f:
                    data = json.load(f)
                    return data.get('predictions', self._get_default_fallback())
            else:
                model_logger.warning(f"Fallback data not found at {fallback_path}, using defaults")
                return self._get_default_fallback()
        except Exception as e:
            model_logger.warning(f"Could not load fallback data: {e}, using defaults")
            return self._get_default_fallback()

    def _get_default_fallback(self):
        """Get default fallback predictions (normal sinus rhythm)"""
        return {
            '1st_degree_AV_block': 0.02,
            'RBBB': 0.01,
            'LBBB': 0.01,
            'sinus_bradycardia': 0.05,
            'atrial_fibrillation': 0.01,
            'sinus_tachycardia': 0.03
        }

    def load_model(self):
        """
        Load TensorFlow model with safety nets

        Returns:
            bool: True if model loaded, False if running in fallback mode
        """
        if not os.path.exists(self.model_path):
            model_logger.error(f"Model file not found: {self.model_path}")
            model_logger.info("Entering SIMULATION MODE - will serve cached predictions")
            self.simulation_mode = True
            return False

        try:
            model_logger.info(f"Loading ECG model from {self.model_path}...")
            self.model = load_model(self.model_path, compile=False)
            self.model.compile(loss='binary_crossentropy', optimizer='adam')

            # Warmup prediction to catch any model issues
            dummy_input = np.random.randn(1, 4096, 12).astype(np.float32)
            _ = self.model.predict(dummy_input, verbose=0)

            model_logger.info(f"ECG model loaded successfully from {self.model_path}")
            self.simulation_mode = False
            return True

        except Exception as e:
            model_logger.error(f"Failed to load model: {str(e)}")
            model_logger.info("Entering SIMULATION MODE - will serve cached predictions")
            self.simulation_mode = True
            self.model = None
            return False

    def predict(self, ecg_signal):
        """
        Predict ECG conditions with fallback support

        Args:
            ecg_signal: numpy array (4096, 12) or (1, 4096, 12)

        Returns:
            dict: {condition_name: probability}
        """
        # Fallback mode: return canned predictions
        if self.model is None or self.simulation_mode:
            model_logger.warning("Model not available - returning fallback predictions")
            return self.fallback_predictions.copy()

        try:
            # Ensure correct shape
            if ecg_signal.shape == (4096, 12):
                ecg_signal = np.expand_dims(ecg_signal, axis=0)

            # Validate input
            if np.isnan(ecg_signal).any() or np.isinf(ecg_signal).any():
                model_logger.warning("Invalid input detected (NaN/Inf) - returning fallback")
                return self.fallback_predictions.copy()

            # Run inference
            predictions = self.model.predict(ecg_signal, verbose=0)[0]

            # Validate predictions
            if np.isnan(predictions).any() or np.isinf(predictions).any():
                model_logger.error("Model returned invalid predictions - using fallback")
                return self.fallback_predictions.copy()

            # Format as dict
            result = {
                name: float(prob)
                for name, prob in zip(self.condition_names, predictions)
            }

            model_logger.debug(f"Prediction successful: top={max(result, key=result.get)}")
            return result

        except Exception as e:
            model_logger.error(f"Prediction failed: {str(e)} - using fallback")
            return self.fallback_predictions.copy()

    def get_top_condition(self, predictions_dict):
        """
        Get the most likely condition

        Args:
            predictions_dict: {condition: probability}

        Returns:
            tuple: (condition_name, confidence)
        """
        if not predictions_dict:
            model_logger.warning("Empty predictions dict - using default")
            return "unknown", 0.0

        top_condition = max(predictions_dict, key=predictions_dict.get)
        confidence = predictions_dict[top_condition]

        return top_condition, confidence


# Test module
if __name__ == '__main__':
    print("Testing ECGModelLoader...")

    loader = ECGModelLoader()
    loaded = loader.load_model()

    print(f"Model loaded: {loaded}")
    print(f"Simulation mode: {loader.simulation_mode}")

    # Test prediction with random data
    test_signal = np.random.randn(4096, 12).astype(np.float32)
    predictions = loader.predict(test_signal)

    print(f"\nPredictions: {predictions}")

    top_condition, confidence = loader.get_top_condition(predictions)
    print(f"Top condition: {top_condition} ({confidence:.2%})")