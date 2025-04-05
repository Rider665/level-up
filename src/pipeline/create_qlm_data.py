import csv
import random
from faker import Faker
from pathlib import Path
from datetime import datetime, timedelta

fake = Faker()
current_year = datetime.now().year

NAAC_CRITERIA = {
    0: {
        "name": "Curricular Aspects",
        "templates": [
            "Curriculum revision through Board of Studies in {year} added {courses} courses",
            "Academic flexibility: {electives} electives + {credits}-credit MOOCs",
            "OBE implemented in {percent}% courses with {mappings} CO-PO mappings",
            "Syllabus updated in {year} with {update_percent}% industry input",
            "NAAC Criterion I: {percent}% courses aligned with NEP-2020"
        ],
        "metrics": {
            "year": lambda: random.randint(2019, current_year-1),
            "courses": lambda: random.randint(7, 25),
            "electives": lambda: random.randint(30, 50),
            "credits": lambda: random.choice([2, 3]),
            "percent": lambda: random.randint(85, 95),
            "update_percent": lambda: random.randint(20, 40),
            "mappings": lambda: random.randint(100, 150)
        }
    },
    1: {
        "name": "Teaching-Learning",
        "templates": [
            "Pedagogy: {percent}% courses use {methods}",
            "Faculty development: {hours} hrs/year training",
            "Student-teacher ratio maintained at {ratio}:1",
            "ICT tools: {tools} platforms integrated",
            "Assessment: {percent}% digital evaluation"
        ],
        "metrics": {
            "percent": lambda: random.randint(40, 85),
            "methods": lambda: random.choice(["flipped classrooms", "project-based learning", "MOOCs"]),
            "hours": lambda: random.randint(30, 100),
            "ratio": lambda: random.choice([12, 15, 18]),
            "tools": lambda: random.randint(3, 8)
        }
    },
    2: {
        "name": "Research",
        "templates": [
            "₹{amount} crore research funding",
            "{pubs} Scopus papers (h-index {hindex})",
            "{patents} patents filed in {year}",
            "{conferences} int'l conferences organized",
            "{projects} funded research projects"
        ],
        "metrics": {
            "amount": lambda: round(random.uniform(0.5, 5.0), 1),
            "pubs": lambda: random.randint(50, 300),
            "hindex": lambda: random.randint(8, 25),
            "patents": lambda: random.randint(2, 15),
            "year": lambda: random.randint(2019, current_year-1),
            "conferences": lambda: random.randint(1, 8),
            "projects": lambda: random.randint(5, 25)
        }
    },
    3: {
        "name": "Infrastructure",
        "templates": [
            "{smart} smart classrooms (₹{cost} crore)",
            "Library: {books} vols + {journals} e-journals",
            "IT: {comp} systems, {wifi} Mbps WiFi",
            "{labs} labs with ₹{equip} crore equipment",
            "Hostel: {capacity} seats, {amenities} amenities"
        ],
        "metrics": {
            "smart": lambda: random.randint(20, 60),
            "cost": lambda: random.randint(1, 15),
            "books": lambda: random.randint(10000, 80000),
            "journals": lambda: random.randint(5000, 20000),
            "comp": lambda: random.randint(100, 500),
            "wifi": lambda: random.choice([100, 200, 500]),
            "labs": lambda: random.randint(5, 20),
            "equip": lambda: random.randint(1, 10),
            "capacity": lambda: random.randint(200, 800),
            "amenities": lambda: random.randint(5, 15)
        }
    },
    4: {
        "name": "Student Support",
        "templates": [
            "{placed}% placements (₹{max}LPA max)",
            "Scholarships: ₹{amount} crore to {students}",
            "{startups} student startups funded",
            "Grievance redressal: {cases} cases resolved",
            "{events} student development events"
        ],
        "metrics": {
            "placed": lambda: random.randint(65, 95),
            "max": lambda: random.randint(12, 45),
            "amount": lambda: round(random.uniform(0.2, 2.5), 1),
            "students": lambda: random.randint(50, 300),
            "startups": lambda: random.randint(5, 25),
            "cases": lambda: random.randint(10, 80),
            "events": lambda: random.randint(20, 100)
        }
    },
    5: {
        "name": "Governance",
        "templates": [
            "IQAC: {meetings} meetings, {actions} actions",
            "Budget: ₹{budget} crore, {util}% utilization",
            "{audits} audits, {certifications} certifications",
            "Stakeholder satisfaction: {percent}%",
            "E-governance: {systems} systems implemented"
        ],
        "metrics": {
            "meetings": lambda: random.randint(4, 12),
            "actions": lambda: random.randint(10, 30),
            "budget": lambda: random.randint(5, 50),
            "util": lambda: random.randint(85, 99),
            "audits": lambda: random.randint(2, 8),
            "certifications": lambda: random.randint(3, 7),
            "percent": lambda: random.randint(75, 95),
            "systems": lambda: random.randint(3, 10)
        }
    },
    6: {
        "name": "Innovations",
        "templates": [
            "Green campus: {solar}KW solar, {water}% recycling",
            "Community: {beneficiaries} people served",
            "{courses} value-added courses offered",
            "SDG initiatives: {sdgs}/17 goals addressed",
            "{collabs} industry collaborations"
        ],
        "metrics": {
            "solar": lambda: random.randint(25, 100),
            "water": lambda: random.randint(40, 90),
            "beneficiaries": lambda: random.randint(1000, 10000),
            "courses": lambda: random.randint(5, 25),
            "sdgs": lambda: random.randint(5, 12),
            "collabs": lambda: random.randint(5, 20)
        }
    }
}

def generate_sample(criterion_id: int) -> str:
    """Generate realistic NAAC-compliant sample"""
    crit = NAAC_CRITERIA[criterion_id]
    template = random.choice(crit["templates"])
    metrics = {k: str(fn()) for k, fn in crit["metrics"].items()}
    
    # Generate main content
    content = template.format(**metrics)
    
    # Add references
    ref_year = current_year - random.randint(1,3)
    references = [
        f"Ref: Annual Report {ref_year}-{str(ref_year+1)[-2:]}",
        f"IQAC verified on {fake.date_between(start_date=f'-{random.randint(1,3)}y').strftime('%d-%m-%Y')}",
        f"NAAC Guideline {random.choice(['1.4.2', '2.3.1', '3.2.5'])}",
        f"Doc ID: {random.choice(['AR', 'IQAC', 'BOS'])}/{ref_year}/{random.randint(10,99)}"
    ]
    
    return f"{content}. {random.choice(references)}"

def format_content(text: str) -> str:
    """Add structured formatting"""
    formats = [
        lambda t: f"{t}\n• Annexure: {random.randint(1,8)}.{random.randint(1,5)}",
        lambda t: t.replace(". ", ".\n➢ "),
        lambda t: f"Sec {random.randint(1,4)}: {t}",
        lambda t: t + f"\n({random.choice(['UGC', 'AICTE', 'NEP'])} compliant)"
    ]
    return random.choice(formats)(text)

def generate_negative_samples(count: int) -> list:
    """Create challenging misclassification samples"""
    samples = []
    conflict_pairs = [(0,2), (1,4), (3,6), (2,5), (4,6)]
    
    for _ in range(count):
        true_label, false_label = random.choice(conflict_pairs)
        sample = generate_sample(false_label)
        samples.append((format_content(sample), true_label))
    
    return samples

def create_dataset(output_path: Path, samples_per_crit: int = 50, neg_samples: int = 50):
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['text', 'label'])
        
        # Generate main samples
        for crit_id in NAAC_CRITERIA:
            print(f"Creating {samples_per_crit} {NAAC_CRITERIA[crit_id]['name']} samples...")
            for _ in range(samples_per_crit):
                text = generate_sample(crit_id)
                writer.writerow([format_content(text), crit_id])
        
        # Add negative samples
        print(f"Adding {neg_samples} negative samples...")
        for text, label in generate_negative_samples(neg_samples):
            writer.writerow([text, label])

if __name__ == "__main__":
    output_dir = Path("data/naac_dataset")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "naac_training_data.csv"
    
    create_dataset(output_file)
    print(f"\nDataset generated: {output_file}")
    print(f"Total samples: {(7*50)+50} (50 per criteria + 50 negative)")