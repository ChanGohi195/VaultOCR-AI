"""
Search Engine - Full-text search using Whoosh (Pure Python, completely free)
"""
from typing import Dict, Any, List
from pathlib import Path
import os

from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME, KEYWORD
from whoosh.qparser import MultifieldParser, QueryParser
from whoosh.analysis import StemmingAnalyzer
import datetime


class SearchEngine:
    """Full-text search engine using Whoosh (free, no API calls)"""

    def __init__(self, index_dir: str = ".vaultocr_index"):
        """
        Initialize search engine

        Args:
            index_dir: Directory to store search index
        """
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(exist_ok=True)

        # Define schema
        self.schema = Schema(
            doc_id=ID(stored=True, unique=True),
            title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
            content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
            path=TEXT(stored=True),
            tags=KEYWORD(stored=True, commas=True, scorable=True),
            created=DATETIME(stored=True),
            modified=DATETIME(stored=True),
            page_count=TEXT(stored=True),
            layout_type=TEXT(stored=True),
        )

        # Create or open index
        if index.exists_in(str(self.index_dir)):
            self.ix = index.open_dir(str(self.index_dir))
        else:
            self.ix = index.create_in(str(self.index_dir), self.schema)

    def add_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        path: str,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Add document to search index

        Args:
            doc_id: Unique document identifier
            title: Document title
            content: Full text content
            path: File path
            tags: List of tags
            metadata: Additional metadata
        """
        writer = self.ix.writer()

        now = datetime.datetime.now()

        writer.add_document(
            doc_id=doc_id,
            title=title,
            content=content,
            path=path,
            tags=",".join(tags) if tags else "",
            created=metadata.get('created', now) if metadata else now,
            modified=now,
            page_count=str(metadata.get('page_count', 1)) if metadata else "1",
            layout_type=metadata.get('layout_type', 'unknown') if metadata else 'unknown'
        )

        writer.commit()

    def update_document(
        self,
        doc_id: str,
        title: str = None,
        content: str = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """Update existing document in index"""
        writer = self.ix.writer()

        # Read existing document
        with self.ix.searcher() as searcher:
            results = searcher.search(QueryParser("doc_id", self.ix.schema).parse(doc_id))
            if results:
                existing = results[0]

                writer.update_document(
                    doc_id=doc_id,
                    title=title or existing.get('title', ''),
                    content=content or existing.get('content', ''),
                    path=existing.get('path', ''),
                    tags=",".join(tags) if tags else existing.get('tags', ''),
                    created=existing.get('created', datetime.datetime.now()),
                    modified=datetime.datetime.now(),
                    page_count=str(metadata.get('page_count', 1)) if metadata else existing.get('page_count', '1'),
                    layout_type=metadata.get('layout_type', 'unknown') if metadata else existing.get('layout_type', 'unknown')
                )

        writer.commit()

    def delete_document(self, doc_id: str):
        """Delete document from index"""
        writer = self.ix.writer()
        writer.delete_by_term('doc_id', doc_id)
        writer.commit()

    def search(
        self,
        query: str,
        limit: int = 20,
        fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search documents

        Args:
            query: Search query string
            limit: Maximum number of results
            fields: Fields to search (default: title, content)

        Returns:
            List of matching documents with scores
        """
        if not query.strip():
            return []

        if fields is None:
            fields = ['title', 'content']

        # Create multi-field parser
        parser = MultifieldParser(fields, schema=self.ix.schema)

        with self.ix.searcher() as searcher:
            q = parser.parse(query)
            results = searcher.search(q, limit=limit)

            docs = []
            for hit in results:
                docs.append({
                    'doc_id': hit['doc_id'],
                    'title': hit['title'],
                    'path': hit['path'],
                    'score': hit.score,
                    'tags': hit['tags'].split(',') if hit['tags'] else [],
                    'page_count': hit.get('page_count', '1'),
                    'layout_type': hit.get('layout_type', 'unknown'),
                    'snippet': hit.highlights('content', top=3) if 'content' in fields else None
                })

            return docs

    def search_by_tag(self, tag: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search documents by tag"""
        return self.search(f"tags:{tag}", limit=limit, fields=['tags'])

    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
        tags = set()

        with self.ix.searcher() as searcher:
            for doc in searcher.documents():
                if doc.get('tags'):
                    tags.update(doc['tags'].split(','))

        return sorted([t for t in tags if t.strip()])

    def get_statistics(self) -> Dict[str, Any]:
        """Get search index statistics"""
        with self.ix.searcher() as searcher:
            return {
                'total_documents': searcher.doc_count_all(),
                'total_tags': len(self.get_all_tags()),
                'index_size_mb': sum(
                    f.stat().st_size for f in self.index_dir.glob('*')
                ) / (1024 * 1024)
            }
