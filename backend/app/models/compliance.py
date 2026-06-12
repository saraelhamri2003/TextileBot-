from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class ComplianceReport(Base):
    __tablename__ = "compliance_reports"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    fiber_composition = Column(String, nullable=False) # e.g. "80% Coton, 20% Polyester"
    intended_market = Column(String, nullable=False) # e.g. "Union Européenne"
    label_text = Column(Text, nullable=True) # Text on the label to verify
    analysis_result = Column(Text, nullable=False) # JSON or markdown string of evaluation results
    status = Column(String, default="compliant") # 'compliant', 'non_compliant', 'conditional'
    pdf_path = Column(String, nullable=True) # Path to generated report PDF
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="compliance_reports")
