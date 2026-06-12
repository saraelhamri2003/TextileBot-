from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ComplianceCheckRequest(BaseModel):
    product_name: str
    fiber_composition: str
    intended_market: str
    label_text: Optional[str] = None

class ComplianceReportResponse(BaseModel):
    id: int
    product_name: str
    fiber_composition: str
    intended_market: str
    label_text: Optional[str] = None
    analysis_result: str
    status: str
    pdf_path: Optional[str] = None
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True
