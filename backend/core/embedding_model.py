from sentence_transformers import SentenceTransformer
import numpy as np

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embeddings(list: list[str]) -> list[float]:
    embeddings = embedding_model.encode(list)
    avg_embedding = np.mean(embeddings, axis=0)
    
    return avg_embedding.tolist()