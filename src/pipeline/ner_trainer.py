import spacy
import json
import re
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from spacy.language import Language
from spacy.tokens import Doc

# Custom NAAC entity labels and patterns
NAAC_ENTITIES = [
    "INSTITUTION_NAME",
    "AFFILIATION",
    "PROGRAM",
    "ESTABLISHMENT_YEAR",
    "FACULTY_COUNT",
    "INFRASTRUCTURE"
]

NAAC_PATTERNS = [
    # Institution Name patterns
    {
        "label": "INSTITUTION_NAME",
        "pattern": [
            {"ENT_TYPE": "ORG"},
            {"LOWER": {"IN": ["university", "college", "institute", "school"]}},
            {"LOWER": "of", "OP": "?"},
            {"POS": "PROPN", "OP": "+"}
        ]
    },
    
    # Academic Programs
    {
        "label": "PROGRAM",
        "pattern": [
            {"LOWER": {"IN": ["bachelor", "b.sc", "b.tech", "master", "m.tech", "phd"]}},
            {"LOWER": "in"},
            {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"}
        ]
    },
    
    # Establishment Year
    {
        "label": "ESTABLISHMENT_YEAR",
        "pattern": [
            {"TEXT": {"REGEX": r"^(19|20)\d{2}$"}},
            {"LOWER": {"IN": ["established", "founded", "instituted"]}, "OP": "?"}
        ]
    },
    
    # Faculty Count
    {
        "label": "FACULTY_COUNT",
        "pattern": [
            {"LOWER": {"IN": ["faculty", "teaching", "academic"]}},
            {"LOWER": "strength"},
            {"LIKE_NUM": True}
        ]
    }
]

# Valid degree types and fields
VALID_DEGREES = {
    "bachelor": ["arts", "science", "commerce", "technology", "business"],
    "master": ["science", "technology", "business", "arts", "education"],
    "phd": ["philosophy", "science", "engineering"]
}

class EnhancedNAACNerExtractor:
    def __init__(self, model_path: str = None):
        self.nlp = spacy.load(model_path or "en_core_web_lg")
        self.add_custom_components()
        
    def add_custom_components(self):
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(NAAC_PATTERNS)
        
        @Language.component("academic_sentencizer")
        def academic_sentencizer(doc):
            for token in doc[:-1]:
                if token.text in ("\n\n", ";", "•", "|"):
                    doc[token.i+1].is_sent_start = True
            return doc
        self.nlp.add_pipe("academic_sentencizer", first=True)

    def extract_academic_entities(self, text: str) -> List[Dict[str, Any]]:
        """Enhanced entity extraction with validation"""
        doc = self.nlp(text[:500000])
        raw_entities = []
        
        for ent in doc.ents:
            entity = self.process_entity(ent)
            if entity:
                raw_entities.append(entity)
        
        return self.post_process_entities(raw_entities)

    def process_entity(self, ent):
        """Normalize and validate entities"""
        if ent.label_ == "ESTABLISHMENT_YEAR":
            year = re.search(r"\b(19|20)\d{2}\b", ent.text)
            return {
                "text": year.group() if year else None,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            } if year else None
            
        if ent.label_ == "PROGRAM":
            parts = ent.text.lower().split()
            if len(parts) >= 3 and parts[1] == "in":
                degree_type = parts[0]
                field = " ".join(parts[2:])
                if degree_type in VALID_DEGREES and field in VALID_DEGREES[degree_type]:
                    return {
                        "text": ent.text.title(),
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char
                    }
            return None
            
        return {
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char
        }

    def post_process_entities(self, entities: List[Dict]) -> List[Dict]:
        """Deduplicate and filter entities"""
        seen = set()
        filtered = []
        
        for ent in sorted(entities, key=lambda x: x["start"]):
            if not ent: continue
            key = (ent["text"].lower(), ent["label"])
            if key not in seen:
                filtered.append(ent)
                seen.add(key)
                
        return filtered

class EnhancedCriteriaClassifier:
    """Context-aware criteria classifier with exclusion terms"""
    CRITERIA_KEYWORDS = {
        "1. Curricular Aspects": {
            "primary": ["curriculum design", "syllabus revision", "credit system"],
            "secondary": ["course structure", "academic framework", "pedagogy"],
            "exclude": ["research", "infrastructure"]
        },
        "2. Teaching-Learning": {
            "primary": ["faculty development", "teaching methodology", "student ratio"],
            "secondary": ["classroom interaction", "learning outcomes", "pedagogy"],
            "exclude": ["research", "placement"]
        },
        "3. Research": {
            "primary": ["publications", "patents", "conference", "research grants"],
            "secondary": ["scholarly activities", "innovation cell", "citations"],
            "exclude": ["curriculum", "teaching"]
        },
        "4. Infrastructure": {
            "primary": ["laboratory", "library", "hostel", "sports complex"],
            "secondary": ["ICT facilities", "classroom equipment", "maintenance"],
            "exclude": ["curriculum", "research"]
        }
    }

    def classify_section(self, text: str) -> str:
        scores = defaultdict(int)
        text_lower = text.lower()
        
        for criterion, terms in self.CRITERIA_KEYWORDS.items():
            # Positive matches
            for term in terms["primary"]:
                if term in text_lower:
                    scores[criterion] += 3
                    
            for term in terms["secondary"]:
                if term in text_lower:
                    scores[criterion] += 1
                    
            # Negative matches
            for term in terms["exclude"]:
                if term in text_lower:
                    scores[criterion] -= 2
                    
        return max(scores.items(), key=lambda x: x[1])[0] if scores else "Unknown"

def process_naac_documents(input_path: Path, output_path: Path) -> None:
    """End-to-end document processing pipeline"""
    with open(input_path, 'r', encoding='utf-8') as f:
        ssr_sections = json.load(f)
    
    ner = EnhancedNAACNerExtractor()
    classifier = EnhancedCriteriaClassifier()
    results = {}
    
    for section, content in ssr_sections.items():
        print(f"Processing: {section[:50]}...")
        
        # Extract and validate entities
        entities = ner.extract_academic_entities(content)
        
        # Classify section
        criteria = classifier.classify_section(content)
        
        # Extract key metrics
        metrics = {
            "institution": list({e["text"] for e in entities if e["label"] == "INSTITUTION_NAME"}),
            "programs": list({e["text"] for e in entities if e["label"] == "PROGRAM"}),
            "establishment_year": next(
                (e["text"] for e in entities 
                 if e["label"] == "ESTABLISHMENT_YEAR" and 1900 <= int(e["text"]) <= 2023),
                None
            ),
            "faculty_counts": [e["text"] for e in entities if e["label"] == "FACULTY_COUNT"]
        }
        
        results[section] = {
            "criteria": criteria,
            "entities": entities,
            "key_metrics": metrics
        }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nAnalysis complete. Results saved to {output_path}")

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    
    input_path = project_root / "data" / "processed" / "segmented_ssr.json"
    output_path = project_root / "data" / "processed" / "enhanced_analysis.json"
    
    if not input_path.exists():
        print(f"Error: Input file not found at {input_path}")
        exit(1)
    
    try:
        process_naac_documents(input_path, output_path)
    except Exception as e:
        print(f"Processing Error: {str(e)}")
        exit(1)