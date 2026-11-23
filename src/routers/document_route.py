import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path

from src.services.document_loader_service import DocumentLoaderService

router = APIRouter(prefix="/documents", tags=['Documents'])

document_loader = DocumentLoaderService()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = (".pdf",".docs", ".txt")

@router.post("/upload")
def upload_document(file: UploadFile = File(...)):

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported Document Format")

    file_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{extension}"

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extracted_text = document_loader.extract_text(str(file_path))

        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No Extractable Text Found in Document")

        return {
            "message" : "Document Uploaded Successfully",
            "fileName" : file.filename,
            "character_count" : len(extracted_text),
            "extracted_text" : extracted_text
        }
    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(status_code=500, detail="Document Processing Failed") from error

    finally:
        file.file.close()