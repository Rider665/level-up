import json
from pathlib import Path
from typing import Dict, Any

class CGPACalculator:
    GRADE_BOUNDARIES = {
        "A++": (3.51, 4.00),
        "A+": (3.26, 3.50),
        "A": (3.01, 3.25),
        "B++": (2.76, 3.00),
        "B+": (2.51, 2.75),
        "B": (2.01, 2.50),
        "C": (1.51, 2.00),
        "D": (0.00, 1.50)
    }

    QNM_BENCHMARKS = {
        "3.2.1": 200,  # Research Papers
        "4.1.1": 40,   # Classrooms
        "5.2.1": 100   # Placement %
    }

    def _normalize_qnm(self, raw_metrics: Dict) -> Dict:
        """Normalize QnM metrics to 0-4 scale"""
        return {
            k: min(4.0, (v / self.QNM_BENCHMARKS[k]) * 4)
            for k, v in raw_metrics.items()
            if k in self.QNM_BENCHMARKS
        }

    def calculate(self, qnm_path: Path, qlm_path: Path, sss_path: Path) -> Dict[str, Any]:
        # Load and normalize QnM metrics
        with open(qnm_path, 'r') as f:
            raw_qnm = json.load(f)
        
        normalized_qnm = self._normalize_qnm(raw_qnm)
        sgs = sum(normalized_qnm.values()) / len(normalized_qnm) if normalized_qnm else 0

        # Load and process QlM scores
        with open(qlm_path, 'r') as f:
            qlm_data = json.load(f)
        
        qlm_scores = [v['confidence'] * 4 for v in qlm_data.values()]
        qlm = sum(qlm_scores) / len(qlm_scores) if qlm_scores else 0

        # Load and validate SSS score
        with open(sss_path, 'r') as f:
            sss_data = json.load(f)
        
        sss_score = sss_data['naac_scoring']['weighted_score']
        sss_score = min(4.0, max(0.0, sss_score))

        # Calculate final CGPA
        cgpa = (sgs * 0.5) + (qlm * 0.3) + (sss_score * 0.2)
        cgpa = round(cgpa, 2)

        # Determine grade
        grade = next(
            (g for g, (low, high) in self.GRADE_BOUNDARIES.items() if low <= cgpa <= high),
            "D"
        )

        return {
            "sgs_score": round(sgs, 2),
            "qlm_score": round(qlm, 2),
            "sss_score": round(sss_score, 2),
            "cgpa": cgpa,
            "grade": grade,
            "is_accredited": grade != "D",
            "normalized_qnm": normalized_qnm
        }

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    
    # Input paths
    qnm_path = project_root / "data" / "processed" / "qnm_metrics.json"
    qlm_path = project_root / "data" / "processed" / "qlm_predictions.json"
    sss_path = project_root / "data" / "processed" / "naac_sss_report.json"
    output_path = project_root / "data" / "processed" / "cgpa_result.json"
    
    # Validate inputs
    missing = [p for p in [qnm_path, qlm_path, sss_path] if not p.exists()]
    if missing:
        print("Error: Missing input files")
        for path in missing:
            print(f"- {path.name}")
        exit(1)
    
    try:
        calculator = CGPACalculator()
        result = calculator.calculate(qnm_path, qlm_path, sss_path)
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        print("\nNAAC Accreditation Results:")
        print("-" * 40)
        print(f"SGS Score: {result['sgs_score']}/4.0")
        print(f"QlM Score: {result['qlm_score']}/4.0")
        print(f"SSS Score: {result['sss_score']}/4.0")
        print(f"Final CGPA: {result['cgpa']} → Grade: {result['grade']}")
        print(f"Status: {'✅ Accredited' if result['is_accredited'] else '❌ Not Accredited'}")
        
    except Exception as e:
        print(f"\nCritical Error: {str(e)}")
        exit(1)