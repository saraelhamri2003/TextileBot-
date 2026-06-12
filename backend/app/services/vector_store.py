import os
import uuid
import re
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from backend.app.config import settings
from backend.app.services.embedder import Embedder

class QdrantVectorStore:
    _client = None
    COLLECTION_NAME = "textile_rules"

    @classmethod
    def get_client(cls) -> QdrantClient:
        if cls._client is None:
            # If host is provided, connect to running Qdrant instance. Otherwise use local path/memory.
            if settings.QDRANT_HOST:
                cls._client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
            else:
                # Ensure the path directory exists
                if not settings.QDRANT_PATH.startswith(":") and not os.path.exists(settings.QDRANT_PATH):
                    os.makedirs(settings.QDRANT_PATH, exist_ok=True)
                cls._client = QdrantClient(path=settings.QDRANT_PATH)
            
            cls._initialize_collection()
        return cls._client

    @classmethod
    def _initialize_collection(cls):
        client = cls._client
        # Check if collection already exists
        collections = client.get_collections().collections
        exists = any(c.name == cls.COLLECTION_NAME for c in collections)
        
        if not exists:
            dim = Embedder.get_dimension()
            client.create_collection(
                collection_name=cls.COLLECTION_NAME,
                vectors_config=qmodels.VectorParams(
                    size=dim,
                    distance=qmodels.Distance.COSINE
                )
            )

    @classmethod
    def index_chunks(cls, document_id: int, owner_id: int, filename: str, chunks: list[str]) -> list[str]:
        client = cls.get_client()
        embeddings = Embedder.embed_batch(chunks)
        
        points = []
        qdrant_ids = []
        
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            qid = str(uuid.uuid4())
            qdrant_ids.append(qid)
            
            points.append(
                qmodels.PointStruct(
                    id=qid,
                    vector=vector,
                    payload={
                        "document_id": document_id,
                        "owner_id": owner_id,
                        "filename": filename,
                        "chunk_index": idx,
                        "content": chunk
                    }
                )
            )
            
        if points:
            client.upsert(
                collection_name=cls.COLLECTION_NAME,
                points=points
            )
            
        return qdrant_ids

    @classmethod
    def delete_document_points(cls, document_id: int):
        client = cls.get_client()
        client.delete(
            collection_name=cls.COLLECTION_NAME,
            points_selector=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="document_id",
                        match=qmodels.MatchValue(value=document_id)
                    )
                ]
            )
        )

    @classmethod
    def search_similar(cls, owner_id: int, query: str, limit: int = 5) -> list[dict]:
        client = cls.get_client()
        query_vector = Embedder.embed_text(query)
        
        # We filter by owner_id to ensure user documents are isolated, or load global rules
        # Let's support retrieving documents owned by the user.
        query_filter = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="owner_id",
                    match=qmodels.MatchValue(value=owner_id)
                )
            ]
        )

        if hasattr(client, "search"):
            search_result = client.search(
                collection_name=cls.COLLECTION_NAME,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=max(limit * 3, limit)
            )
        else:
            response = client.query_points(
                collection_name=cls.COLLECTION_NAME,
                query=query_vector,
                query_filter=query_filter,
                limit=max(limit * 3, limit),
                with_payload=True
            )
            search_result = response.points
        
        results = []
        for hit in search_result:
            content = hit.payload.get("content") or ""
            lexical_score = cls._lexical_score(query, content)
            vector_score = float(hit.score or 0)
            hybrid_score = round((0.68 * vector_score) + (0.32 * lexical_score), 4)
            results.append({
                "score": hybrid_score,
                "vector_score": vector_score,
                "lexical_score": lexical_score,
                "content": content,
                "document_id": hit.payload.get("document_id"),
                "filename": hit.payload.get("filename"),
                "chunk_index": hit.payload.get("chunk_index")
            })
            
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:limit]

    @staticmethod
    def _normalize(text: str) -> list[str]:
        if not text:
            return []
        text = text.lower()
        replacements = str.maketrans({
            "à": "a", "â": "a", "ä": "a", "á": "a",
            "ç": "c",
            "è": "e", "é": "e", "ê": "e", "ë": "e",
            "î": "i", "ï": "i",
            "ô": "o", "ö": "o",
            "ù": "u", "û": "u", "ü": "u",
        })
        text = text.translate(replacements)
        return [token for token in re.findall(r"[a-z0-9]{3,}", text) if token not in {"les", "des", "avec", "pour", "dans", "sur"}]

    @classmethod
    def _lexical_score(cls, query: str, content: str) -> float:
        query_terms = set(cls._normalize(query))
        if not query_terms:
            return 0.0
        content_terms = cls._normalize(content)
        if not content_terms:
            return 0.0
        content_set = set(content_terms)
        overlap = query_terms.intersection(content_set)
        coverage = len(overlap) / len(query_terms)
        phrase_bonus = 0.15 if " ".join(list(query_terms)[:2]) in " ".join(content_terms) else 0.0
        density = min(0.2, len(overlap) / max(len(content_terms), 1))
        return min(1.0, coverage + phrase_bonus + density)
