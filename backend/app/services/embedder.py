import math
import hashlib

class Embedder:
    @classmethod
    def get_model(cls):
        return None

    @classmethod
    def embed_text(cls, text: str) -> list[float]:
        # Lightweight term-frequency hashing vectorizer
        # Maps text to a normalized 384-dimensional space
        dim = 384
        vector = [0.0] * dim
        
        words = text.lower().split()
        if not words:
            return vector
            
        for word in words:
            # Hash word to index
            h = hashlib.md5(word.encode('utf-8')).hexdigest()
            idx = int(h, 16) % dim
            vector[idx] += 1.0
            
        # Normalize vector
        magnitude = math.sqrt(sum(x*x for x in vector))
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
            
        return vector

    @classmethod
    def embed_batch(cls, texts: list[str]) -> list[list[float]]:
        return [cls.embed_text(t) for t in texts]

    @classmethod
    def get_dimension(cls) -> int:
        return 384
