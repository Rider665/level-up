import re
import json
from pathlib import Path
from typing import Dict, Any

# Metric patterns with value validation ranges
QNM_PATTERNS = {
    # Format: {metric_id: [(pattern, min, max), ...]}
    "1.1.1": [
        (r"Faculty\D*student ratio\D*(\d+:\d+)", 5, 50),
        (r"Faculty\D*(\d+)\D*student\D*(\d+)", 5, 50)
    ],
    "2.3.1": [
        (r"PhD faculty\D*(\d+)", 0, 200),
        (r"Doctoral faculty\D*(\d+)", 0, 200)
    ],
    "3.2.1": [
        (r"Research papers\D*(\d+)", 0, 1000),
        (r"Publications\D*(\d+)", 0, 1000)
    ],
    "4.1.1": [
        (r"Classrooms\D*(\d+)", 1, 100),
        (r"Lecture halls\D*(\d+)", 1, 50)
    ],
    "5.2.1": [
        (r"Placement percentage\D*(\d+)%", 0, 100),
        (r"Students placed\D*(\d+)%", 0, 100)
    ]
}

def validate_value(value: float, min_val: float, max_val: float) -> float:
    """Ensure extracted values are within reasonable ranges"""
    if value < min_val or value > max_val:
        raise ValueError(f"Value {value} outside expected range ({min_val}-{max_val})")
    return value

def extract_qnm(text: str) -> Dict[str, Any]:
    """Extract metrics with validation"""
    results = {}
    for metric_id, patterns in QNM_PATTERNS.items():
        for pattern, min_val, max_val in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = next((g for g in match.groups() if g and g.replace(':','').isdigit()), None)
                    if value:
                        num_value = float(value.split(':')[0]) if ':' in value else float(value)
                        validated = validate_value(num_value, min_val, max_val)
                        results[metric_id] = validated
                        break
                except ValueError as e:
                    print(f"⚠️ Validation failed for {metric_id}: {e}")
    return results

if __name__ == "__main__":
    # Get absolute paths using script location
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    
    input_path = project_root / "data" / "processed" / "segmented_ssr.json"
    output_path = project_root / "data" / "processed" / "qnm_metrics.json"
    
    # Verify paths and data directory structure
    if not input_path.exists():
        print(f"\nError: Input file not found at {input_path}")
        print("\nMake sure:")
        print("1. You've run text_segmenter.py first")
        print("2. Your directory structure looks like this:")
        print("naac-automation/")
        print("├── data/")
        print("│   └── processed/")
        print("│       └── segmented_ssr.json")
        print("└── src/")
        print("    └── pipeline/")
        print("        └── qnm_extractor.py")
        exit(1)

    try:
        # Create processed directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load and process data
        with open(input_path, 'r', encoding='utf-8') as f:
            ssr_sections = json.load(f)
        
        final_metrics = {}
        for section, content in ssr_sections.items():
            print(f"\nExtracting from: {section[:50]}...")
            section_metrics = extract_qnm(content)
            for metric, value in section_metrics.items():
                if metric not in final_metrics:  # Avoid overwriting
                    final_metrics[metric] = value
                    print(f"Found {metric}: {value}")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_metrics, f, indent=2)
        
        print("\nValidated Results:")
        print("-" * 40)
        print(json.dumps(final_metrics, indent=2))
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        exit(1)