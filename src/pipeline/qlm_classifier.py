import json
from pathlib import Path
from typing import Dict, Any
from transformers import pipeline

class QlMClassifier:
    def __init__(self, model_path: str = None):
        """Initialize with optional custom model path"""
        self.classifier = pipeline(
            "text-classification",
            model=model_path or "bert-base-uncased",
            tokenizer=model_path or "bert-base-uncased"
        )
        self.label_map = {
            0: "1. Curricular Aspects",
            1: "2. Teaching-Learning",
            2: "3. Research",
            3: "4. Infrastructure",
            4: "5. Student Support",
            5: "6. Governance",
            6: "7. Best Practices"
        }

    def predict_section(self, text: str) -> Dict[str, Any]:
        """Classify text into one of the 7 criteria"""
        result = self.classifier(text[:512])  # Truncate to model max length
        return {
            "predicted_criterion": self.label_map[int(result[0]['label'].split('_')[-1])],
            "confidence": round(result[0]['score'], 4)
        }

def process_qlm(input_path: Path, output_path: Path) -> None:
    """Process all qualitative sections"""
    with open(input_path, 'r', encoding='utf-8') as f:
        ssr_sections = json.load(f)
    
    classifier = QlMClassifier()
    results = {}
    
    for section, content in ssr_sections.items():
        if "CRITERION" in section.upper():  # Only process criterion sections
            print(f"Classifying: {section[:50]}...")
            prediction = classifier.predict_section(content)
            results[section] = prediction
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print("\nQlM Classification Results:")
    print("-" * 40)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    
    input_path = project_root / "data" / "processed" / "segmented_ssr.json"
    output_path = project_root / "data" / "processed" / "qlm_predictions.json"
    
    if not input_path.exists():
        print(f"Error: Input file not found at {input_path}")
        exit(1)
    
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        process_qlm(input_path, output_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)