import spacy
from spacy.tokens import Doc
import re

nlp = spacy.load("en_core_web_sm")

def clean_text(text: str) -> str:
    """Remove headers/footers and normalize whitespace."""
    # Example: Remove page numbers (e.g., "Page 1 of 10")
    text = re.sub(r'Page\s\d+\s+of\s+\d+', '', text)
    # Normalize multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize_text(text: str) -> Doc:
    """Tokenize text with spaCy."""
    doc = nlp(text)
    return doc

# Example usage
if __name__ == "__main__":
    sample_text = "The institute has 150 faculty members.\nPage 1 of 10"
    cleaned = clean_text(sample_text)
    tokens = tokenize_text(cleaned)
    print([token.text for token in tokens])