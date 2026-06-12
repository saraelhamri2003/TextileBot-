import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_user
from backend.app.database import get_db
from backend.app.models.compliance import ComplianceReport
from backend.app.models.user import User
from backend.app.schemas.compliance import ComplianceCheckRequest, ComplianceReportResponse
from backend.app.services.llm import LocalLLM
from backend.app.services.pdf_generator import PDFReportGenerator
from backend.app.services.vector_store import QdrantVectorStore

router = APIRouter(prefix="/compliance", tags=["Compliance Analysis"])
REPORT_DIR = "./data/reports"


@router.post("/check", response_model=ComplianceReportResponse, status_code=status.HTTP_201_CREATED)
def check_compliance(
    req: ComplianceCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    search_query = (
        "composition fibres etiquetage textile reglementation "
        f"{req.intended_market} {req.fiber_composition} {req.label_text or ''}"
    )
    try:
        contexts = QdrantVectorStore.search_similar(
            owner_id=current_user.id,
            query=search_query,
            limit=6,
        )
    except Exception:
        contexts = []

    analysis_result, status_resolved, confidence, references = LocalLLM.generate_compliance_analysis(
        product_name=req.product_name,
        fiber_composition=req.fiber_composition,
        intended_market=req.intended_market,
        label_text=req.label_text or "",
        contexts=contexts,
    )

    os.makedirs(REPORT_DIR, exist_ok=True)
    pdf_filename = f"report_{uuid.uuid4().hex}.pdf"
    pdf_path = os.path.join(REPORT_DIR, pdf_filename)

    try:
        PDFReportGenerator.generate_compliance_report(
            output_path=pdf_path,
            product_name=req.product_name,
            fiber_composition=req.fiber_composition,
            intended_market=req.intended_market,
            label_text=req.label_text or "",
            analysis_result=analysis_result,
            status=status_resolved,
            confidence=confidence,
            references=references,
            analyst_name=current_user.username,
        )
    except Exception:
        pdf_path = None

    report = ComplianceReport(
        product_name=req.product_name,
        fiber_composition=req.fiber_composition,
        intended_market=req.intended_market,
        label_text=req.label_text,
        analysis_result=analysis_result,
        status=status_resolved,
        pdf_path=pdf_path,
        user_id=current_user.id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/reports", response_model=List[ComplianceReportResponse])
def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ComplianceReport)
        .filter(ComplianceReport.user_id == current_user.id)
        .order_by(ComplianceReport.created_at.desc())
        .all()
    )


@router.get("/reports/{report_id}/download")
def download_report_pdf(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = (
        db.query(ComplianceReport)
        .filter(ComplianceReport.id == report_id, ComplianceReport.user_id == current_user.id)
        .first()
    )

    if not report or not report.pdf_path or not os.path.exists(report.pdf_path):
        raise HTTPException(status_code=404, detail="Rapport PDF non trouve.")

    return FileResponse(
        path=report.pdf_path,
        media_type="application/pdf",
        filename=f"Rapport_{report.product_name.replace(' ', '_')}.pdf",
    )
