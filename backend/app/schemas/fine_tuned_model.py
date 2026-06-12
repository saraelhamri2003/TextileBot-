from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FineTunedModelCreate(BaseModel):
    model_name: str
    base_model: str
    training_data_path: str
    output_path: str
    description: Optional[str] = None

class FineTunedModelResponse(BaseModel):
    id: int
    user_id: int
    model_name: str
    base_model: str
    training_data_path: str
    output_path: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
