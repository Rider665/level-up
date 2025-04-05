import re
import json
from pathlib import Path
from typing import Dict, List

def manual_segmenter(text: str) -> Dict[str, str]:
    """Precise manual extraction with exact header matching"""
    # ENTER YOUR EXACT HEADERS HERE (copy from your PDF)
    MANUAL_HEADERS = [
        "CRITERION I  : Curricular Aspects",
        "CRITERION II : Teaching, Learning and Evaluation",
        "CRITERION III : Research and Consultancy",
        "CRITERION IV : Infrastructure and Learning Resources",
        "CRITERION V  : Student Support and Progression",
        "CRITERION VI : Governance and Leadership",
        "CRITERION VII : Innovations and Best Practices"
    ]
    
    sections = {}
    current_pos = 0
    
    for i in range(len(MANUAL_HEADERS)):
        header = MANUAL_HEADERS[i]
        next_header = MANUAL_HEADERS[i+1] if i+1 < len(MANUAL_HEADERS) else None
        
        # Find header position
        start = text.find(header, current_pos)
        if start == -1:
            print(f"⚠️ Header not found: {header}")
            continue
            
        # Find next header position
        end = text.find(next_header, start) if next_header else len(text)
        if end == -1 and next_header:
            print(f"⚠️ Next header not found: {next_header}")
            end = len(text)
            
        content = text[start+len(header):end].strip()
        sections[header] = content
        current_pos = end
    
    return sections

def verify_extraction(sections: Dict[str, str]) -> bool:
    """Check if all criteria were captured"""
    REQUIRED_CRITERIA = 7
    if len(sections) < REQUIRED_CRITERIA:
        print(f"\n❌ Only found {len(sections)}/{REQUIRED_CRITERIA} criteria")
        print("Missing sections:")
        for i in range(1, 8):
            if f"CRITERION {roman_numeral(i)}" not in sections:
                print(f"- Criterion {i}")
        return False
    return True

def roman_numeral(num: int) -> str:
    """Convert numbers to roman numerals (for criteria)"""
    val = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]
    result = []
    for (n, symbol) in val:
        while num >= n:
            result.append(symbol)
            num -= n
    return ''.join(result)

if __name__ == "__main__":
    # Config paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    INPUT_PATH = BASE_DIR / "data" / "processed" / "sample_ssr.json"
    OUTPUT_PATH = BASE_DIR / "data" / "processed" / "segmented_ssr.json"
    
    # Load text
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        text = json.load(f)["raw_text"]
    
    # Manual extraction
    print("\n⚡ RUNNING NUCLEAR OPTION (Manual Extraction)")
    sections = manual_segmenter(text)
    
    # Verify results
    if verify_extraction(sections):
        print("\n✅ SUCCESS: All criteria extracted")
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {OUTPUT_PATH}")
    else:
        print("\n❌ CRITICAL: Manual extraction failed")
        print("Please check your MANUAL_HEADERS match the PDF exactly")
        
        # Generate debug file
        with open(BASE_DIR / "data" / "debug" / "manual_fallback.txt", 'w') as f:
            f.write("NEED MANUAL INTERVENTION\n")
            f.write("Required headers:\n")
            for i in range(1, 8):
                f.write(f"CRITERION {roman_numeral(i)} : ...\n")
            f.write("\nFirst 1000 chars:\n")
            f.write(text[:1000])