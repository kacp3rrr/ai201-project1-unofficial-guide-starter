"""Retrieval + grounded generation for The Unofficial Guide (M4 + M5).

Opens the persistent ChromaDB collection built by ingest.py, embeds a query
with the same all-MiniLM-L6-v2 model, retrieves the top-k most relevant chunks,
and (in retrieve_and_generate) feeds them to Groq's llama-3.3-70b-versatile to
produce an answer grounded only in the retrieved reviews.
"""

import os
import sys

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq

from ingest import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL

TOP_K = 5
GROQ_MODEL = "llama-3.3-70b-versatile"  # planning.md generation step

# Exact phrase the model must return when the context can't answer the question.
# Keeping it a constant lets us (and graders) detect refusals unambiguously.
REFUSAL_MESSAGE = "I don't have enough information on that."

# Grounding instruction. The model is told to use ONLY the retrieved context
# and to refuse rather than fall back on its training knowledge.
SYSTEM_PROMPT = (
    "You are The Unofficial Guide, answering questions about food options near "
    "CUNY Hunter College using ONLY the student and customer reviews provided "
    "as context.\n\n"
    "Rules:\n"
    "1. Answer using ONLY the information in the provided context. Never use "
    "outside or prior knowledge.\n"
    "2. If the context does not contain enough information to answer the "
    f"question, reply with exactly this sentence and nothing else: "
    f'"{REFUSAL_MESSAGE}"\n'
    "3. Be concise. Reflect the sentiment of the reviews, and note disagreement "
    "between reviewers when it exists.\n"
    "4. Do not invent prices, names, or details that are not in the context."
)

EVAL_QUERIES = [
    "What do students say about the Hunter College cafeteria?",
    "Is the Chipotle near Hunter worth going to?",
    "Where can I eat near Hunter if I'm on a budget?",
    "What do people say about the Halal carts near Hunter?",
    "How is service quality at Gourmet Bagel?",
]

# Lazily-initialized singletons so the Gradio app reuses one collection and one
# Groq client instead of reloading the embedding model on every request.
_collection = None
_groq_client = None

def get_collection():
    """Open the persisted collection with the matching embedding function.

    The collection must be reopened with the same SentenceTransformerEmbedding-
    Function used in ingest.py; ChromaDB persists the vectors, not the embedding
    model itself. Re-attaching it lets us query by raw text and have Chroma
    embed it with all-MiniLM-L6-v2 on our behalf.
    """
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    try:
        return client.get_collection(
            name=COLLECTION_NAME, embedding_function=embedding_fn
        )
    except Exception as exc:  # collection missing / store not built yet
        raise SystemExit(
            f"Could not open collection '{COLLECTION_NAME}' at ./{CHROMA_DIR}/.\n"
            f"Run `python ingest.py` first to build the vector store.\n({exc})"
        )

def retrieve(query: str, collection=None, k: int = TOP_K) -> list[dict]:
    """Return the top-k chunks most relevant to `query`.

    Each result is a dict with the chunk text, its source document and position
    (from the metadata stored at ingestion), and the cosine distance score
    (lower = more similar).
    """
    if collection is None:
        collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for text, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append(
            {
                "text": text,
                "source": meta["source"],
                "chunk_index": meta["chunk_index"],
                "distance": distance,
            }
        )
    return hits

def _get_cached_collection():
    """Open the collection once and reuse it across calls (app friendliness)."""
    global _collection
    if _collection is None:
        _collection = get_collection()
    return _collection

def _get_groq_client() -> Groq:
    """Create the Groq client once, reading GROQ_API_KEY from .env."""
    global _groq_client
    if _groq_client is None:
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_key_here":
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add "
                "your free key from https://console.groq.com"
            )
        _groq_client = Groq(api_key=api_key)
    return _groq_client

def _build_context(hits: list[dict]) -> str:
    """Format retrieved chunks into a labeled context block for the prompt.

    Each chunk is tagged with its source filename so the model sees which
    document every piece of evidence came from.
    """
    blocks = []
    for hit in hits:
        blocks.append(f"[Source: {hit['source']}]\n{hit['text']}")
    return "\n\n".join(blocks)

def _unique_sources(hits: list[dict]) -> list[str]:
    """Distinct source filenames in retrieval order (for attribution)."""
    seen = []
    for hit in hits:
        if hit["source"] not in seen:
            seen.append(hit["source"])
    return seen

def retrieve_and_generate(q: str, k: int = TOP_K) -> dict:
    """Answer question `q` grounded only in the top-k retrieved review chunks.

    Opens the existing ChromaDB collection, retrieves the most relevant chunks
    (embedded with the same model as ingest.py), passes them to Groq's
    llama-3.3-70b-versatile with a strict grounding instruction, and returns:

    {
      "answer":  str,          # model answer, or the refusal sentence
      "sources": list[str],    # distinct source files the context came from
      "hits":    list[dict],   # the raw retrieved chunks (text/source/dist)
    }

    If nothing is retrieved, or the model judges the context insufficient, the
    answer is the fixed REFUSAL_MESSAGE rather than an unfounded guess.
    """
    hits = retrieve(q, collection=_get_cached_collection(), k=k)
    if not hits:
        return {"answer": REFUSAL_MESSAGE, "sources": [], "hits": []}

    context = _build_context(hits)
    user_message = (
        f"Context (student and customer reviews):\n\n{context}\n\n"
        f"Question: {q}"
    )

    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.2,  # low: keep the answer close to the source text
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        answer = response.choices[0].message.content.strip()
    except Exception as exc:  # surface API/network errors in the UI, don't crash
        return {
            "answer": f"Generation failed: {exc}",
            "sources": [],
            "hits": hits,
        }

    # Attribution is only meaningful when the model actually answered. On a
    # refusal there is no grounded source to cite.
    sources = [] if answer == REFUSAL_MESSAGE else _unique_sources(hits)
    return {"answer": answer, "sources": sources, "hits": hits}

def print_results(query: str, hits: list[dict]) -> None:
    """Pretty-print retrieved chunks for inspection against the checkpoint."""
    print(f"\n{'=' * 70}\nQUERY: {query}\n{'=' * 70}")
    for rank, hit in enumerate(hits, start=1):
        print(
            f"\n[{rank}] {hit['source']} #{hit['chunk_index']}  "
            f"distance={hit['distance']:.3f}"
        )
        print(hit["text"])

def main() -> None:
    collection = get_collection()

    # QOL feature to pass a question as command-line arg 
    queries = sys.argv[1:] or EVAL_QUERIES
    for query in queries:
        hits = retrieve(query, collection=collection)
        print_results(query, hits)

    print(
        f"\n{'=' * 70}\nCheckpoint: top-result distances should be < 0.5 "
        "and visibly on-topic."
    )

if __name__ == "__main__":
    main()
