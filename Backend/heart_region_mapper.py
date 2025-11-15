"""
Heart Region Mapper

Maps ECG condition predictions to anatomical heart regions with severity scores,
colors, and electrical activation timing for VR visualization.

Author: Backend Developer 2
Project: HoloHuman XR - Immerse the Bay 2025
"""

import numpy as np


class HeartRegionMapper:
    """
    Maps ECG conditions to 10 anatomical heart regions.

    Regions:
    - sa_node: Sinoatrial node (pacemaker)
    - ra: Right atrium
    - la: Left atrium
    - av_node: Atrioventricular node
    - bundle_his: Bundle of His
    - rbbb: Right bundle branch
    - lbbb: Left bundle branch
    - purkinje: Purkinje fibers
    - rv: Right ventricle
    - lv: Left ventricle
    """

    def __init__(self):
        # Define normal electrical activation timing (milliseconds)
        self.normal_activation_delays = {
            'sa_node': 0,        # Fires first
            'ra': 25,            # Right atrium
            'la': 30,            # Left atrium
            'av_node': 50,       # AV node
            'bundle_his': 150,   # Bundle of His
            'rbbb': 160,         # Right bundle branch
            'lbbb': 160,         # Left bundle branch
            'purkinje': 180,     # Purkinje fibers
            'rv': 200,           # Right ventricle
            'lv': 200            # Left ventricle
        }

        # Define condition → region mapping with severity multipliers
        self.condition_region_map = {
            'RBBB': {
                'rbbb': 1.0,      # Right bundle branch most affected
                'rv': 0.7,        # Right ventricle secondarily affected
                'purkinje': 0.4   # Purkinje fibers affected
            },
            'LBBB': {
                'lbbb': 1.0,      # Left bundle branch most affected
                'lv': 0.7,        # Left ventricle secondarily affected
                'purkinje': 0.4   # Purkinje fibers affected
            },
            'sinus_bradycardia': {
                'sa_node': 1.0,   # SA node firing slowly
                'ra': 0.2,        # Atria mildly affected
                'la': 0.2
            },
            'sinus_tachycardia': {
                'sa_node': 1.0,   # SA node firing rapidly
                'ra': 0.2,        # Atria mildly affected
                'la': 0.2
            },
            'atrial_fibrillation': {
                'ra': 1.0,        # Both atria severely affected
                'la': 1.0,
                'av_node': 0.75   # AV node stressed by irregular input
            },
            '1st_degree_AV_block': {
                'av_node': 1.0,   # AV node conduction delayed
                'bundle_his': 0.5 # Bundle of His mildly affected
            }
        }

        # Abnormal activation delays for conditions
        self.abnormal_delays = {
            'RBBB': {
                'rbbb': 320,      # Right bundle severely delayed
                'rv': 360,        # Right ventricle delayed
                'purkinje': 234   # Purkinje modified timing
            },
            'LBBB': {
                'lbbb': 320,      # Left bundle severely delayed
                'lv': 360,        # Left ventricle delayed
                'purkinje': 234   # Purkinje modified timing
            },
            'atrial_fibrillation': {
                'ra': 0,          # Chaotic, no ordered activation
                'la': 0,          # Chaotic, no ordered activation
                'av_node': 65     # Irregular AV conduction
            }
        }

    def severity_to_color(self, severity):
        """
        Convert severity (0.0-1.0) to RGB color on spectrum:
        Green (healthy) → Yellow → Orange → Red (critical)

        Args:
            severity (float): 0.0 (healthy) to 1.0 (critical)

        Returns:
            list: [r, g, b] values in 0.0-1.0 range
        """
        severity = np.clip(severity, 0.0, 1.0)

        if severity < 0.25:
            # Green → Yellow (0.0 - 0.25)
            t = severity / 0.25
            r = t
            g = 1.0
            b = 0.0
        elif severity < 0.50:
            # Yellow → Orange (0.25 - 0.50)
            t = (severity - 0.25) / 0.25
            r = 1.0
            g = 1.0 - (t * 0.35)  # 1.0 → 0.65
            b = 0.0
        elif severity < 0.75:
            # Orange → Red (0.50 - 0.75)
            t = (severity - 0.50) / 0.25
            r = 1.0
            g = 0.65 - (t * 0.65)  # 0.65 → 0.0
            b = 0.0
        else:
            # Deep Red (0.75 - 1.0)
            r = 1.0
            g = 0.0
            b = 0.0

        return [round(r, 3), round(g, 3), round(b, 3)]

    def calculate_region_severity(self, region_name, predictions_dict):
        """
        Calculate severity for a single region based on all conditions.

        Args:
            region_name (str): Name of anatomical region
            predictions_dict (dict): {condition_name: probability}

        Returns:
            tuple: (severity, list of affecting conditions)
        """
        severity = 0.0
        affecting_conditions = []

        for condition, probability in predictions_dict.items():
            if condition in self.condition_region_map:
                region_map = self.condition_region_map[condition]
                if region_name in region_map:
                    multiplier = region_map[region_name]
                    contribution = probability * multiplier
                    severity = max(severity, contribution)  # Use max, not sum
                    if probability > 0.05:  # Only list if significant
                        affecting_conditions.append(condition)

        return round(severity, 3), affecting_conditions

    def get_activation_delay(self, region_name, predictions_dict):
        """
        Get activation delay for region, accounting for abnormalities.

        Args:
            region_name (str): Name of anatomical region
            predictions_dict (dict): {condition_name: probability}

        Returns:
            float: Activation delay in milliseconds
        """
        # Start with normal delay
        delay = self.normal_activation_delays[region_name]

        # Check for abnormal conditions that modify timing
        for condition, probability in predictions_dict.items():
            if probability > 0.5:  # Only apply if condition is likely
                if condition in self.abnormal_delays:
                    if region_name in self.abnormal_delays[condition]:
                        delay = self.abnormal_delays[condition][region_name]

        return delay

    def get_region_health_status(self, predictions_dict):
        """
        Generate complete health status for all 10 anatomical regions.

        Args:
            predictions_dict (dict): {condition_name: probability}
                Example: {
                    '1st_degree_AV_block': 0.08,
                    'RBBB': 0.89,
                    'LBBB': 0.02,
                    'sinus_bradycardia': 0.12,
                    'atrial_fibrillation': 0.05,
                    'sinus_tachycardia': 0.18
                }

        Returns:
            dict: {
                region_name: {
                    'severity': float,
                    'color': [r, g, b],
                    'activation_delay_ms': float,
                    'affected_by': [condition_names]
                }
            }
        """
        region_health = {}

        for region_name in self.normal_activation_delays.keys():
            # Calculate severity and affecting conditions
            severity, affecting_conditions = self.calculate_region_severity(
                region_name, predictions_dict
            )

            # Convert severity to color
            color = self.severity_to_color(severity)

            # Get activation delay
            activation_delay = self.get_activation_delay(region_name, predictions_dict)

            region_health[region_name] = {
                'severity': severity,
                'color': color,
                'activation_delay_ms': activation_delay,
                'affected_by': affecting_conditions
            }

        return region_health

    def get_activation_sequence(self, region_health):
        """
        Generate activation sequence sorted by timing.

        Args:
            region_health (dict): Output from get_region_health_status()

        Returns:
            list: [[region_name, delay_ms], ...] sorted by delay
        """
        # Extract (region, delay) pairs
        sequence = [
            [region_name, data['activation_delay_ms']]
            for region_name, data in region_health.items()
        ]

        # Sort by activation delay
        sequence.sort(key=lambda x: x[1])

        return sequence


# Example usage and testing
if __name__ == '__main__':
    print("Testing Heart Region Mapper...")
    print("=" * 60)

    # Test 1: RBBB condition
    print("\nTest 1: Right Bundle Branch Block (RBBB)")
    print("-" * 60)
    mapper = HeartRegionMapper()

    test_predictions = {
        '1st_degree_AV_block': 0.08,
        'RBBB': 0.89,
        'LBBB': 0.02,
        'sinus_bradycardia': 0.12,
        'atrial_fibrillation': 0.05,
        'sinus_tachycardia': 0.18
    }

    region_health = mapper.get_region_health_status(test_predictions)
    activation_sequence = mapper.get_activation_sequence(region_health)

    print(f"RBBB region severity: {region_health['rbbb']['severity']}")
    print(f"RBBB region color: {region_health['rbbb']['color']}")
    print(f"RBBB activation delay: {region_health['rbbb']['activation_delay_ms']} ms")
    print(f"Right ventricle severity: {region_health['rv']['severity']}")

    print("\nActivation sequence:")
    for region, delay in activation_sequence:
        print(f"  {region:15} @ {delay:6.1f} ms")

    # Test 2: Atrial Fibrillation
    print("\n\nTest 2: Atrial Fibrillation")
    print("-" * 60)

    test_af = {
        '1st_degree_AV_block': 0.15,
        'RBBB': 0.08,
        'LBBB': 0.04,
        'sinus_bradycardia': 0.03,
        'atrial_fibrillation': 0.92,
        'sinus_tachycardia': 0.25
    }

    region_health_af = mapper.get_region_health_status(test_af)

    print(f"Right atrium severity: {region_health_af['ra']['severity']}")
    print(f"Right atrium color: {region_health_af['ra']['color']}")
    print(f"Left atrium severity: {region_health_af['la']['severity']}")
    print(f"AV node severity: {region_health_af['av_node']['severity']}")

    # Test 3: Color spectrum
    print("\n\nTest 3: Color Spectrum")
    print("-" * 60)
    for severity in [0.0, 0.25, 0.5, 0.75, 1.0]:
        color = mapper.severity_to_color(severity)
        print(f"Severity {severity:.2f}: RGB {color}")

    print("\n" + "=" * 60)
    print("All tests complete!")