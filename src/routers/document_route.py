import traceback

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
from sqlalchemy.orm import Session

from src.services.document_service import DocumentService
from src.database.models import User
from src.dependencies.auth_dependency import get_logged_user
from src.database.database import get_db

router = APIRouter(prefix="/documents", tags=['Documents'])

document_loader = DocumentService()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = (".pdf",".docx", ".txt")

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_logged_user)
):
    try:
        file_content = file.file.read()
        document = document_loader.upload_and_index(db, user_id=current_user.id, fileName=file.filename or "", file_content=file_content)

        return {
            "message" : "Document uploaded and indexed successfully",
            "document_id" : document.id,
            "fileName" : document.fileName,
            "status" : document.status,
            "chunk_count": document.chunk_count
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    except Exception as error:
        print("Document Indexing Error:", repr(error))
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Document indexing failed"
        ) from error

