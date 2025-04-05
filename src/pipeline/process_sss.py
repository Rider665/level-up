import csv
import json
import statistics
import numpy as np
from pathlib import Path
from typing import Dict, List

NAAC_WEIGHTS = {
    "Curriculum_Design_Relevance": 0.15,
    "Teaching_Learning_Quality": 0.20,
    "Assessment_Process_Fairness": 0.10,
    "Infrastructure_Facilities": 0.08,
    "Library_Resources_Access": 0.07,
    "ICT_Resources_Availability": 0.07,
    "Student_Support_Services": 0.08,
    "Administrative_Efficiency": 0.07,
    "Extracurricular_Activities": 0.05,
    "Research_Innovation_Support": 0.08,
    "Gender_Sensitivity_Initiatives": 0.04,
    "Environmental_Sustainability": 0.03,
    "Value_Added_Courses": 0.03,
    "Grievance_Redressal_System": 0.03,
    "Overall_Institutional_Experience": 0.10
}

class NAACSSSProcessor:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.weights = NAAC_WEIGHTS
        self.categories = list(NAAC_WEIGHTS.keys())
        
    def _validate_response(self, row: Dict) -> bool:
        try:
            return all(0 <= float(row[cat]) <= 4 for cat in self.categories)
        except (ValueError, KeyError):
            return False

    def process(self) -> Dict:
        """Process data according to NAAC guidelines"""
        category_data = {cat: [] for cat in self.categories}
        valid_responses = 0
        
        with open(self.data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if self._validate_response(row):
                    valid_responses += 1
                    for cat in self.categories:
                        category_data[cat].append(float(row[cat]))
        
        if valid_responses == 0:
            raise ValueError("No valid responses found")
        
        # Calculate category statistics
        analysis = {
            "metadata": {
                "total_responses": reader.line_num - 1,  # Subtract header
                "valid_responses": valid_responses,
                "validity_percentage": round((valid_responses/(reader.line_num - 1)) * 100, 1)
            },
            "category_analysis": {},
            "naac_scoring": {}
        }
        
        # Category-wise analysis
        for cat in self.categories:
            scores = category_data[cat]
            analysis["category_analysis"][cat] = {
                "mean": round(np.mean(scores), 2),
                "median": round(np.median(scores), 2),
                "std_dev": round(np.std(scores), 2),
                "percentile_25": round(np.percentile(scores, 25), 2),
                "percentile_75": round(np.percentile(scores, 75), 2),
                "naac_weight": self.weights[cat]
            }
        
        # Calculate NAAC Official Score
        weighted_sum = sum(
            analysis["category_analysis"][cat]["mean"] * self.weights[cat]
            for cat in self.categories
        )
        
        analysis["naac_scoring"] = {
            "weighted_score": round(weighted_sum, 2),
            "grade_boundaries": NAAC_GRADE_BOUNDARIES,
            "interpretation": "Scores calculated using NAAC 2023 weightings"
        }
        
        return analysis

NAAC_GRADE_BOUNDARIES = {
    "A++": (3.51, 4.00),
    "A+": (3.26, 3.50),
    "A": (3.01, 3.25),
    "B++": (2.76, 3.00),
    "B+": (2.51, 2.75),
    "B": (2.01, 2.50),
    "C": (1.51, 2.00),
    "D": (0.00, 1.50)
}

if __name__ == "__main__":
    input_path = Path("data/raw/naac_sss_2023.csv")
    output_path = Path("data/processed/naac_sss_report.json")
    
    processor = NAACSSSProcessor(input_path)
    try:
        report = processor.process()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print("NAAC SSS Processing Report:")
        print(f"- Valid Responses: {report['metadata']['valid_responses']}")
        print(f"- Weighted NAAC Score: {report['naac_scoring']['weighted_score']}/4.0")
        print(f"Full report saved to {output_path}")
        
    except Exception as e:
        print(f"NAAC Processing Error: {str(e)}")
        exit(1)