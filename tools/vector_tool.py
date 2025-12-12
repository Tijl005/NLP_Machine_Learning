import os
import chromadb
from chromadb.utils import embedding_functions
from crewai.tools import tool
from docling.document_converter import DocumentConverter
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "vector_db")

# Setup ChromaDB
client = chromadb.PersistentClient(path=DB_PATH)
ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(name="ww2_knowledge", embedding_function=ef)

def add_document_to_knowledge_base(file_obj, filename):
    """
    Process an uploaded file (PDF, DOCX, TXT) and add it to the vector database.
    """
    try:
        chunks = []
        suffix = os.path.splitext(filename)[1].lower()

        # Simple text files (.txt) - read directly
        if suffix == '.txt':
            try:
                text = file_obj.getvalue().decode("utf-8")
                chunks = [p.strip() for p in text.split("\n\n") if p.strip()]
            except Exception as e:
                return False, f"Could not read text file (encoding error?): {str(e)}"

        # Complex files (PDF/DOCX) - process with Docling
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(file_obj.getvalue())
                tmp_path = tmp_file.name

            try:
                converter = DocumentConverter()
                result = converter.convert(tmp_path)
                markdown_text = result.document.export_to_markdown()
                chunks = [p.strip() for p in markdown_text.split("\n\n") if p.strip()]
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        if not chunks:
            return False, "No readable text found in document."

        # Add to ChromaDB
        current_count = collection.count()
        ids = [f"{filename}_{current_count + i}" for i in range(len(chunks))]
        metadatas = [{"source": filename} for _ in chunks]

        collection.add(documents=chunks, ids=ids, metadatas=metadatas)

        return True, f"Successfully added {len(chunks)} chunks from {filename}."

    except Exception as e:
        return False, f"Error processing document: {str(e)}"

@tool("search_history_vector")
def search_history_vector(query: str) -> str:
    """
    Search the WW2 history notes and uploaded documents using a Vector Database.
    Useful for finding specific facts, events, or explanations in the knowledge base.
    """
    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    if not results["documents"] or not results["documents"][0]:
        return "No relevant information found in the notes."

    return "\n\n".join(results["documents"][0])