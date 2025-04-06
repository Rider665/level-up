# __init__.py
import json
import sys
from pathlib import Path

# Import pipeline modules
from .pdf_extractor import extract_text_from_pdf, save_text_to_json
from .text_segmenter import manual_segmenter, verify_extraction
from .qnm_extractor import extract_qnm
from .qlm_classifier import process_qlm
from .process_sss import NAACSSSProcessor
from .cgpa_calculator import CGPACalculator

def run_pipeline():
    print("Starting NAAC Automation Pipeline...")

    # Setup paths (adjust as needed)
    project_root = Path(__file__).resolve().parent.parent
    data_raw = project_root / "data" / "raw"
    data_processed = project_root / "data" / "processed"
    data_raw.mkdir(parents=True, exist_ok=True)
    data_processed.mkdir(parents=True, exist_ok=True)

    # === 1. PDF Extraction ===
    pdf_path = data_raw / "sample_ssr.pdf"
    pdf_json_path = data_raw / "sample_ssr.json"
    if not pdf_path.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        sys.exit(1)
    print("Extracting text from PDF...")
    text = extract_text_from_pdf(str(pdf_path))
    save_text_to_json(text, str(pdf_json_path))
    print(f"PDF text extracted and saved to {pdf_json_path}")

    # === 2. Text Segmentation ===
    print("Segmenting extracted text...")
    with open(pdf_json_path, 'r', encoding='utf-8') as f:
        text_data = json.load(f)
    raw_text = text_data["raw_text"]
    sections = manual_segmenter(raw_text)
    segmented_path = data_processed / "segmented_ssr.json"
    if verify_extraction(sections):
        with open(segmented_path, 'w', encoding='utf-8') as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)
        print(f"Text segmentation successful. Results saved to {segmented_path}")
    else:
        print("CRITICAL: Text segmentation failed. Please verify your headers.")
        sys.exit(1)

    # === 3. Quantitative Metrics Extraction (QnM) ===
    print("Extracting Quantitative Metrics...")
    final_metrics = {}
    for section, content in sections.items():
        qm = extract_qnm(content)
        # Avoid overwriting; assumes each metric appears only once overall.
        for metric, value in qm.items():
            if metric not in final_metrics:
                final_metrics[metric] = value
    qnm_path = data_processed / "qnm_metrics.json"
    with open(qnm_path, 'w', encoding='utf-8') as f:
        json.dump(final_metrics, f, indent=2)
    print(f"Quantitative Metrics extracted and saved to {qnm_path}")

    # === 4. Qualitative Classification (QlM) ===
    print("Processing Qualitative Sections...")
    qlm_output_path = data_processed / "qlm_predictions.json"
    process_qlm(segmented_path, qlm_output_path)
    print(f"QlM Classification results saved to {qlm_output_path}")

    # === 5. SSS Processing ===
    print("Processing SSS Data...")
    sss_input_csv = project_root / "data" / "raw" / "naac_sss_2023.csv"
    sss_output_path = data_processed / "naac_sss_report.json"
    processor = NAACSSSProcessor(sss_input_csv)
    report = processor.process()
    with open(sss_output_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"SSS report generated and saved to {sss_output_path}")

    # === 6. CGPA Calculation ===
    print("Calculating CGPA based on QnM, QlM, and SSS scores...")
    calculator = CGPACalculator()
    cgpa_result = calculator.calculate(qnm_path, qlm_output_path, sss_output_path)
    cgpa_output_path = data_processed / "cgpa_result.json"
    with open(cgpa_output_path, 'w') as f:
        json.dump(cgpa_result, f, indent=2)
    print("\nNAAC Accreditation Results:")
    print("-" * 40)
    print(f"SGS Score: {cgpa_result['sgs_score']}/4.0")
    print(f"QlM Score: {cgpa_result['qlm_score']}/4.0")
    print(f"SSS Score: {cgpa_result['sss_score']}/4.0")
    print(f"Final CGPA: {cgpa_result['cgpa']} → Grade: {cgpa_result['grade']}")
    print(f"Status: {'✅ Accredited' if cgpa_result['is_accredited'] else '❌ Not Accredited'}")

    print("\nNAAC Automation Pipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()