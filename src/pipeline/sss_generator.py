import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

# Official NAAC SSS Categories (Version 2023)
NAAC_CATEGORIES = [
    "Curriculum_Design_Relevance",
    "Teaching_Learning_Quality",
    "Assessment_Process_Fairness",
    "Infrastructure_Facilities",
    "Library_Resources_Access",
    "ICT_Resources_Availability",
    "Student_Support_Services",
    "Administrative_Efficiency",
    "Extracurricular_Activities",
    "Research_Innovation_Support",
    "Gender_Sensitivity_Initiatives",
    "Environmental_Sustainability",
    "Value_Added_Courses",
    "Grievance_Redressal_System",
    "Overall_Institutional_Experience"
]

NAAC_WEIGHTS = {
    "Curriculum_Design_Relevance": 0.15,
    "Teaching_Learning_Quality": 0.20,
    "Assessment_Process_Fairness": 0.10,
    "Infrastructure_Facilities": 0.08,
    "Library_Resources_Access": 0.07,
    "ICT_Resources_Availability": 0.07,
    "Student_Support_Services": 0.10,
    "Administrative_Efficiency": 0.05,
    "Extracurricular_Activities": 0.04,
    "Research_Innovation_Support": 0.05,
    "Gender_Sensitivity_Initiatives": 0.03,
    "Environmental_Sustainability": 0.03,
    "Value_Added_Courses": 0.03,
    "Grievance_Redressal_System": 0.02
}

def generate_naac_sss_data(output_path: Path, num_responses=1000):
    """Generate NAAC-compliant SSS dataset"""
    header = ["Response_ID", "Timestamp"] + list(NAAC_WEIGHTS.keys()) + ["Overall_Institutional_Experience"]
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        for i in range(num_responses):
            # Generate realistic timestamps within academic year
            base_date = datetime(2023, 7, 1)
            timestamp = base_date + timedelta(days=random.randint(0, 180))
            
            # Generate category scores with NAAC-specific patterns
            scores = {
                "Curriculum_Design_Relevance": min(4, max(0, random.normalvariate(3.4, 0.5))),
                "Teaching_Learning_Quality": min(4, max(0, random.normalvariate(3.6, 0.4))),
                "Assessment_Process_Fairness": round(random.uniform(2.8, 4.0), 1),
                "Infrastructure_Facilities": random.choices([3.0, 3.5, 4.0], weights=[1, 2, 3])[0],
                "Library_Resources_Access": random.triangular(2.5, 4.0, 3.3),
                "ICT_Resources_Availability": min(4, random.expovariate(1.5) + 2.2),
                "Student_Support_Services": round(random.betavariate(2, 2) * 4, 1),
                "Administrative_Efficiency": random.randrange(2, 5),
                "Extracurricular_Activities": min(4, max(0, random.gauss(3.2, 0.8))),
                "Research_Innovation_Support": random.choices([2.5, 3.0, 3.5], weights=[2, 3, 1])[0],
                "Gender_Sensitivity_Initiatives": random.uniform(3.2, 4.0),
                "Environmental_Sustainability": min(4, random.lognormvariate(0.6, 0.2)),
                "Value_Added_Courses": round(random.normalvariate(3.3, 0.5), 1),
                "Grievance_Redressal_System": random.choices([3.5, 4.0], weights=[1, 3])[0]
            }
            
            # Calculate overall experience (not included in NAAC score)
            overall = min(4, sum(scores.values())/len(scores) * random.uniform(0.9, 1.1))
            
            writer.writerow([
                f"RESP_{i+1:04d}",
                timestamp.isoformat(),
                *[scores[k] for k in NAAC_WEIGHTS],
                round(overall, 1)
            ])

if __name__ == "__main__":
    output_path = Path("data/raw/naac_sss_2023.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    generate_naac_sss_data(output_path, 1500)
    print(f"Generated NAAC-compliant SSS dataset at {output_path}")