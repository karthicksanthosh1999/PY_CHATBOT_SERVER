from sqlalchemy import select 
from sqlalchemy.orm import Session

from src.database.models import Document

class DocumentRepository:

    def create(self, db: Session, data: dict):
        document = Document(**data)
        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    def find_by_id(self, db: Session, document_id: int, user_id: int):
        statement = select(Document).where(Document.id == document_id, Document.user_id == user_id)

        return db.scalar(statement)

    def update_status(self, db: Session, document: Document, status: str, chunk_count: int | None = None):

        document.status = status

        if chunk_count is not None:
            document.chunk_count = chunk_count

        db.commit()
        db.refresh(document)

        return document