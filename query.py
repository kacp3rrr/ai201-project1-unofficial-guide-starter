"""Retrieval for The Unofficial Guide (M4).

Opens the persistent ChromaDB collection built by ingest.py, embeds a query
with the same all-MiniLM-L6-v2 model, and returns the top-k most relevant
chunks with their text, source, and distance score.
"""

import sys
import chromadb
from chromadb.utils import embedding_functions

from ingest import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL

TOP_K = 5  
EVAL_QUERIES = [
    "What do students say about the Hunter College cafeteria?",
    "Is the Chipotle near Hunter worth going to?",
    "Where can I eat near Hunter if I'm on a budget?",
    "What do people say about the Halal carts near Hunter?",
    "How is service quality at Gourmet Bagel?",
]

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
