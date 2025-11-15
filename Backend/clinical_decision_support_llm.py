"""
Clinical Decision Support LLM

Uses Claude API to provide expert-level clinical decision support for cardiologists.
Supports dual output modes:
- clinical_expert: Comprehensive decision support for doctors (differential diagnosis, workup, treatment)
- patient_education: Patient-friendly explanations (legacy mode)

Author: Backend Developer 2
Project: HoloHuman XR - Immerse the Bay 2025
"""

import os
import json
from anthropic import Anthropic


class ClinicalDecisionSupportLLM:
    """
    Provides clinical decision support using Claude LLM API.

    Supports two output modes:
    1. clinical_expert: Expert-focused clinical guidance for cardiologists
    2. patient_education: Patient-friendly explanations (legacy)
    """

    def __init__(self, api_key=None):
        """
        Initialize clinical decision support system.

        Args:
            api_key (str, optional): Anthropic API key.
                                     If None, reads from ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None

        if self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                print("[ClinicalLLM] Claude API client initialized")
            except Exception as e:
                print(f"[ClinicalLLM] Warning: Failed to initialize Claude client: {e}")
                print("[ClinicalLLM] Will use fallback mode")
        else:
            print("[ClinicalLLM] No API key found - using fallback mode")

        # Initialize fallback data for both modes
        self._init_patient_education_fallbacks()
        self._init_clinical_expert_fallbacks()

    def _init_patient_education_fallbacks(self):
        """Initialize patient education fallback explanations (legacy mode)."""
        self.patient_fallbacks = {
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

    def _init_clinical_expert_fallbacks(self):
        """Initialize clinical expert fallback guidance."""
        self.clinical_fallbacks = {
            'RBBB': {
                'urgency': 'routine',
                'primary_diagnosis': 'Isolated right bundle branch block (RBBB)',
                'differential': ['RV hypertrophy', 'Brugada syndrome (if ST elevation present)', 'ARVC (if epsilon waves)'],
                'workup': ['Transthoracic echocardiogram to assess RV size/function', 'If dyspnea: BNP, D-dimer to rule out PE/RV strain', 'Baseline troponin if chest pain present'],
                'treatment': ['No specific treatment for isolated RBBB', 'Treat underlying cause if identified'],
                'avoid': ['Avoid Class IC antiarrhythmics (may worsen conduction)'],
                'critical_alerts': []
            },
            'LBBB': {
                'urgency': 'urgent',
                'primary_diagnosis': 'Left bundle branch block (LBBB)',
                'differential': ['Acute MI (Sgarbossa criteria)', 'Cardiomyopathy', 'Progressive conduction disease'],
                'workup': ['Troponin (stat if chest pain)', 'Echocardiogram to assess LV function/EF', 'Compare with prior ECGs if available'],
                'treatment': ['If new onset + chest pain: Activate cath lab (STEMI equivalent)', 'CRT consideration if EF <35% with heart failure'],
                'avoid': ['Do not rule out MI based on ECG alone with LBBB'],
                'critical_alerts': ['New LBBB with chest pain is STEMI equivalent']
            },
            'atrial_fibrillation': {
                'urgency': 'urgent',
                'primary_diagnosis': 'Atrial fibrillation',
                'differential': ['AFib with RVR', 'Atrial flutter', 'Multifocal atrial tachycardia'],
                'workup': ['TSH, basic metabolic panel', 'Echocardiogram', 'CHA2DS2-VASc score calculation', 'HAS-BLED bleeding risk assessment'],
                'treatment': ['Rate control (beta-blocker, calcium channel blocker)', 'Rhythm control (cardioversion, antiarrhythmic)', 'Anticoagulation based on CHA2DS2-VASc score'],
                'avoid': ['Do not cardiovert if >48hrs without TEE or 3 weeks anticoagulation'],
                'critical_alerts': ['High stroke risk - assess CHA2DS2-VASc within 24 hours', 'If RVR with hypotension: consider urgent cardioversion']
            },
            'sinus_bradycardia': {
                'urgency': 'routine',
                'primary_diagnosis': 'Sinus bradycardia',
                'differential': ['Physiologic (athletes)', 'Medication-induced (beta-blockers, CCB)', 'Hypothyroidism', 'Sick sinus syndrome'],
                'workup': ['Medication review', 'TSH', 'Assess for symptoms (dizziness, syncope, fatigue)'],
                'treatment': ['None if asymptomatic', 'Adjust/discontinue causative medications', 'Pacemaker if symptomatic bradycardia unresponsive to treatment'],
                'avoid': ['Avoid additional rate-lowering medications unless necessary'],
                'critical_alerts': []
            },
            'sinus_tachycardia': {
                'urgency': 'routine',
                'primary_diagnosis': 'Sinus tachycardia',
                'differential': ['Physiologic response (pain, anxiety, fever)', 'Hypovolemia/dehydration', 'Hyperthyroidism', 'Pulmonary embolism'],
                'workup': ['Identify underlying cause', 'If persistent: TSH, CBC, basic metabolic panel', 'If dyspnea/chest pain: D-dimer, troponin'],
                'treatment': ['Treat underlying cause', 'Rarely requires direct rate control'],
                'avoid': ['Do not treat sinus tachycardia without addressing underlying cause'],
                'critical_alerts': []
            },
            '1st_degree_AV_block': {
                'urgency': 'routine',
                'primary_diagnosis': '1st degree AV block',
                'differential': ['Medication-induced (beta-blockers, CCB, digoxin)', 'Enhanced vagal tone', 'Progressive conduction disease'],
                'workup': ['Medication review', 'If progressive: serial ECGs', 'Consider EP study if high-grade AV block suspected'],
                'treatment': ['None for isolated 1st degree AV block', 'Adjust medications if causing symptoms'],
                'avoid': ['Avoid additional rate-lowering drugs unless necessary'],
                'critical_alerts': []
            },
            'normal': {
                'urgency': 'routine',
                'primary_diagnosis': 'Normal sinus rhythm',
                'differential': [],
                'workup': ['None required for isolated normal ECG'],
                'treatment': ['No treatment needed'],
                'avoid': [],
                'critical_alerts': []
            }
        }

    def build_clinical_expert_prompt(self, predictions_dict, heart_rate_data,
                                    region_health, top_condition, confidence):
        """
        Build prompt for clinical expert mode (cardiologist-focused).

        Returns:
            str: Formatted prompt for Claude API
        """
        most_affected_region = max(
            region_health.items(),
            key=lambda x: x[1]['severity']
        )[0] if region_health else "none"

        most_affected_severity = region_health[most_affected_region]['severity'] if region_health else 0.0

        prompt = f"""You are a cardiology AI assistant providing clinical decision support to an expert physician using an immersive VR ECG analysis system.

**AUDIENCE**: Board-certified cardiologist or emergency physician
**PURPOSE**: Clinical decision support, NOT patient education
**TONE**: Technical, evidence-based, actionable

**ECG Analysis Results:**

Top Condition: {top_condition}
Confidence: {confidence:.1%}
Heart Rate: {heart_rate_data.get('bpm', 'N/A')} BPM

All Condition Probabilities:
{json.dumps(predictions_dict, indent=2)}

Most Affected Anatomical Region: {most_affected_region}
Most Affected Region Severity: {most_affected_severity:.2f} (0.0 = healthy, 1.0 = critical)

**Your Task:**
Provide expert-level clinical analysis in JSON format with the following structure:

{{
  "differential_diagnosis": {{
    "primary_diagnosis": "<Most likely diagnosis>",
    "alternative_diagnoses": ["<Alternative 1>", "<Alternative 2>"],
    "reasoning": "<Explain probability combinations and clinical significance>",
    "probability_interpretation": "<Interpret what the probability values mean clinically>"
  }},

  "risk_assessment": {{
    "urgency": "<immediate|urgent|routine>",
    "stroke_risk": "<Assessment of stroke risk>",
    "sudden_death_risk": "<Assessment of sudden cardiac death risk>",
    "progression_risk": "<Risk of disease progression>",
    "risk_factors": ["<Key risk factor 1>", "<Key risk factor 2>"]
  }},

  "clinical_correlations": {{
    "expected_symptoms": ["<Symptom 1>", "<Symptom 2>"],
    "red_flags": ["<Warning sign 1>", "<Warning sign 2>"],
    "age_considerations": "<Age-appropriateness of findings>",
    "medication_effects": "<Potential medication influences on ECG>"
  }},

  "recommended_workup": {{
    "immediate_tests": ["<Test 1>", "<Test 2>"],
    "follow_up_tests": ["<Test 1>", "<Test 2>"],
    "specialist_referrals": ["<Specialty 1>", "<Specialty 2>"],
    "imaging": ["<Imaging 1>", "<Imaging 2>"]
  }},

  "treatment_considerations": {{
    "medications_to_consider": ["<Med 1 with rationale>", "<Med 2 with rationale>"],
    "medications_to_avoid": ["<Med 1 with reason>", "<Med 2 with reason>"],
    "device_therapy": "<Pacemaker/ICD/CRT candidacy assessment>",
    "procedural_options": ["<Procedure 1>", "<Procedure 2>"]
  }},

  "vr_visualization_strategy": {{
    "primary_view": "<electrical_pathway|chamber_focus|atrial_focus|custom>",
    "regions_to_emphasize": ["<region1>", "<region2>"],
    "animation_recommendations": "<Detailed animation strategy for VR>",
    "comparison_views": ["<Comparison 1>", "<Comparison 2>"],
    "teaching_points": ["<Teaching point 1>", "<Teaching point 2>"],
    "interactive_elements": ["<Interactive feature 1>", "<Interactive feature 2>"]
  }},

  "literature_references": {{
    "guidelines": ["<Guideline 1>", "<Guideline 2>"],
    "evidence": ["<Evidence 1>", "<Evidence 2>"],
    "clinical_pearls": ["<Pearl 1>", "<Pearl 2>"]
  }},

  "critical_alerts": ["<Alert 1 if any>", "<Alert 2 if any>"]
}}

**Important:**
- Use technical medical terminology - this is doctor-to-doctor communication
- Cite specific ECG criteria when applicable (Sgarbossa, Brugada, etc.)
- Be specific with measurements and thresholds
- Flag any need for immediate action
- Provide evidence-based recommendations
- Focus on actionable clinical pathways
- For VR: suggest specific visualization strategies to enhance diagnostic understanding

Respond with ONLY valid JSON matching this structure."""

        return prompt

    def build_patient_education_prompt(self, predictions_dict, heart_rate_data,
                                      region_health, top_condition, confidence):
        """
        Build prompt for patient education mode (legacy).

        Returns:
            str: Formatted prompt for Claude API
        """
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

    def get_clinical_expert_fallback(self, top_condition, confidence, heart_rate_data, region_health):
        """
        Generate clinical expert fallback when API unavailable.

        Returns:
            dict: Clinical decision support structure
        """
        fallback = self.clinical_fallbacks.get(
            top_condition,
            self.clinical_fallbacks['normal']
        )

        most_affected = max(
            region_health.items(),
            key=lambda x: x[1]['severity']
        ) if region_health else ('none', {'severity': 0.0})

        most_affected_region = most_affected[0]
        most_affected_severity = most_affected[1]['severity']

        return {
            'differential_diagnosis': {
                'primary_diagnosis': fallback['primary_diagnosis'],
                'alternative_diagnoses': fallback['differential'],
                'reasoning': f"ECG shows {top_condition} with {confidence:.1%} confidence. {most_affected_region.replace('_', ' ')} shows severity of {most_affected_severity:.2f}.",
                'probability_interpretation': f"High confidence ({confidence:.1%}) indicates clear ECG findings consistent with {top_condition}."
            },
            'risk_assessment': {
                'urgency': fallback['urgency'],
                'stroke_risk': 'Elevated - assess CHA2DS2-VASc score' if top_condition == 'atrial_fibrillation' else 'Not elevated',
                'sudden_death_risk': 'Low unless structural heart disease present',
                'progression_risk': 'Variable - depends on underlying cause',
                'risk_factors': [f"Heart rate: {heart_rate_data.get('bpm', 'N/A')} BPM", f"Most affected region: {most_affected_region}"]
            },
            'clinical_correlations': {
                'expected_symptoms': ['May be asymptomatic', 'Possible palpitations or fatigue'],
                'red_flags': ['Syncope', 'Chest pain', 'Dyspnea'],
                'age_considerations': 'Consider age-appropriate differential diagnosis',
                'medication_effects': 'Review current medications for QT prolongation, rate/rhythm effects'
            },
            'recommended_workup': {
                'immediate_tests': fallback['workup'][:2] if len(fallback['workup']) >= 2 else fallback['workup'],
                'follow_up_tests': fallback['workup'][2:] if len(fallback['workup']) > 2 else [],
                'specialist_referrals': ['Cardiology for risk stratification'] if fallback['urgency'] != 'routine' else [],
                'imaging': ['Transthoracic echocardiogram']
            },
            'treatment_considerations': {
                'medications_to_consider': fallback['treatment'],
                'medications_to_avoid': fallback['avoid'],
                'device_therapy': 'Consider if develops symptomatic bradycardia or high-grade AV block',
                'procedural_options': []
            },
            'vr_visualization_strategy': {
                'primary_view': 'electrical_pathway',
                'regions_to_emphasize': [most_affected_region] if most_affected_region != 'none' else [],
                'animation_recommendations': f"Animate sequential activation highlighting {most_affected_region} with {most_affected_severity:.2f} severity. Use slow-motion to demonstrate conduction abnormalities.",
                'comparison_views': ['Normal activation vs. current pathology', 'Side-by-side comparison'],
                'teaching_points': [
                    f"Explain why {most_affected_region.replace('_', ' ')} is most affected",
                    f"Demonstrate electrical pathway changes in {top_condition}",
                    'Show compensatory mechanisms if present'
                ],
                'interactive_elements': ['Toggle normal vs abnormal activation', 'Adjustable animation speed', 'Region-specific annotations']
            },
            'literature_references': {
                'guidelines': ['2018 ACC/AHA/HRS Guideline on ECG interpretation', '2021 ESC Guidelines on cardiac pacing'],
                'evidence': ['Evidence-based recommendations from major cardiology societies'],
                'clinical_pearls': [f"Isolated {top_condition} management depends on clinical context", 'Always correlate ECG findings with symptoms']
            },
            'critical_alerts': fallback['critical_alerts']
        }

    def get_patient_education_fallback(self, top_condition, confidence, heart_rate_data, region_health):
        """
        Generate patient education fallback when API unavailable (legacy).

        Returns:
            dict: Patient education structure
        """
        fallback = self.patient_fallbacks.get(
            top_condition,
            self.patient_fallbacks['normal']
        )

        most_affected = max(
            region_health.items(),
            key=lambda x: x[1]['severity']
        ) if region_health else ('none', {'severity': 0.0})

        most_affected_region = most_affected[0]
        most_affected_severity = most_affected[1]['severity']

        return {
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

    def parse_llm_response(self, response_text):
        """
        Parse Claude API response and extract JSON.

        Args:
            response_text (str): Raw response from Claude

        Returns:
            dict: Parsed interpretation or None if parsing fails
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
            print(f"[ClinicalLLM] JSON parsing error: {e}")
            print(f"[ClinicalLLM] Response text: {response_text[:200]}...")
            return None

    def analyze(self, predictions_dict, heart_rate_data, region_health,
                top_condition, confidence, output_mode='clinical_expert'):
        """
        Generate clinical interpretation.

        Args:
            predictions_dict (dict): {condition: probability}
            heart_rate_data (dict): {bpm, rr_intervals_ms, beat_timestamps, r_peak_count}
            region_health (dict): {region: {severity, color, ...}}
            top_condition (str): Most likely condition
            confidence (float): Confidence score
            output_mode (str): 'clinical_expert' or 'patient_education'

        Returns:
            dict: Complete interpretation based on output_mode
        """
        if output_mode not in ['clinical_expert', 'patient_education']:
            raise ValueError(f"Invalid output_mode: {output_mode}. Must be 'clinical_expert' or 'patient_education'")

        # Build appropriate prompt
        if output_mode == 'clinical_expert':
            prompt = self.build_clinical_expert_prompt(
                predictions_dict, heart_rate_data, region_health,
                top_condition, confidence
            )
        else:
            prompt = self.build_patient_education_prompt(
                predictions_dict, heart_rate_data, region_health,
                top_condition, confidence
            )

        # Try Claude API first
        if self.client:
            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2500 if output_mode == 'clinical_expert' else 1500,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                response_text = message.content[0].text
                interpretation = self.parse_llm_response(response_text)

                if interpretation:
                    print(f"[ClinicalLLM] Successfully generated {output_mode} interpretation via Claude API")
                    return interpretation
                else:
                    print(f"[ClinicalLLM] Failed to parse Claude response, using fallback")

            except Exception as e:
                print(f"[ClinicalLLM] Claude API error: {e}")
                print(f"[ClinicalLLM] Falling back to hardcoded {output_mode} guidance")

        # Use fallback if API fails or not available
        print(f"[ClinicalLLM] Using fallback {output_mode} interpretation")

        if output_mode == 'clinical_expert':
            return self.get_clinical_expert_fallback(
                top_condition, confidence, heart_rate_data, region_health
            )
        else:
            return self.get_patient_education_fallback(
                top_condition, confidence, heart_rate_data, region_health
            )

    # Legacy method for backward compatibility
    def interpret_ecg_analysis(self, predictions_dict, heart_rate_data, region_health,
                               top_condition, confidence):
        """
        Legacy method - defaults to patient education mode.
        For new code, use analyze() with explicit output_mode parameter.
        """
        return self.analyze(predictions_dict, heart_rate_data, region_health,
                          top_condition, confidence, output_mode='patient_education')


# Example usage and testing
if __name__ == '__main__':
    print("Testing Clinical Decision Support LLM...")
    print("=" * 80)

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
        'sa_node': {'severity': 0.18, 'color': [0.72, 1.0, 0.0], 'activation_delay_ms': 0},
        'rbbb': {'severity': 0.89, 'color': [1.0, 0.0, 0.0], 'activation_delay_ms': 320},
        'rv': {'severity': 0.623, 'color': [1.0, 0.247, 0.0], 'activation_delay_ms': 360}
    }

    # Initialize system
    clinical_llm = ClinicalDecisionSupportLLM(api_key=None)

    # Test 1: Clinical Expert Mode (NEW)
    print("\n" + "=" * 80)
    print("Test 1: Clinical Expert Mode (Doctor-Focused)")
    print("=" * 80)

    expert_analysis = clinical_llm.analyze(
        test_predictions,
        test_heart_rate,
        test_region_health,
        'RBBB',
        0.89,
        output_mode='clinical_expert'
    )

    print("\n[Differential Diagnosis]")
    print(f"Primary: {expert_analysis['differential_diagnosis']['primary_diagnosis']}")
    print(f"Alternatives: {', '.join(expert_analysis['differential_diagnosis']['alternative_diagnoses'])}")

    print("\n[Risk Assessment]")
    print(f"Urgency: {expert_analysis['risk_assessment']['urgency'].upper()}")
    print(f"Stroke Risk: {expert_analysis['risk_assessment']['stroke_risk']}")

    print("\n[Recommended Workup]")
    for test in expert_analysis['recommended_workup']['immediate_tests']:
        print(f"  - {test}")

    print("\n[VR Visualization Strategy]")
    print(f"Primary View: {expert_analysis['vr_visualization_strategy']['primary_view']}")
    print(f"Emphasize: {', '.join(expert_analysis['vr_visualization_strategy']['regions_to_emphasize'])}")

    print("\n[Critical Alerts]")
    if expert_analysis['critical_alerts']:
        for alert in expert_analysis['critical_alerts']:
            print(f"  [!] {alert}")
    else:
        print("  [OK] No critical alerts")

    # Test 2: Patient Education Mode (LEGACY)
    print("\n" + "=" * 80)
    print("Test 2: Patient Education Mode (Legacy - Patient-Focused)")
    print("=" * 80)

    patient_analysis = clinical_llm.analyze(
        test_predictions,
        test_heart_rate,
        test_region_health,
        'RBBB',
        0.89,
        output_mode='patient_education'
    )

    print("\n[Plain English Summary]")
    print(patient_analysis['plain_english_summary'])

    print("\n[Patient Explanation]")
    print(patient_analysis['patient_explanation'][:200] + "...")

    # Test 3: API Mode (if key available)
    print("\n" + "=" * 80)
    print("Test 3: Claude API Mode (if key available)")
    print("=" * 80)

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print("[Testing with Claude API in clinical expert mode...]")
        llm_with_api = ClinicalDecisionSupportLLM()

        api_analysis = llm_with_api.analyze(
            test_predictions,
            test_heart_rate,
            test_region_health,
            'RBBB',
            0.89,
            output_mode='clinical_expert'
        )

        print("\n[API Response - Differential Diagnosis]")
        print(json.dumps(api_analysis['differential_diagnosis'], indent=2))
    else:
        print("No ANTHROPIC_API_KEY found - skipping API test")
        print("To test with Claude API:")
        print("  Set environment variable: ANTHROPIC_API_KEY=sk-ant-your-key-here")
        print("  python clinical_decision_support_llm.py")

    print("\n" + "=" * 80)
    print("All tests complete!")
    print("=" * 80)
