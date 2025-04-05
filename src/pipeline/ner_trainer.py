import spacy
import json
from pathlib import Path
from typing import Dict, List, Any

class NERExtractor:
    def __init__(self, model_path: str = None):
        """Initialize with custom or default model"""
        self.nlp = spacy.load(model_path or "en_core_web_lg")
        
        # Add custom entity ruler if needed
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        patterns = [
            {"label": "METRIC_ID", "pattern": [{"TEXT": {"REGEX": r"\d+\.\d+\.\d+"}}]},
            {"label": "PERCENTAGE", "pattern": [{"TEXT": {"REGEX": r"\d+\%"}}]}
        ]
        ruler.add_patterns(patterns)

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text"""
        doc = self.nlp(text[:1000000])  # Limit to 1M chars
        return [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            for ent in doc.ents
        ]

def process_ner(input_path: Path, output_path: Path) -> None:
    """Process all sections for NER"""
    with open(input_path, 'r', encoding='utf-8') as f:
        ssr_sections = json.load(f)
    
    extractor = NERExtractor()
    results = {}
    
    for section, content in ssr_sections.items():
        print(f"Processing NER for: {section[:50]}...")
        entities = extractor.extract_entities(content)
        if entities:
            results[section] = entities
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print("\nNER Extraction Results:")
    print("-" * 40)
    print(f"Found entities in {len(results)} sections")

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    
    input_path = project_root / "data" / "processed" / "segmented_ssr.json"
    output_path = project_root / "data" / "processed" / "ner_entities.json"
    
    if not input_path.exists():
        print(f"Error: Input file not found at {input_path}")
        exit(1)
    
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        process_ner(input_path, output_path)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)