import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.models.document import Document, DocumentChunk
from backend.app.schemas.document import DocumentResponse
from backend.app.services.parser import DocumentParser
from backend.app.services.vector_store import QdrantVectorStore

router = APIRouter(prefix="/documents", tags=["Documents"])
UPLOAD_DIR = "./data/uploads"

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate extension
    filename = file.filename
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ["pdf", "docx", "txt"]:
        raise HTTPException(
            status_code=400,
            detail="Seuls les formats PDF, DOCX et TXT sont acceptés."
        )

    # Make upload directory
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique storage path
    file_path = os.path.join(UPLOAD_DIR, f"{uuid_name(filename)}")
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde du fichier : {str(e)}")

    file_size = os.path.getsize(file_path)

    # Create document in DB
    db_doc = Document(
        filename=filename,
        filepath=file_path,
        file_type=ext,
        file_size=file_size,
        status="processing",
        owner_id=current_user.id
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    try:
        # Extract content
        text = DocumentParser.extract_text(file_path, ext)
        # Chunk text
        chunks = DocumentParser.chunk_text(text)
        
        if not chunks:
            raise ValueError("Le document ne contient pas de texte extractible.")

        # Index in Qdrant
        qdrant_ids = QdrantVectorStore.index_chunks(
            document_id=db_doc.id,
            owner_id=current_user.id,
            filename=filename,
            chunks=chunks
        )

        # Store chunks in SQL Database
        for idx, (chunk_text, qid) in enumerate(zip(chunks, qdrant_ids)):
            db_chunk = DocumentChunk(
                document_id=db_doc.id,
                chunk_index=idx,
                content=chunk_text,
                qdrant_id=qid
            )
            db.add(db_chunk)
            
        db_doc.status = "indexed"
        db.commit()
        db.refresh(db_doc)
        
    except Exception as e:
        db_doc.status = "failed"
        db.commit()
        # Clean up files if processing failed completely and file is corrupted
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'indexation du document : {str(e)}"
        )

    return db_doc

@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Document).filter(Document.owner_id == current_user.id).all()

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé.")

    # Remove from Qdrant
    try:
        QdrantVectorStore.delete_document_points(document_id)
    except Exception as e:
        pass

    # Remove from local files
    if os.path.exists(doc.filepath):
        try:
            os.remove(doc.filepath)
        except:
            pass

    # Delete from DB
    db.delete(doc)
    db.commit()
    return None

def uuid_name(orig_name: str) -> str:
    import uuid
    ext = orig_name.split(".")[-1] if "." in orig_name else ""
    return f"{uuid.uuid4()}.{ext}"
