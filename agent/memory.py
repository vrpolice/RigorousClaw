import uuid
import os
import hashlib
from langchain_core.tools import tool
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

collection_name = "agent_memory"
VECTOR_DIM = 128  # We use a lightweight local hashing approach, no external embedding API needed

def get_qdrant_client():
    """Lazy initialize QdrantClient to avoid early initialization and shutdown errors."""
    client = QdrantClient(path="qdrant_db")
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
        )
    return client

def _text_to_vector(text: str) -> list:
    """
    Convert text to a simple deterministic vector using hashing.
    This is a lightweight, API-free embedding substitute.
    It works well enough for keyword-level similarity matching in a personal assistant.
    """
    # Use SHA-512 to get enough bytes, then normalize
    text_lower = text.lower().strip()
    hash_bytes = hashlib.sha512(text_lower.encode("utf-8")).digest()
    # Extend to fill VECTOR_DIM floats
    raw = []
    while len(raw) < VECTOR_DIM:
        hash_bytes = hashlib.sha512(hash_bytes).digest()
        for b in hash_bytes:
            raw.append((b / 255.0) * 2 - 1)  # normalize to [-1, 1]
            if len(raw) >= VECTOR_DIM:
                break
    # Also mix in word-level n-gram hashes for better semantic spread
    words = text_lower.split()
    for i, word in enumerate(words):
        idx = hash(word) % VECTOR_DIM
        raw[idx] = (raw[idx] + (1.0 if i % 2 == 0 else -1.0)) / 2.0
    # Normalize the vector
    magnitude = sum(x*x for x in raw) ** 0.5
    if magnitude > 0:
        raw = [x / magnitude for x in raw]
    return raw[:VECTOR_DIM]

@tool
def save_to_memory(fact: str) -> str:
    """
    Save an important fact, user preference, or project background into long-term memory.
    Use this proactively when the user tells you something you should remember for future conversations.
    Examples: user's name, preferences, project details, important decisions.
    """
    vector = _text_to_vector(fact)
    
    qdrant = get_qdrant_client()
    point_id = str(uuid.uuid4())
    qdrant.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={"fact": fact}
            )
        ]
    )
    qdrant.close()
    return f"Successfully saved to memory: '{fact}'"

@tool
def recall_from_memory(query: str) -> str:
    """
    Search the long-term memory for relevant past facts, preferences, or context.
    Use this whenever you need to remember something from a previous conversation or context you don't currently have.
    """
    vector = _text_to_vector(query)
    
    qdrant = get_qdrant_client()
    try:
        search_result = qdrant.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=5
        )
        
        qdrant.close()
        
        if not search_result:
            return f"No memories found matching the query: '{query}'."
            
        memories = [hit.payload.get("fact", "") for hit in search_result]
        return "Retrieved memories:\n" + "\n".join(f"- {m}" for m in memories)
        
    except Exception as e:
        qdrant.close()
        return f"Error retrieving from memory: {e}"

def auto_recall(query: str) -> str:
    """Non-tool version of recall for internal use by the graph (auto-context injection)."""
    vector = _text_to_vector(query)
    qdrant = get_qdrant_client()
    try:
        search_result = qdrant.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=3
        )
        qdrant.close()
        if not search_result:
            return ""
        memories = [hit.payload.get("fact", "") for hit in search_result]
        return "Relevant memories from past conversations:\n" + "\n".join(f"- {m}" for m in memories)
    except Exception:
        try:
            qdrant.close()
        except:
            pass
        return ""
