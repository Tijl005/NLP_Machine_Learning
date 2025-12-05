from crewai.tools import tool
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ww2_history_notes.txt")


def _load_history_text() -> str:
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "WW2 history notes file not found. Please check data/ww2_history_notes.txt."


@tool("search_history")
def search_history(query: str) -> str:
    """Search the small WW2 history notes and return relevant snippets."""
    text = _load_history_text()
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    query_lower = query.lower()
    scored = []
    for p in paragraphs:
        score = sum(1 for word in query_lower.split() if word in p.lower())
        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        return text

    top_paragraphs = [p for _, p in scored[:3]]
    return "\n\n".join(top_paragraphs)
