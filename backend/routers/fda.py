from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os
from sqlalchemy import select

from services.fda_service import FDAService
from config.database import get_db
from models.fda import FDAApplication, ClinicalTrial

router = APIRouter(
    prefix="/api/fda",
    tags=["FDA"]
)

# Initialize FDA service with API key
FDA_API_KEY = os.getenv("FDA_API_KEY", "")
fda_service = FDAService(FDA_API_KEY)

@router.get("/company/{symbol}/summary")
async def get_company_fda_summary(
    symbol: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a summary of FDA-related information for a company
    """
    try:
        return await fda_service.get_company_fda_summary(db, symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{symbol}/applications")
async def get_company_applications(
    symbol: str,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all FDA applications for a company
    """
    applications = db.query(FDAApplication).filter(
        FDAApplication.company_id == symbol
    ).all()
    
    return [{
        "id": app.id,
        "application_number": app.application_number,
        "application_type": app.application_type.value,
        "drug_name": app.drug_name,
        "therapeutic_area": app.therapeutic_area,
        "current_status": app.current_status.value,
        "submission_date": app.submission_date.isoformat() if getattr(app.submission_date, '_value', None) is not None else None,
        "pdufa_date": app.pdufa_date.isoformat() if getattr(app.pdufa_date, '_value', None) is not None else None,
        "approval_date": app.approval_date.isoformat() if getattr(app.approval_date, '_value', None) is not None else None,
    } for app in applications]

@router.get("/application/{application_id}/trials")
async def get_application_trials(
    application_id: int,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all clinical trials for a specific FDA application
    """
    trials = db.query(ClinicalTrial).filter(
        ClinicalTrial.application_id == application_id
    ).all()
    
    return [{
        "id": trial.id,
        "nct_number": trial.nct_number,
        "phase": trial.phase.value,
        "status": trial.status,
        "start_date": trial.start_date.isoformat() if getattr(trial.start_date, '_value', None) is not None else None,
        "estimated_completion_date": trial.estimated_completion_date.isoformat() if getattr(trial.estimated_completion_date, '_value', None) is not None else None,
        "actual_completion_date": trial.actual_completion_date.isoformat() if getattr(trial.actual_completion_date, '_value', None) is not None else None,
        "enrollment_target": trial.enrollment_target,
        "enrollment_actual": trial.enrollment_actual,
        "primary_endpoint": trial.primary_endpoint,
    } for trial in trials]

@router.post("/company/{symbol}/sync")
async def sync_company_fda_data(
    symbol: str,
    company_name: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Sync FDA data for a specific company
    """
    try:
        await fda_service.process_company_fda_data(db, symbol, company_name)
        return {"status": "success", "message": "FDA data synchronized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/therapeutic-areas")
async def get_therapeutic_area_stats(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get statistics about applications by therapeutic area
    """
    applications = db.query(FDAApplication).all()
    stats = {}
    
    for app in applications:
        therapeutic_area = getattr(app.therapeutic_area, '_value', None)
        if therapeutic_area:
            if therapeutic_area not in stats:
                stats[therapeutic_area] = {
                    "total": 0,
                    "approved": 0,
                    "pending": 0,
                    "rejected": 0
                }
            stats[therapeutic_area]["total"] += 1
            
            if app.current_status.value == "Approved":
                stats[therapeutic_area]["approved"] += 1
            elif app.current_status.value in ["Submitted", "Under Review"]:
                stats[therapeutic_area]["pending"] += 1
            elif app.current_status.value == "Rejected":
                stats[therapeutic_area]["rejected"] += 1
    
    return {
        "therapeutic_areas": stats,
        "total_applications": sum(area["total"] for area in stats.values()),
        "total_approved": sum(area["approved"] for area in stats.values()),
    } 