import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import os

class ECGModelLoader:
    def __init__(self, model_path='model/model.hdf5'):
        self.model_path = model_path
        self.model = None
        self.condition_names = [
            '1st_degree_AV_block',
            'RBBB',
            'LBBB',
            'sinus_bradycardia',
            'atrial_fibrillation',
            'sinus_tachycardia'
        ]

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path, compile=False)
            self.model.compile(loss='binary_crossentropy', optimizer='adam')
            print(f"ECG model loaded from {self.model_path}")
            return True
        else:
            print(f"ERROR: Model file not found at {self.model_path}")
            return False

    def predict(self, ecg_signal):
        """
        Args:
            ecg_signal: numpy array (4096, 12) or (1, 4096, 12)

        Returns:
            dict: {condition_name: probability}
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Ensure correct shape
        if ecg_signal.shape == (4096, 12):
            ecg_signal = np.expand_dims(ecg_signal, axis=0)

        # Run inference
        predictions = self.model.predict(ecg_signal, verbose=0)[0]

        # Format as dict
        return {
            name: float(prob)
            for name, prob in zip(self.condition_names, predictions)
        }

    def get_top_condition(self, predictions_dict):
        top_condition = max(predictions_dict, key=predictions_dict.get)
        confidence = predictions_dict[top_condition]
        return top_condition, confidence