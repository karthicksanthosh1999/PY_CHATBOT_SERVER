import uuid

from pathlib import Path
from sqlalchemy.orm import Session

from src.services.document_loader_service import DocumentLoaderService
from src.services.chunk_service import ChunkService
from src.services.embadding_service import EmbeddingService

from src.repositories.document_repository import DocumentRepository
from src.repositories.document_chunk_repository import DocumentChunkRepository


class DocumentService:

    def __init__(self):
        self.loader = DocumentLoaderService()
        self.chunking_service = ChunkService()
        self.embedding_service = EmbeddingService()

        self.document_repository = DocumentRepository()
        self.chunk_repository = DocumentChunkRepository()

    def upload_and_index(self, db: Session, user_id: int, fileName: str, file_content: bytes):
        allowed_extensions=(".pdf", ".docx", ".txt")

        extension = Path(fileName).suffix.lower()

        if extension not in allowed_extensions:
            raise ValueError("Unsupported file is empty")

        if not file_content:
            raise ValueError("Uploaded file is empty")

        upload_directory = Path("uploads")
        upload_directory.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid.uuid4().hex}{extension}"
        file_path = upload_directory / stored_filename

        document = None

        try:
            # 1. SAVE UPLOADED FILE
            with file_path.open("wb") as file:
                file.write(file_content)

            # 2. CREATE DOCUMENT RECORD
            document = self.document_repository.create(db, 
                                                       {
                                                           "user_id" : user_id,
                                                           "fileName" : Path(fileName).name,
                                                           "file_path" : str(file_path),
                                                           "status" : "processing"
                                                       }
                                                       )
            # 3. EXTRACT TEXT
            extract_text = self.loader.extract_text(str(file_path))

            if not extract_text.strip():
                raise ValueError("No readable text found in document")

            # 4. GENERATE CHUNKS
            chunks = self.chunking_service.recursive_chunking(extract_text, chunk_size=500, chunk_overlap=100)

            if not chunks:
                raise ValueError("No text chunks generated")

            # 5. GENERATE EMBEDDINGS
            embeddings = self.embedding_service.generate_embeddings(chunks)

            if len(chunks) != len(embeddings):
                raise RuntimeError("Chunk and embedding count mismatch")

            # 6. PREPARE CHUNK RECORDS
            chunk_records = []

            for index, (content, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_records.append({
                    "document_id" : document.id,
                    "chunk_index" : index,
                    "content" : content,
                    "embedding" : embedding
                })

            # 7. STORE CHUNKS AND EMBEDDINGS
            self.chunk_repository.create_many(db, chunk_records)

            # 8. UPDATE DOCUMENT STATUS
            self.document_repository.update_status(db, document, status="completed", chunk_count=len(chunks))
            return document

        except Exception:
            db.rollback()

            if document is not None:
                self.document_repository.update_status(db, document, status="failed")
                raise
            
            
