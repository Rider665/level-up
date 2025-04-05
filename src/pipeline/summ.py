import re
import json
import spacy
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline

class SSRSummarizer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.key_metrics = {
            'institution': None,
            'establishment_year': None,
            'programs': [],
            'faculty_stats': defaultdict(int),
            'infrastructure': {},
            'research_stats': defaultdict(int),
            'naac_grade': None
        }

    def process_ssr(self, text: str) -> dict:
        """Main processing pipeline"""
        # Extract structured data
        self._extract_entities(text)
        self._extract_stats(text)
        
        # Generate summaries
        return {
            "executive_summary": self._generate_summary(text),
            "key_metrics": self.key_metrics,
            "critical_findings": self._identify_key_sections(text)
        }

    def _extract_entities(self, text: str):
        """Extract key entities using rule-based + ML approach"""
        doc = self.nlp(text)
        
        # Institution Name (First occurrence of ORG + College/University)
        for ent in doc.ents:
            if ent.label_ == "ORG" and any(x in ent.text.lower() for x in ["college", "university"]):
                self.key_metrics['institution'] = ent.text
                break
                
        # Establishment Year
        years = re.findall(r"\b(19|20)\d{2}\b", text)
        self.key_metrics['establishment_year'] = min(years) if years else None
        
        # Academic Programs
        programs = []
        for match in re.finditer(r"\b(B\.?[A-Z]+|M\.?[A-Z]+|PhD)\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text):
            programs.append(f"{match.group(1)} in {match.group(2)}")
        self.key_metrics['programs'] = list(set(programs))[:10]  # Top 10 unique programs

    def _extract_stats(self, text: str):
        """Extract numerical statistics"""
        # Faculty Numbers
        faculty_matches = re.findall(
            r"(permanent faculty|teaching staff)\D*(\d+)", 
            text, 
            re.IGNORECASE
        )
        self.key_metrics['faculty_stats']['total'] = sum(int(m[1]) for m in faculty_matches)
        
        # Infrastructure
        infra_matches = re.findall(
            r"(classrooms|laboratories|computers)\D*(\d+)", 
            text, 
            re.IGNORECASE
        )
        for item, count in infra_matches:
            self.key_metrics['infrastructure'][item.lower()] = int(count)
            
        # Research Metrics
        research_matches = re.findall(
            r"(publications|patents|research projects)\D*(\d+)", 
            text, 
            re.IGNORECASE
        )
        for item, count in research_matches:
            self.key_metrics['research_stats'][item.lower()] = int(count)

    def _generate_summary(self, text: str) -> str:
        """Generate abstractive summary with key sections"""
        # Identify important sections using TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2))
        tfidf = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        # Convert important terms to a list of str
        important_terms = [str(term) for term in feature_names[tfidf.sum(axis=0).argsort()[0,-20:]]]
        
        # Filter text for key sections
        sentences = [sent.text for sent in self.nlp(text).sents]
        key_sentences = [s for s in sentences if any(term in s.lower() for term in important_terms)]
        
        # Generate summary
        return self.summarizer(
            " ".join(key_sentences),
            max_length=500,
            min_length=200,
            do_sample=False
        )[0]['summary_text']

    def _identify_key_sections(self, text: str) -> list:
        """Identify critical NAAC sections"""
        naac_keywords = {
            'strengths': ['strength', 'advantage', 'achievement'],
            'weaknesses': ['weakness', 'challenge', 'limitation'],
            'innovations': ['innovation', 'unique', 'patent'],
            'quality_indicators': ['naac', 'grade', 'accreditation']
        }
        
        findings = []
        for section, keywords in naac_keywords.items():
            matches = re.finditer("|".join(keywords), text, re.IGNORECASE)
            for match in matches:
                context = text[match.start()-200:match.end()+200].replace("\n", " ")
                findings.append({
                    'type': section,
                    'excerpt': f"...{context}..."
                })
                
        return findings[:5]  # Return top 5 critical findings

from pathlib import Path
import pdfplumber

if __name__ == "__main__":
    # Update the file path to point to the correct location of your SSR document.
    pdf_file = Path(__file__).resolve().parent / "ssr_document.pdf"
    
    # Extract text from the PDF
    try:
        with pdfplumber.open(pdf_file) as pdf:
            ssr_text = ""
            for page in pdf.pages:
                ssr_text += page.extract_text()
        
        summarizer = SSRSummarizer()
        report = summarizer.process_ssr(ssr_text)
        
        print("# NAAC SSR Executive Summary\n")
        print("## Key Metrics")
        print(json.dumps(report["key_metrics"], indent=2))
        
        print("\n## Executive Summary")
        print(report["executive_summary"])
        
        print("\n## Critical Findings")
        for finding in report["critical_findings"]:
            print(f"### {finding['type'].title()}")
            print(f"{finding['excerpt']}\n")
    
    except Exception as e:
        print(f"Error processing the PDF: {e}")