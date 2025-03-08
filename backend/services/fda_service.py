from typing import List, Dict, Any, Optional, cast
import httpx
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging
from fastapi import HTTPException

from models.fda import (
    FDAApplication,
    ClinicalTrial,
    RegulatoryDesignation,
    AdvisoryCommitteeMeeting,
    ApplicationType,
    ApplicationStatus,
    TrialPhase,
    DesignationType
)

logger = logging.getLogger(__name__)

class FDAService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.fda.gov"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Authorization": f"Bearer {api_key}"}
        )

    async def close(self):
        await self.client.aclose()

    async def fetch_drug_applications(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Fetch drug applications from openFDA API for a specific company
        """
        try:
            # Search in drug applications
            query = f'sponsor_name:"{company_name}"'
            response = await self.client.get(
                "/drug/drugsfda.json",
                params={
                    "search": query,
                    "limit": 100  # Adjust based on needs
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except httpx.HTTPError as e:
            logger.error(f"Error fetching FDA drug applications: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch FDA data")

    async def fetch_clinical_trials(self, application_number: str) -> List[Dict[str, Any]]:
        """
        Fetch clinical trials data from ClinicalTrials.gov via openFDA
        """
        try:
            query = f'id:"{application_number}"'
            response = await self.client.get(
                "/drug/nct.json",
                params={
                    "search": query,
                    "limit": 100
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except httpx.HTTPError as e:
            logger.error(f"Error fetching clinical trials: {str(e)}")
            return []

    def _parse_application_status(self, status: Optional[str]) -> ApplicationStatus:
        """Map openFDA status to our ApplicationStatus enum"""
        if not status:
            return ApplicationStatus.UNDER_REVIEW
            
        status_map = {
            "Submitted": ApplicationStatus.SUBMITTED,
            "Pending": ApplicationStatus.UNDER_REVIEW,
            "Approved": ApplicationStatus.APPROVED,
            "Complete Response": ApplicationStatus.REJECTED,
            "Withdrawn": ApplicationStatus.WITHDRAWN,
        }
        return status_map.get(status, ApplicationStatus.UNDER_REVIEW)

    def _parse_application_type(self, type_str: Optional[str]) -> ApplicationType:
        """Map openFDA application type to our ApplicationType enum"""
        if not type_str:
            return ApplicationType.NDA
            
        type_map = {
            "NDA": ApplicationType.NDA,
            "BLA": ApplicationType.BLA,
            "ANDA": ApplicationType.ANDA,
            "IND": ApplicationType.IND,
        }
        return type_map.get(type_str, ApplicationType.NDA)

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    async def process_company_fda_data(
        self,
        db: Session,
        company_symbol: str,
        company_name: str
    ) -> None:
        """
        Process and store FDA data for a company
        """
        # Fetch drug applications
        applications = await self.fetch_drug_applications(company_name)
        
        for app_data in applications:
            # Create or update FDA Application
            application = FDAApplication(
                company_id=company_symbol,
                application_number=cast(str, app_data.get("application_number")),
                application_type=self._parse_application_type(app_data.get("application_type")),
                therapeutic_area=app_data.get("product_details", [{}])[0].get("substance_name"),
                drug_name=app_data.get("openfda", {}).get("brand_name", [None])[0],
                indication=app_data.get("product_details", [{}])[0].get("indication_and_usage"),
                current_status=self._parse_application_status(app_data.get("application_status")),
                submission_date=self._parse_date(app_data.get("submission_date")),
                approval_date=self._parse_date(app_data.get("approval_date")),
            )

            db.merge(application)

            # Fetch and process clinical trials
            app_number = app_data.get("application_number")
            if app_number:
                trials = await self.fetch_clinical_trials(app_number)
                for trial_data in trials:
                    trial = ClinicalTrial(
                        application_id=application.id,
                        nct_number=cast(str, trial_data.get("nct_id")),
                        phase=TrialPhase[f"PHASE{trial_data.get('phase', '1')}"],
                        status=trial_data.get("overall_status"),
                        start_date=self._parse_date(trial_data.get("start_date")),
                        estimated_completion_date=self._parse_date(trial_data.get("completion_date")),
                        enrollment_target=trial_data.get("enrollment_target"),
                        primary_endpoint=trial_data.get("primary_outcome", [{}])[0].get("measure"),
                    )
                    db.merge(trial)

            # Process regulatory designations
            for designation in app_data.get("regulatory_designations", []):
                reg_designation = RegulatoryDesignation(
                    application_id=application.id,
                    designation_type=DesignationType[designation.get("type", "FAST_TRACK").upper().replace(" ", "_")],
                    granted_date=self._parse_date(designation.get("granted_date")),
                )
                db.merge(reg_designation)

        try:
            db.commit()
        except Exception as e:
            logger.error(f"Error committing FDA data: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to store FDA data")

    async def get_company_fda_summary(
        self,
        db: Session,
        company_symbol: str
    ) -> Dict[str, Any]:
        """
        Get a summary of FDA-related information for a company
        """
        applications = db.query(FDAApplication).filter(
            FDAApplication.company_id == company_symbol
        ).all()

        summary = {
            "total_applications": len(applications),
            "applications_by_status": {},
            "applications_by_type": {},
            "active_trials": 0,
            "completed_trials": 0,
            "regulatory_designations": {},
            "upcoming_pdufa_dates": [],
        }

        for app in applications:
            # Count by status
            status = app.current_status.value
            summary["applications_by_status"][status] = summary["applications_by_status"].get(status, 0) + 1

            # Count by type
            app_type = app.application_type.value
            summary["applications_by_type"][app_type] = summary["applications_by_type"].get(app_type, 0) + 1

            # Count trials
            for trial in app.trials:
                if trial.status == "Active":
                    summary["active_trials"] += 1
                elif trial.status == "Completed":
                    summary["completed_trials"] += 1

            # Count designations
            for designation in app.designations:
                des_type = designation.designation_type.value
                summary["regulatory_designations"][des_type] = summary["regulatory_designations"].get(des_type, 0) + 1

            # Track upcoming PDUFA dates
            pdufa_date = getattr(app.pdufa_date, '_value', None)
            if pdufa_date and pdufa_date > date.today():
                summary["upcoming_pdufa_dates"].append({
                    "drug_name": getattr(app.drug_name, '_value', None),
                    "pdufa_date": pdufa_date.isoformat(),
                    "application_type": app.application_type.value
                })

        return summary 