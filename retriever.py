import chromadb
from chromadb.utils import embedding_functions
from config import CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, N_RESULTS

# Embedding function and ChromaDB client are initialized once at module load.
# sentence-transformers downloads the model on first use — this may take
# 30–60 seconds the very first time. Subsequent runs use a local cache.
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    """Return the ChromaDB collection. Used by app.py during ingestion."""
    return _collection


def embed_and_store(chunks):
    """
    Embed a list of chunks and store them in the vector database.
    """
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{
            "title": c["title"],
            "source": c["source"],
            "url": c["url"],
            "position": c["position"]
        } for c in chunks],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} total chunks in the vector database.")


def retrieve(query, n_results=N_RESULTS):
    """
    Find the most relevant rule chunks for a user's question.
    """
    if _collection.count() == 0:
        return []

    # Your implementation here.
    chunks = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    documents = chunks["documents"][0] if chunks["documents"] else []
    metadatas = chunks["metadatas"][0] if chunks["documents"] else []
    distances = chunks["distances"][0] if chunks["documents"] else []

    output = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        print(f"[{meta['title']}] (dist: {dist:.3f}) {doc[:80]}...")
        output.append({
            "text": doc,
            "title": meta["title"],
            "source": meta["source"],
            "url": meta["url"],
            "distance": dist
        })

    return output
