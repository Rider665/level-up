from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
import json
from typing import Dict, Any, Optional
from cgpa_calculator import CGPACalculator

# Initialize FastAPI app with metadata
app = FastAPI(
    title="NAAC CGPA Calculator API",
    description="API for calculating NAAC CGPA scores based on QNM, QLM and SSS metrics",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Define paths to input files
BASE_DIR = Path(__file__).resolve().parent.parent.parent
QNM_PATH = BASE_DIR / "data" / "processed" / "qnm_metrics.json"
QLM_PATH = BASE_DIR / "data" / "processed" / "qlm_predictions.json"
SSS_PATH = BASE_DIR / "data" / "processed" / "naac_sss_report.json"

# Pydantic models for request/response
class CGPAResponse(BaseModel):
    sgs_score: float
    qlm_score: float
    sss_score: float
    cgpa: float
    grade: str
    is_accredited: bool
    normalized_qnm: Dict[str, float]

    class Config:
        schema_extra = {
            "example": {
                "sgs_score": 1.7,
                "qlm_score": 2.46,
                "sss_score": 3.77,
                "cgpa": 2.34,
                "grade": "B",
                "is_accredited": True,
                "normalized_qnm": {
                    "3.2.1": 0.94,
                    "4.1.1": 4.0,
                    "5.2.1": 0.16
                }
            }
        }

class ErrorResponse(BaseModel):
    detail: str

@app.get("/",
    response_model=Dict[str, str],
    responses={
        200: {
            "description": "Welcome message",
            "content": {
                "application/json": {
                    "example": {"message": "Welcome to the NAAC CGPA Calculator API. Use /docs for API documentation."}
                }
            }
        }
    }
)
async def root():
    """Root endpoint displaying welcome message"""
    return {"message": "Welcome to the NAAC CGPA Calculator API. Use /docs for API documentation."}

@app.post("/calculate-cgpa/",
    response_model=CGPAResponse,
    responses={
        200: {
            "description": "Successfully calculated CGPA",
            "model": CGPAResponse
        },
        400: {
            "description": "Missing input files",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    },
    tags=["CGPA Calculation"]
)
async def calculate_cgpa():
    """
    Calculate CGPA based on QnM, QlM, and SSS scores
    
    Returns:
        CGPAResponse: Calculated CGPA metrics including scores, grade and accreditation status
    
    Raises:
        HTTPException: If input files are missing or calculation fails
    """
    try:
        # Validate input files
        missing_files = [str(p) for p in [QNM_PATH, QLM_PATH, SSS_PATH] if not p.exists()]
        if missing_files:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required input files: {', '.join(missing_files)}"
            )

        # Perform CGPA calculation
        calculator = CGPACalculator()
        result = calculator.calculate(QNM_PATH, QLM_PATH, SSS_PATH)

        # Validate result format
        return CGPAResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating CGPA: {str(e)}"
        )

@app.post("/calculate-custom/",
    response_model=CGPAResponse,
    responses={
        200: {"description": "Successfully calculated CGPA"},
        400: {"description": "Invalid input data"},
        500: {"description": "Internal server error"}
    },
    tags=["CGPA Calculation"]
)
async def calculate_custom(
    qnm_file: UploadFile = File(...),
    qlm_file: UploadFile = File(...),
    sss_file: UploadFile = File(...)
):
    """
    Calculate CGPA using custom input files
    
    Args:
        qnm_file: JSON file containing QNM metrics
        qlm_file: JSON file containing QLM predictions
        sss_file: JSON file containing SSS report
    
    Returns:
        CGPAResponse: Calculated CGPA metrics
    """
    try:
        # Validate file types
        for file in [qnm_file, qlm_file, sss_file]:
            if not file.filename.endswith('.json'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file format for {file.filename}. Only JSON files are accepted."
                )

        # Create temporary files
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        temp_paths = []
        for file in [qnm_file, qlm_file, sss_file]:
            temp_path = temp_dir / file.filename
            with open(temp_path, "wb") as f:
                f.write(await file.read())
            temp_paths.append(temp_path)

        # Calculate CGPA
        calculator = CGPACalculator()
        result = calculator.calculate(*temp_paths)

        # Clean up temp files
        for path in temp_paths:
            path.unlink()
        
        return CGPAResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing custom files: {str(e)}"
        )