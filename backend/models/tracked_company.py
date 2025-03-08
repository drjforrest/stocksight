from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from config.database import Base
from models.user import User

# SQLAlchemy Model
class TrackedCompany(Base):
    __tablename__ = "tracked_companies"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("stocksight.users.id"), nullable=False)
    company_symbol = Column(String, nullable=False)
    added_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="tracked_companies")

    class Config:
        from_attributes = True

# Pydantic Schemas
class TrackedCompanyBase(BaseModel):
    company_symbol: str

class TrackedCompanyCreate(TrackedCompanyBase):
    user_id: int

class TrackedCompanyResponse(TrackedCompanyBase):
    id: int
    user_id: int
    added_at: datetime

    class Config:
        from_attributes = True