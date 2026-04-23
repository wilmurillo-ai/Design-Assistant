"""
embedding_store.py - Chroma 向量存储 + 语义搜索
配合结构化检索实现双路检索
"""

import os
import hashlib
import logging

logger = logging.getLogger(__name__)


class EmbeddingStore:
    """基于 Chroma 的语义向量存储"""

    def __init__(
        self,
        persist_dir: str = None,
        model_name: str = "all-MiniLM-L6-v2",
        collection_name: str = "agent_memory",
    ):
        import chromadb

        self.persist_dir = persist_dir or os.path.join(
            os.path.dirname(__file__), "chroma_db"
        )
        os.makedirs(self.persist_dir, exist_ok=True)

        # Chroma 客户端（持久化）
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # Embedding 模型（首次加载会下载 ~80MB）
        # 如果下载失败，降级为 hash-based embedding
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name, device="cpu")
            self._use_model = True
            logger.info(f"Embedding model '{model_name}' loaded")
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}, using hash fallback")
            self.model = None
            self._use_model = False

    def _encode(self, text: str) -> list[float]:
        """编码文本为向量"""
        if self._use_model:
            return self.model.encode(text).tolist()
        else:
            # 降级：用 hash 生成固定维度的伪向量（仅供测试，无语义能力）
            return self._hash_embedding(text, dim=384)

    def _hash_embedding(self, text: str, dim: int = 384) -> list[float]:
        """基于 hash 的伪 embedding（降级方案）"""
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # 用 hash 扩展到 dim 维
        result = []
        for i in range(dim):
            byte_idx = (i * 7 + 3) % len(h)
            result.append((h[byte_idx] / 255.0) * 2 - 1)  # 归一化到 [-1, 1]
        return result

    def add(self, memory_id: str, content: str, metadata: dict = None):
        """添加一条记忆的向量"""
        embedding = self._encode(content)
        meta = metadata or {}
        meta["content_preview"] = content[:200]

        self.collection.upsert(
            ids=[memory_id],
            embeddings=[embedding],
            metadatas=[meta],
            documents=[content],
        )

    def add_batch(self, items: list[dict]):
        """批量添加
        items: [{"memory_id": str, "content": str, "metadata": dict}, ...]
        """
        if not items:
            return

        ids = [it["memory_id"] for it in items]
        contents = [it["content"] for it in items]
        embeddings = [self._encode(c) for c in contents]
        metadatas = []
        for it in items:
            m = it.get("metadata") or {}
            m["content_preview"] = it["content"][:200]
            metadatas.append(m)

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=contents,
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: dict = None,
    ) -> list[dict]:
        """语义搜索
        返回: [{"memory_id": str, "score": float, "content": str, "metadata": dict}, ...]
        """
        query_embedding = self._encode(query)

        where = filter_metadata if filter_metadata else None
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        output = []
        if results and results["ids"] and results["ids"][0]:
            for i, mid in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                # cosine distance → similarity score (0~1, 1=最相似)
                score = max(0.0, 1.0 - distance)
                output.append({
                    "memory_id": mid,
                    "score": round(score, 4),
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                })

        return output

    def delete(self, memory_id: str):
        """删除一条向量"""
        self.collection.delete(ids=[memory_id])

    def count(self) -> int:
        """返回存储的向量数量"""
        return self.collection.count()

    @staticmethod
    def content_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
