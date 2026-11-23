from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkService:

    def fixed_size_chunk(self, text: str, chunk_size: int = 500, chunk_overlap: int = 100):

        if chunk_size <=0:
            raise ValueError("Chunk Size Must be Positive")

        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("Overlap Must be Non-negative and smaller then chunk size")

        text = text.strip()

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - chunk_overlap

        return chunks

    def recursive_chunking(self, text: str, chunk_size: int = 500, chunk_overlap: int = 100):
        if chunk_size < 0:
            raise ValueError("Chunk Size must be Positive")

        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("Invalid Chunk Overlap")

        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\n\n", "\n", ". ", " ", ""])

        chunk = splitter.split_text(text)
        return chunk
