import os
import chromadb
from chromadb.utils import embedding_functions
from crewai.tools import tool

# Pad naar je data
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "ww2_history_notes.txt")
DB_PATH = os.path.join(BASE_DIR, "data", "vector_db")

# Setup ChromaDB (de vector database)
client = chromadb.PersistentClient(path=DB_PATH)
# We gebruiken de standaard embedding functie (kan ook OpenAI zijn voor betere resultaten)
ef = embedding_functions.DefaultEmbeddingFunction() 
collection = client.get_or_create_collection(name="ww2_knowledge", embedding_function=ef)

def _init_db():
    """Lees het tekstbestand en vul de database als deze leeg is."""
    if collection.count() > 0:
        return # DB is al gevuld

    if not os.path.exists(DATA_PATH):
        print(f"Waarschuwing: {DATA_PATH} niet gevonden.")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Simpele split op lege regels (paragrafen)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    # Voeg toe aan ChromaDB
    ids = [f"id_{i}" for i in range(len(paragraphs))]
    collection.add(documents=paragraphs, ids=ids)
    print(f"Vector Database gevuld met {len(paragraphs)} items.")

# Initialiseer de DB bij het starten
_init_db()

@tool("search_history_vector")
def search_history_vector(query: str) -> str:
    """
    Search the WW2 history notes using a Vector Database for semantic similarity.
    Useful for finding specific facts, events, or explanations in the knowledge base.
    """
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    if not results["documents"]:
        return "No relevant information found in the notes."
        
    # Combineer de top 3 gevonden stukjes tekst
    return "\n\n".join(results["documents"][0])