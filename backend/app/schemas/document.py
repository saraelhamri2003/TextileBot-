from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class DocumentChunkResponse(BaseModel):
    id: int
    chunk_index: int
    content: str

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    upload_date: datetime
    status: str
    owner_id: int

    class Config:
        from_attributes = True
