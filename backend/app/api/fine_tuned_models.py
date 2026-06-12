from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.fine_tuned_model import FineTunedModel
from backend.app.models.user import User
from backend.app.schemas.fine_tuned_model import FineTunedModelCreate, FineTunedModelResponse

router = APIRouter(prefix="/models", tags=["Fine-tuned Models"])

@router.post("/fine-tuned", response_model=FineTunedModelResponse, status_code=status.HTTP_201_CREATED)
def create_fine_tuned_model(
    model_in: FineTunedModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = FineTunedModel(
        user_id=current_user.id,
        model_name=model_in.model_name,
        base_model=model_in.base_model,
        training_data_path=model_in.training_data_path,
        output_path=model_in.output_path,
        description=model_in.description,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model

@router.get("/fine-tuned", response_model=List[FineTunedModelResponse])
def list_fine_tuned_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(FineTunedModel).filter(FineTunedModel.user_id == current_user.id).all()
