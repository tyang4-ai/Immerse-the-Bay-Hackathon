"""
LLM Medical Interpreter

Uses Claude API to generate natural language medical explanations from ECG analysis.
Provides patient-friendly explanations, clinical notes, and VR visualization suggestions.

Author: Backend Developer 2
Project: HoloHuman XR - Immerse the Bay 2025
"""

import os
import json
from anthropic import Anthropic


class LLMMedicalInterpreter:
    """
    Interprets ECG analysis results using Claude LLM API.

    Generates:
    - Plain English summaries
    - Patient-friendly explanations
    - Clinical notes for healthcare providers
    - VR visualization suggestions
    """

    def __init__(self, api_key=None):
        """
        Initialize LLM interpreter.

        Args:
            api_key (str, optional): Anthropic API key.
                                     If None, reads from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None

        if self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                print("[LLM] Claude API client initialized")
            except Exception as e:
                print(f"[LLM] Warning: Failed to initialize Claude client: {e}")
                print("[LLM] Will use fallback mode")
        else:
            print("[LLM] No API key found - using fallback mode")

        # Fallback hardcoded explanations
        self.fallback_explanations = {
            'RBBB': {
                'summary': "Right bundle branch block detected - the electrical signal to your right ventricle is significantly delayed.",
                'severity': 'moderate',
                'patient_explanation': "Right Bundle Branch Block (RBBB) means the electrical pathway that signals your right ventricle to contract is blocked or delayed. Instead of both ventricles contracting together, your left ventricle contracts first, and then the signal slowly spreads to activate the right ventricle. This can be a normal finding in some people, but it's important to have it evaluated by a cardiologist."
            },
            'LBBB': {
                'summary': "Left bundle branch block detected - the electrical signal to your left ventricle is significantly delayed.",
                'severity': 'moderate',
                'patient_explanation': "Left Bundle Branch Block (LBBB) means the electrical pathway to your left ventricle is blocked. This causes your heart chambers to contract out of sync, which can reduce pumping efficiency. It requires medical evaluation to determine the underlying cause."
            },
            'atrial_fibrillation': {
                'summary': "Atrial fibrillation detected - the upper chambers of your heart are beating irregularly and chaotically instead of in a coordinated rhythm.",
                'severity': 'high',
                'patient_explanation': "Atrial Fibrillation (AFib) is a serious heart rhythm disorder where the upper chambers of your heart (atria) quiver rapidly and irregularly instead of contracting normally. This irregular rhythm significantly increases your risk of stroke because blood can pool in the atria and form clots. AFib requires immediate medical attention."
            },
            'sinus_bradycardia': {
                'summary': "Sinus bradycardia detected - your heart is beating slower than normal.",
                'severity': 'low',
                'patient_explanation': "Sinus bradycardia means your heart is beating slower than the typical range (60-100 BPM). This can be completely normal, especially if you're an athlete or physically fit. However, if you're experiencing symptoms like dizziness, fatigue, or shortness of breath, you should consult a doctor."
            },
            'sinus_tachycardia': {
                'summary': "Sinus tachycardia detected - your heart is beating faster than normal.",
                'severity': 'low',
                'patient_explanation': "Sinus tachycardia means your heart is beating faster than the normal resting range (typically >100 BPM). This is often a normal response to exercise, stress, fever, or caffeine. However, if it persists at rest or you have symptoms, medical evaluation is recommended."
            },
            '1st_degree_AV_block': {
                'summary': "1st degree AV block detected - there is a slight delay in the electrical signal between your atria and ventricles.",
                'severity': 'low',
                'patient_explanation': "First degree AV block means the electrical signal traveling from your atria to your ventricles is slightly delayed. This is usually benign and often requires no treatment. It's commonly found in athletes and healthy individuals."
            },
            'normal': {
                'summary': "Normal sinus rhythm with healthy electrical conduction throughout the heart.",
                'severity': 'low',
                'patient_explanation': "Great news! Your ECG shows a normal sinus rhythm. This means your heart's electrical system is functioning exactly as it should. The SA node (your heart's natural pacemaker) is firing at a healthy rate, and the electrical signal is traveling normally through all parts of your heart."
            }
        }

    def build_prompt(self, predictions_dict, heart_rate_data, region_health,
                    top_condition, confidence):
        """
        Build structured prompt for Claude API.

        Args:
            predictions_dict (dict): {condition: probability}
            heart_rate_data (dict): {bpm, rr_intervals_ms, beat_timestamps, r_peak_count}
            region_health (dict): {region: {severity, color, ...}}
            top_condition (str): Most likely condition
            confidence (float): Confidence score

        Returns:
            str: Formatted prompt
        """
        # Find most affected region
        most_affected_region = max(
            region_health.items(),
            key=lambda x: x[1]['severity']
        )[0] if region_health else "none"

        most_affected_severity = region_health[most_affected_region]['severity'] if region_health else 0.0

        prompt = f"""You are a medical AI assistant analyzing ECG (electrocardiogram) results. Generate a comprehensive medical interpretation in JSON format.

**ECG Analysis Data:**

Top Condition: {top_condition}
Confidence: {confidence:.1%}
Heart Rate: {heart_rate_data.get('bpm', 'N/A')} BPM

All Condition Probabilities:
{json.dumps(predictions_dict, indent=2)}

Most Affected Anatomical Region: {most_affected_region}
Most Affected Region Severity: {most_affected_severity:.2f} (0.0 = healthy, 1.0 = critical)

**Task:**
Provide a medical interpretation with the following structure (respond with ONLY valid JSON):

{{
  "plain_english_summary": "<2-3 sentence overview for general audience>",
  "severity_assessment": {{
    "overall": "<low|moderate|high>",
    "regions": {{
      "most_affected_region": "{most_affected_region}",
      "severity_explanation": "<1-2 sentences explaining why this region is affected>"
    }}
  }},
  "patient_explanation": "<Detailed patient-friendly explanation (3-5 sentences). Explain what the condition means, why it happens, and what the patient should do.>",
  "clinical_notes": "<Technical medical notes for healthcare providers. Include ECG findings, recommendations, and next steps.>",
  "visualization_suggestions": {{
    "highlight_regions": ["<region1>", "<region2>"],
    "recommended_view": "<frontal|atrial_focus|electrical_pathway>",
    "animation_speed": "<slow|normal|fast>",
    "color_emphasis": "<Describe how colors should be used in VR visualization>"
  }}
}}

**Important:**
- Be medically accurate but avoid unnecessary alarm
- For low-severity conditions, reassure appropriately
- For high-severity conditions, emphasize importance of medical attention
- Suggest 2-3 regions to highlight in VR visualization
- Keep explanations clear and jargon-free for patients"""

        return prompt

    def parse_llm_response(self, response_text):
        """
        Parse Claude API response and extract JSON.

        Args:
            response_text (str): Raw response from Claude

        Returns:
            dict: Parsed interpretation
        """
        try:
            # Try to extract JSON from response
            # Claude might wrap JSON in markdown code blocks
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()

            interpretation = json.loads(response_text)
            return interpretation

        except json.JSONDecodeError as e:
            print(f"[LLM] JSON parsing error: {e}")
            print(f"[LLM] Response text: {response_text[:200]}...")
            return None

    def get_fallback_interpretation(self, top_condition, confidence, heart_rate_data,
                                   region_health):
        """
        Generate fallback interpretation when API is unavailable.

        Args:
            top_condition (str): Most likely condition
            confidence (float): Confidence score
            heart_rate_data (dict): Heart rate data
            region_health (dict): Region health data

        Returns:
            dict: Fallback interpretation
        """
        # Get fallback text for condition
        fallback = self.fallback_explanations.get(
            top_condition,
            self.fallback_explanations['normal']
        )

        # Find most affected region
        most_affected = max(
            region_health.items(),
            key=lambda x: x[1]['severity']
        ) if region_health else ('none', {'severity': 0.0})

        most_affected_region = most_affected[0]
        most_affected_severity = most_affected[1]['severity']

        # Build interpretation
        interpretation = {
            'plain_english_summary': fallback['summary'],
            'severity_assessment': {
                'overall': fallback['severity'],
                'regions': {
                    'most_affected_region': most_affected_region,
                    'severity_explanation': f"The {most_affected_region.replace('_', ' ')} shows severity of {most_affected_severity:.2f}."
                }
            },
            'patient_explanation': fallback['patient_explanation'],
            'clinical_notes': f"ECG findings: {top_condition} with {confidence:.1%} confidence. Heart rate: {heart_rate_data.get('bpm', 'N/A')} BPM. Automated analysis - clinical correlation recommended.",
            'visualization_suggestions': {
                'highlight_regions': [most_affected_region] if most_affected_region != 'none' else [],
                'recommended_view': 'electrical_pathway',
                'animation_speed': 'normal',
                'color_emphasis': f"Highlight {most_affected_region} based on severity."
            }
        }

        return interpretation

    def interpret_ecg_analysis(self, predictions_dict, heart_rate_data, region_health,
                               top_condition, confidence):
        """
        Generate complete medical interpretation.

        Args:
            predictions_dict (dict): {condition: probability}
            heart_rate_data (dict): {bpm, rr_intervals_ms, beat_timestamps, r_peak_count}
            region_health (dict): {region: {severity, color, ...}}
            top_condition (str): Most likely condition
            confidence (float): Confidence score

        Returns:
            dict: Complete interpretation with all fields
        """
        # Try Claude API first
        if self.client:
            try:
                prompt = self.build_prompt(
                    predictions_dict, heart_rate_data, region_health,
                    top_condition, confidence
                )

                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                response_text = message.content[0].text
                interpretation = self.parse_llm_response(response_text)

                if interpretation:
                    print("[LLM] Successfully generated interpretation via Claude API")
                    return interpretation
                else:
                    print("[LLM] Failed to parse Claude response, using fallback")

            except Exception as e:
                print(f"[LLM] Claude API error: {e}")
                print("[LLM] Falling back to hardcoded explanations")

        # Use fallback if API fails or not available
        print("[LLM] Using fallback interpretation")
        return self.get_fallback_interpretation(
            top_condition, confidence, heart_rate_data, region_health
        )


# Example usage and testing
if __name__ == '__main__':
    print("Testing LLM Medical Interpreter...")
    print("=" * 60)

    # Test data (RBBB case)
    test_predictions = {
        '1st_degree_AV_block': 0.08,
        'RBBB': 0.89,
        'LBBB': 0.02,
        'sinus_bradycardia': 0.12,
        'atrial_fibrillation': 0.05,
        'sinus_tachycardia': 0.18
    }

    test_heart_rate = {
        'bpm': 95.2,
        'rr_intervals_ms': [630.4, 631.0, 629.8],
        'beat_timestamps': [0.35, 0.98, 1.61],
        'r_peak_count': 16
    }

    test_region_health = {
        'sa_node': {'severity': 0.18, 'color': [0.72, 1.0, 0.0]},
        'rbbb': {'severity': 0.89, 'color': [1.0, 0.0, 0.0]},
        'rv': {'severity': 0.623, 'color': [1.0, 0.247, 0.0]}
    }

    # Test with fallback mode (no API key)
    print("\nTest 1: Fallback Mode (No API Key)")
    print("-" * 60)
    interpreter = LLMMedicalInterpreter(api_key=None)

    interpretation = interpreter.interpret_ecg_analysis(
        test_predictions,
        test_heart_rate,
        test_region_health,
        'RBBB',
        0.89
    )

    print(json.dumps(interpretation, indent=2))

    # Test with API (if key available)
    print("\n\nTest 2: Claude API Mode (if key available)")
    print("-" * 60)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print("[Testing with Claude API...]")
        interpreter_api = LLMMedicalInterpreter()

        interpretation_api = interpreter_api.interpret_ecg_analysis(
            test_predictions,
            test_heart_rate,
            test_region_health,
            'RBBB',
            0.89
        )

        print("\nPlain English Summary:")
        print(interpretation_api.get('plain_english_summary', 'N/A'))
        print("\nPatient Explanation:")
        print(interpretation_api.get('patient_explanation', 'N/A')[:200] + "...")
    else:
        print("No ANTHROPIC_API_KEY found - skipping API test")
        print("To test with Claude API:")
        print("  export ANTHROPIC_API_KEY=sk-ant-your-key-here")
        print("  python llm_medical_interpreter.py")

    print("\n" + "=" * 60)
    print("All tests complete!")
