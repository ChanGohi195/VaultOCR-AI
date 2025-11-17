"""
Vector Search Engine - Phase 8
Semantic search using sentence-transformers and FAISS
Supports cross-lingual search across 50+ languages
"""
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path
import pickle
import json


class VectorSearchEngine:
    """
    Vector-based semantic search engine
    Uses sentence-transformers for multilingual embeddings
    Uses FAISS for efficient similarity search
    """

    def __init__(self, index_dir: str = './data/vector_index',
                 model_name: str = 'paraphrase-multilingual-mpnet-base-v2'):
        """
        Initialize vector search engine

        Args:
            index_dir: Directory to store FAISS index and metadata
            model_name: Sentence-transformers model name
                       Default: paraphrase-multilingual-mpnet-base-v2 (50+ languages)
                       Alternative: distiluse-base-multilingual-cased-v2 (lighter, 15 languages)
        """
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.model_name = model_name
        self._model = None
        self._index = None

        # Document metadata: doc_id -> {title, content, embedding, ...}
        self.documents = {}

        # Load existing index if available
        self._load_index()

    @property
    def model(self):
        """Lazy load sentence-transformers model"""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def index(self):
        """Lazy load FAISS index"""
        if self._index is None:
            import faiss
            # Create empty index (768 dimensions for mpnet-base)
            dimension = 768
            self._index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
        return self._index

    def add_document(self, doc_id: str, title: str, content: str,
                     metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add document to vector index

        Args:
            doc_id: Unique document ID
            title: Document title
            content: Document content (full text)
            metadata: Additional metadata
        """
        # Combine title and content for better semantic representation
        text_to_embed = f"{title}\n\n{content}"

        # Generate embedding
        embedding = self.model.encode(text_to_embed, convert_to_numpy=True)

        # Normalize for cosine similarity (IndexFlatIP requires normalized vectors)
        embedding = embedding / np.linalg.norm(embedding)

        # Add to FAISS index
        self.index.add(np.array([embedding], dtype=np.float32))

        # Store metadata
        self.documents[doc_id] = {
            'title': title,
            'content': content,
            'embedding': embedding.tolist(),  # For serialization
            'index_position': len(self.documents),  # Position in FAISS index
            'metadata': metadata or {}
        }

    def add_documents_batch(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add multiple documents in batch

        Args:
            documents: List of document dicts with keys: doc_id, title, content, metadata
        """
        texts_to_embed = []
        doc_ids = []

        for doc in documents:
            doc_id = doc['doc_id']
            title = doc.get('title', '')
            content = doc.get('content', '')

            texts_to_embed.append(f"{title}\n\n{content}")
            doc_ids.append(doc_id)

        # Batch embedding (faster than one-by-one)
        embeddings = self.model.encode(texts_to_embed, convert_to_numpy=True, show_progress_bar=True)

        # Normalize
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        # Add to FAISS index
        self.index.add(embeddings.astype(np.float32))

        # Store metadata
        for i, doc in enumerate(documents):
            doc_id = doc['doc_id']
            self.documents[doc_id] = {
                'title': doc.get('title', ''),
                'content': doc.get('content', ''),
                'embedding': embeddings[i].tolist(),
                'index_position': len(self.documents) + i,
                'metadata': doc.get('metadata', {})
            }

    def search(self, query: str, top_k: int = 10, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Semantic search

        Args:
            query: Search query (any language)
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of search results with scores
        """
        if not self.documents:
            return []

        # Generate query embedding
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        # Search FAISS index
        scores, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32),
            min(top_k, len(self.documents))
        )

        # Prepare results
        results = []
        doc_ids_list = list(self.documents.keys())

        for score, idx in zip(scores[0], indices[0]):
            if score >= threshold and idx < len(doc_ids_list):
                doc_id = doc_ids_list[idx]
                doc_data = self.documents[doc_id]

                results.append({
                    'doc_id': doc_id,
                    'title': doc_data['title'],
                    'content': doc_data['content'][:500],  # Preview
                    'score': float(score),
                    'metadata': doc_data.get('metadata', {})
                })

        return results

    def find_similar(self, doc_id: str, top_k: int = 5, exclude_self: bool = True) -> List[Dict[str, Any]]:
        """
        Find similar documents to a given document

        Args:
            doc_id: Document ID to find similar documents for
            top_k: Number of similar documents to return
            exclude_self: Whether to exclude the document itself

        Returns:
            List of similar documents with scores
        """
        if doc_id not in self.documents:
            return []

        # Get document embedding
        doc_embedding = np.array(self.documents[doc_id]['embedding'], dtype=np.float32)
        doc_embedding = doc_embedding / np.linalg.norm(doc_embedding)

        # Search FAISS index
        k = top_k + 1 if exclude_self else top_k
        scores, indices = self.index.search(np.array([doc_embedding]), min(k, len(self.documents)))

        # Prepare results
        results = []
        doc_ids_list = list(self.documents.keys())

        for score, idx in zip(scores[0], indices[0]):
            if idx < len(doc_ids_list):
                similar_doc_id = doc_ids_list[idx]

                # Skip self if requested
                if exclude_self and similar_doc_id == doc_id:
                    continue

                doc_data = self.documents[similar_doc_id]
                results.append({
                    'doc_id': similar_doc_id,
                    'title': doc_data['title'],
                    'content': doc_data['content'][:500],
                    'score': float(score),
                    'metadata': doc_data.get('metadata', {})
                })

        return results[:top_k]

    def update_document(self, doc_id: str, title: str = None, content: str = None,
                       metadata: Dict[str, Any] = None) -> None:
        """
        Update existing document
        Note: FAISS doesn't support in-place updates, so we need to rebuild index
        """
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")

        # Update metadata
        if title is not None:
            self.documents[doc_id]['title'] = title
        if content is not None:
            self.documents[doc_id]['content'] = content
        if metadata is not None:
            self.documents[doc_id]['metadata'].update(metadata)

        # Rebuild index (expensive operation)
        self._rebuild_index()

    def delete_document(self, doc_id: str) -> None:
        """
        Delete document from index
        Note: FAISS doesn't support deletion, so we need to rebuild index
        """
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Rebuild FAISS index from scratch"""
        import faiss

        if not self.documents:
            self._index = faiss.IndexFlatIP(768)
            return

        # Collect all embeddings
        embeddings = []
        for doc_id in self.documents:
            embedding = np.array(self.documents[doc_id]['embedding'], dtype=np.float32)
            embeddings.append(embedding)

        embeddings = np.array(embeddings)

        # Create new index
        dimension = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dimension)
        self._index.add(embeddings)

        # Update index positions
        for i, doc_id in enumerate(self.documents):
            self.documents[doc_id]['index_position'] = i

    def save_index(self) -> None:
        """Save FAISS index and metadata to disk"""
        import faiss

        # Save FAISS index
        index_path = self.index_dir / 'faiss.index'
        faiss.write_index(self.index, str(index_path))

        # Save document metadata (without embeddings to reduce size)
        metadata_path = self.index_dir / 'metadata.json'
        metadata_to_save = {}
        for doc_id, doc_data in self.documents.items():
            metadata_to_save[doc_id] = {
                'title': doc_data['title'],
                'content': doc_data['content'],
                'index_position': doc_data['index_position'],
                'metadata': doc_data['metadata']
            }

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_to_save, f, ensure_ascii=False, indent=2)

        # Save embeddings separately (binary format for efficiency)
        embeddings_path = self.index_dir / 'embeddings.pkl'
        embeddings = {doc_id: doc_data['embedding'] for doc_id, doc_data in self.documents.items()}
        with open(embeddings_path, 'wb') as f:
            pickle.dump(embeddings, f)

        print(f"✓ Vector index saved: {len(self.documents)} documents")

    def _load_index(self) -> None:
        """Load FAISS index and metadata from disk"""
        import faiss

        index_path = self.index_dir / 'faiss.index'
        metadata_path = self.index_dir / 'metadata.json'
        embeddings_path = self.index_dir / 'embeddings.pkl'

        if not index_path.exists() or not metadata_path.exists():
            return

        try:
            # Load FAISS index
            self._index = faiss.read_index(str(index_path))

            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Load embeddings
            if embeddings_path.exists():
                with open(embeddings_path, 'rb') as f:
                    embeddings = pickle.load(f)
            else:
                embeddings = {}

            # Reconstruct documents
            for doc_id, doc_data in metadata.items():
                self.documents[doc_id] = {
                    **doc_data,
                    'embedding': embeddings.get(doc_id, [])
                }

            print(f"✓ Vector index loaded: {len(self.documents)} documents")

        except Exception as e:
            print(f"✗ Failed to load vector index: {e}")
            self.documents = {}

    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            'total_documents': len(self.documents),
            'index_dimension': 768,
            'model_name': self.model_name,
            'index_type': 'FAISS IndexFlatIP (Cosine Similarity)'
        }

    def clear(self) -> None:
        """Clear all documents and rebuild empty index"""
        import faiss
        self.documents = {}
        self._index = faiss.IndexFlatIP(768)
