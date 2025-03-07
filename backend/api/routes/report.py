from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from backend.services.pdf_generator import generate_pdf_report
from backend.services.email_service import send_report

router = APIRouter()

class ReportRequest(BaseModel):
    selected_charts: list
    email: str = None  # Optional field for emailing

@router.post("/generate-report")
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """Generate a report and optionally email it"""
    if not request.selected_charts:
        raise HTTPException(status_code=400, detail="No charts selected")

    pdf_path = generate_pdf_report(request.selected_charts)

    if request.email:
        background_tasks.add_task(send_report, request.email, pdf_path)
        return {"message": "Report generated and email is being sent", "pdf_url": pdf_path}

    return {"message": "Report generated successfully", "pdf_url": pdf_path}