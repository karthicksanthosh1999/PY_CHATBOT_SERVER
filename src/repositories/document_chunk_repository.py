from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import DocumentChunk

class DocumentChunkRepository:
    
    def create_many(self, db: Session, chunks: list[dict]):
        records = [
            DocumentChunk(**chunk)
            for chunk in chunks
        ]

        db.add_all(records)
        db.commit()

        return records

    def search_similar_chunks(self, db: Session, query_embedding: list[float], limit: int = 5):

        distance = DocumentChunk.embedding_cosine_distance(query_embedding)

        statement = select(DocumentChunk, distance.label("distance")).order_by(distance.asc()).limit(limit)

        return db.execute(statement).all()

    def delete_by_document_id(self, db: Session, document_id: int):
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete(synchronize_session=False)

        db.commit()