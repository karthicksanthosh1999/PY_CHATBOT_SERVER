import pymupdf

from docx import Document
from pathlib import Path


class DocumentLoaderService:

    def extract_text(self, file_path: str):
        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return self.extract_pdf_text(file_path)
        elif extension == ".docx":
            return self.extract_docs_text(file_path)
        elif extension == ".txt":
            return self.extract_txt_text(file_path)
        else:
            raise ValueError("Unsupported File Format")

    def extract_pdf_text(self, file_path: str):
        extract_text = []

        with pymupdf.open(file_path) as document:
            for page in document:
                extract_text.append(page.get_text())

        return "\n".join(extract_text)

    def extract_docs_text(self, file_path: str):

        document = Document(file_path)

        extract_text = []

        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                extract_text.append(paragraph.text)
        return "\n".join(extract_text)

    def extract_txt_text(self, file_path: str):

        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    