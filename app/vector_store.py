import numpy as np
import google.generativeai as genai
from app.db import supabase
from typing import List, Tuple

EMBED_MODEL = "models/embedding-001"
DIM = 768
TABLE_NAME = "documents"

def embed_text(text: str, task_type="retrieval_document") -> List[float]:
    res = genai.embed_content(model=EMBED_MODEL, content=text, task_type=task_type)
    emb = res["embedding"]
    return [float(x) for x in emb]

def add_to_index(text_chunk: str):
    vec = embed_text(text_chunk)
    # Insert into Supabase table
    data = {"chunk": text_chunk, "embedding": vec}
    resp = supabase.table(TABLE_NAME).insert(data).execute()
    if resp.status_code != 201 and resp.status_code != 200:
        raise RuntimeError(f"Failed to insert to Supabase: {resp.status_code} - {resp.data}")
    return resp.data

def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get_similar_chunks(query: str, k=3) -> List[str]:
    q_vec = np.array(embed_text(query, task_type="retrieval_query"), dtype=np.float32)
    # Fetch all documents (for small to medium datasets). For large datasets, migrate to pgvector similarity queries.
    resp = supabase.table(TABLE_NAME).select("id,chunk,embedding").execute()
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch documents from Supabase: {resp.status_code} - {resp.data}")
    rows = resp.data or []
    sims = []
    for row in rows:
        emb = np.array(row.get("embedding") or row.get("embedding", []), dtype=np.float32)
        sims.append((row.get("chunk"), _cosine_sim(q_vec, emb)))
    # sort by similarity descending
    sims.sort(key=lambda x: x[1], reverse=True)
    return [chunk for chunk, score in sims[:k]]
