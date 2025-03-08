from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from models.base import Base

class ApplicationType(enum.Enum):
    IND = "Investigational New Drug"
    NDA = "New Drug Application"
    BLA = "Biologics License Application"
    ANDA = "Abbreviated New Drug Application"

class TrialPhase(enum.Enum):
    PHASE1 = "Phase 1"
    PHASE2 = "Phase 2"
    PHASE3 = "Phase 3"
    PHASE4 = "Phase 4"

class ApplicationStatus(enum.Enum):
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"
    ON_HOLD = "On Hold"

class DesignationType(enum.Enum):
    FAST_TRACK = "Fast Track"
    BREAKTHROUGH = "Breakthrough Therapy"
    ACCELERATED = "Accelerated Approval"
    PRIORITY_REVIEW = "Priority Review"
    ORPHAN = "Orphan Drug"

class FDAApplication(Base):
    __tablename__ = "fda_applications"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.symbol"), nullable=False)
    application_number = Column(String, unique=True, index=True)
    application_type = Column(Enum(ApplicationType))
    therapeutic_area = Column(String)
    drug_name = Column(String)
    indication = Column(Text)
    current_status = Column(Enum(ApplicationStatus))
    submission_date = Column(Date)
    pdufa_date = Column(Date, nullable=True)
    approval_date = Column(Date, nullable=True)
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="fda_applications")
    trials = relationship("ClinicalTrial", back_populates="application")
    designations = relationship("RegulatoryDesignation", back_populates="application")

class ClinicalTrial(Base):
    __tablename__ = "clinical_trials"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("fda_applications.id"))
    nct_number = Column(String, unique=True, index=True)  # ClinicalTrials.gov identifier
    phase = Column(Enum(TrialPhase))
    status = Column(String)
    start_date = Column(Date)
    estimated_completion_date = Column(Date)
    actual_completion_date = Column(Date, nullable=True)
    enrollment_target = Column(Integer)
    enrollment_actual = Column(Integer, nullable=True)
    primary_endpoint = Column(Text)
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    # Relationships
    application = relationship("FDAApplication", back_populates="trials")

class RegulatoryDesignation(Base):
    __tablename__ = "regulatory_designations"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("fda_applications.id"))
    designation_type = Column(Enum(DesignationType))
    granted_date = Column(Date)
    expiration_date = Column(Date, nullable=True)
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    # Relationships
    application = relationship("FDAApplication", back_populates="designations")

class AdvisoryCommitteeMeeting(Base):
    __tablename__ = "advisory_committee_meetings"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("fda_applications.id"))
    meeting_date = Column(Date)
    committee_name = Column(String)
    outcome = Column(String, nullable=True)
    vote_result = Column(String, nullable=True)
    key_findings = Column(Text, nullable=True)
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, server_default=func.now(), onupdate=func.now())

    # Relationships
    application = relationship("FDAApplication") 