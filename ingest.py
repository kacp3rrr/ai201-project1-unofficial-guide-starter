"""Ingestion pipeline for The Unofficial Guide (M3).

Loads plain-text documents from documents/, cleans Yelp/Reddit boilerplate out
of them, splits the result into fixed-size character chunks (400 chars, 50 char
overlap), embeds them with all-MiniLM-L6-v2, and stores them in a persistent
ChromaDB collection at /chroma_db.
"""

import html
import random
import re
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

# Use chunking patterns from spec in planning.md
DOCUMENTS_DIR = Path("documents")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "unofficial_guide"

# describing the number of characters:
CHUNK_SIZE = 400          
CHUNK_OVERLAP = 50        

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# CLEANING  
# Filter out common noise among the Yelp and Reddit documents using RegEx patterns, to 
# sanitze the output and reduce boilerplate noise (e.g Photos of, Posted on ...)
_BOILERPLATE_LINE_PATTERNS = [
    r"^Photo of .+$",                       # "Photo of Glenn F."
    r"^See all photos from .+$",
    r"^Business owner information$",
    r"^Business Customer Service$",
    r"^Elite \d+$",
    r"^All-Star$",
    r"^\d+$",                               # bare friend/review/photo counts
    r"^\d+\s+[\w/&. -]*\breviews?$",        # "26 Korean Food reviews"
    r"^\d+\s+photos?$",                     # "2 photos"
    r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}$",
    r"^https?://\S+$",
    r"^.+\.\s*Elite \d+$",                  # "Glenn F.Elite 26"
    r"^[\w .'-]+(?:,\s*[\w .'-]+)*,\s*[A-Z]{2}$",       # location "Brooklyn, NY"
    r"^[A-Z][A-Za-z.'-]*(?:\s+[A-Z][A-Za-z.'-]*){0,3}\s[A-Z]\.$",  # "Carly B."
    r"^.+\s-\sNew York, NY$",               # photo caption line
]
_BOILERPLATE_RE = [re.compile(p) for p in _BOILERPLATE_LINE_PATTERNS]

# Photo captions look like "Korean Express - Kimchi Stew - New York, NY" and
# are usually followed by a standalone copy of the middle segment ("Kimchi
# Stew"). Capturing those middles lets us drop the duplicate line too.
_CAPTION_RE = re.compile(r"^.+ - (.+) - New York, NY$")

def clean_text(text: str) -> str:
    """Strip HTML and Yelp/Reddit boilerplate, leaving review/opinion content.

    Operates line by line so a removed metadata line never takes adjacent
    review text with it.
    """
    text = html.unescape(text)            # &amp; -> &, &#39; -> '
    text = re.sub(r"<[^>]+>", "", text)   # defensive: strip any HTML tags

    caption_middles = {
        m.group(1).strip()
        for line in text.splitlines()
        if (m := _CAPTION_RE.match(line.strip()))
    }

    kept_lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            kept_lines.append("")
            continue
        if any(pattern.match(line) for pattern in _BOILERPLATE_RE):
            continue
        if line in caption_middles:        # duplicated photo-caption text
            continue
        kept_lines.append(line)

    cleaned = "\n".join(kept_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)  # collapse blank-line runs
    return cleaned.strip()

def load_documents(documents_dir: Path) -> list[dict]:
    """Read and clean every .txt file in documents_dir.

    Returns a list of {"source", "text"} dicts holding cleaned content. Files
    that are empty before or after cleaning are skipped so they can't produce
    empty chunks. Prints the cleaning reduction per file as a visible check.
    """
    documents = []
    for path in sorted(documents_dir.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        cleaned = clean_text(raw)
        if not cleaned:
            print(f"  skipping empty file: {path.name}")
            continue
        kept_pct = 100 * len(cleaned) / len(raw) if raw else 0
        print(f"  {path.name}: {len(raw)} -> {len(cleaned)} chars "
              f"({kept_pct:.0f}% kept)")
        documents.append({"source": path.name, "text": cleaned})

    return documents

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into fixed-size character chunks with overlap.

    Each chunk is `chunk_size` characters; consecutive chunks share `overlap`
    characters so information spanning a boundary isn't lost. The final chunk
    may be shorter than chunk_size. Empty/whitespace chunks are dropped.
    """
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    step = chunk_size - overlap
    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        # Stop once this chunk reached the end of the text.
        if start + chunk_size >= len(text):
            break

    return chunks

def build_chunks(documents: list[dict]) -> tuple[list[str], list[dict], list[str]]:
    """Turn loaded documents into parallel lists for ChromaDB.

    Returns (chunk_texts, metadatas, ids). Each chunk gets a stable id of the
    form "<source>::<index>" and metadata recording its source file and the
    chunk's position within that file.
    """
    chunk_texts: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    for doc in documents:
        source = doc["source"]
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunk_texts.append(chunk)
            metadatas.append({"source": source, "chunk_index": i})
            ids.append(f"{source}::{i}")
        print(f"  {source}: {len(chunks)} chunks")

    return chunk_texts, metadatas, ids

def inspect_chunks(chunk_texts: list[str], metadatas: list[dict],
                   n: int = 5, seed: int = 42) -> None:
    """Print n random chunks for the Milestone 3 inspection checkpoint.

    A fixed seed keeps the sample reproducible across runs. Read each one: it
    should be substantive and make sense on its own, with no HTML, fragments,
    or empty strings.
    """
    indices = random.Random(seed).sample(range(len(chunk_texts)), k=min(n, len(chunk_texts)))
    print(f"\n--- Inspecting {len(indices)} random chunks "
          f"(seed={seed}) -------------------")
    for idx in indices:
        meta = metadatas[idx]
        chunk = chunk_texts[idx]
        print(f"\n[{meta['source']} #{meta['chunk_index']}  len={len(chunk)}]")
        print(chunk)
    print("\n" + "-" * 60)

def main() -> None:
    if not DOCUMENTS_DIR.exists():
        raise SystemExit(f"Documents directory not found: {DOCUMENTS_DIR}")

    print(f"Loading and cleaning documents from {DOCUMENTS_DIR}/ ...")
    documents = load_documents(DOCUMENTS_DIR)
    if not documents:
        raise SystemExit(
            f"No non-empty .txt files found in {DOCUMENTS_DIR}/. "
            "Add your source documents and re-run."
        )
    print(f"Loaded {len(documents)} document(s).\n")

    print("Chunking documents ...")
    chunk_texts, metadatas, ids = build_chunks(documents)
    print(f"\nTotal chunks: {len(chunk_texts)}")

    inspect_chunks(chunk_texts, metadatas)

    # Reset the collection so each run rebuilds a clean index. Avoids manual deletion,
    # which I found particularly annoying to do when doing the tinker lab
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    print(f"\nEmbedding with {EMBEDDING_MODEL} and writing to ChromaDB ...")
    collection.add(documents=chunk_texts, metadatas=metadatas, ids=ids)

    print(
        f"\nDone. Stored {collection.count()} chunks in collection "
        f"'{COLLECTION_NAME}' at ./{CHROMA_DIR}/"
    )

if __name__ == "__main__":
    main()
