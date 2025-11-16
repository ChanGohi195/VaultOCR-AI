"""
Document Manager - Manages OCR documents with SQLite (free, built-in Python)
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import sqlite3
import json
import datetime
import hashlib


class DocumentManager:
    """Manages OCR documents and metadata using SQLite"""

    def __init__(self, db_path: str = ".vaultocr.db"):
        """
        Initialize document manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()

        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                file_path TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ocr_date TIMESTAMP,
                page_count INTEGER DEFAULT 1,
                layout_type TEXT,
                section_count INTEGER DEFAULT 0,
                table_count INTEGER DEFAULT 0,
                tags TEXT,
                metadata TEXT
            )
        """)

        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Document-Tag junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_tags (
                document_id TEXT,
                tag_id INTEGER,
                PRIMARY KEY (document_id, tag_id),
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_title ON documents(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)")

        self.conn.commit()

    def _generate_doc_id(self, file_path: str) -> str:
        """Generate unique document ID from file path"""
        return hashlib.md5(file_path.encode()).hexdigest()

    def add_document(
        self,
        title: str,
        file_path: str,
        content: str = "",
        metadata: Dict[str, Any] = None,
        tags: List[str] = None
    ) -> str:
        """
        Add new document

        Returns:
            Document ID
        """
        doc_id = self._generate_doc_id(file_path)
        cursor = self.conn.cursor()

        metadata = metadata or {}

        cursor.execute("""
            INSERT OR REPLACE INTO documents (
                id, title, file_path, content, ocr_date,
                page_count, layout_type, section_count, table_count,
                tags, metadata, modified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            title,
            file_path,
            content,
            datetime.datetime.now(),
            metadata.get('page_count', 1),
            metadata.get('layout_type', 'unknown'),
            metadata.get('section_count', 0),
            metadata.get('total_tables', 0),
            ','.join(tags) if tags else '',
            json.dumps(metadata),
            datetime.datetime.now()
        ))

        # Add tags
        if tags:
            for tag in tags:
                self.add_tag(tag)
                tag_id = self.get_tag_id(tag)
                if tag_id:
                    cursor.execute("""
                        INSERT OR IGNORE INTO document_tags (document_id, tag_id)
                        VALUES (?, ?)
                    """, (doc_id, tag_id))

        self.conn.commit()
        return doc_id

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_document_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get document by file path"""
        doc_id = self._generate_doc_id(file_path)
        return self.get_document(doc_id)

    def update_document(
        self,
        doc_id: str,
        title: str = None,
        content: str = None,
        metadata: Dict[str, Any] = None,
        tags: List[str] = None
    ):
        """Update existing document"""
        cursor = self.conn.cursor()

        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)

        if content is not None:
            updates.append("content = ?")
            params.append(content)

        if metadata is not None:
            if 'page_count' in metadata:
                updates.append("page_count = ?")
                params.append(metadata['page_count'])
            if 'layout_type' in metadata:
                updates.append("layout_type = ?")
                params.append(metadata['layout_type'])
            if 'section_count' in metadata:
                updates.append("section_count = ?")
                params.append(metadata['section_count'])
            if 'total_tables' in metadata:
                updates.append("table_count = ?")
                params.append(metadata['total_tables'])

            updates.append("metadata = ?")
            params.append(json.dumps(metadata))

        updates.append("modified_at = ?")
        params.append(datetime.datetime.now())

        params.append(doc_id)

        if updates:
            cursor.execute(f"""
                UPDATE documents
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)

        # Update tags
        if tags is not None:
            # Remove existing tags
            cursor.execute("DELETE FROM document_tags WHERE document_id = ?", (doc_id,))

            # Add new tags
            for tag in tags:
                self.add_tag(tag)
                tag_id = self.get_tag_id(tag)
                if tag_id:
                    cursor.execute("""
                        INSERT OR IGNORE INTO document_tags (document_id, tag_id)
                        VALUES (?, ?)
                    """, (doc_id, tag_id))

        self.conn.commit()

    def delete_document(self, doc_id: str):
        """Delete document"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        self.conn.commit()

    def list_documents(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = 'modified_at',
        order_desc: bool = True
    ) -> List[Dict[str, Any]]:
        """List all documents"""
        cursor = self.conn.cursor()

        order_clause = f"{order_by} {'DESC' if order_desc else 'ASC'}"

        cursor.execute(f"""
            SELECT * FROM documents
            ORDER BY {order_clause}
            LIMIT ? OFFSET ?
        """, (limit, offset))

        return [dict(row) for row in cursor.fetchall()]

    def add_tag(self, tag_name: str, color: str = None):
        """Add new tag"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO tags (name, color)
            VALUES (?, ?)
        """, (tag_name, color))
        self.conn.commit()

    def get_tag_id(self, tag_name: str) -> Optional[int]:
        """Get tag ID by name"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        row = cursor.fetchone()
        return row['id'] if row else None

    def get_all_tags(self) -> List[Dict[str, Any]]:
        """Get all tags"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tags ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def get_documents_by_tag(self, tag_name: str) -> List[Dict[str, Any]]:
        """Get all documents with specific tag"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT d.* FROM documents d
            JOIN document_tags dt ON d.id = dt.document_id
            JOIN tags t ON dt.tag_id = t.id
            WHERE t.name = ?
            ORDER BY d.modified_at DESC
        """, (tag_name,))

        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM documents")
        total_docs = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM tags")
        total_tags = cursor.fetchone()['count']

        cursor.execute("SELECT SUM(page_count) as total FROM documents")
        total_pages = cursor.fetchone()['total'] or 0

        return {
            'total_documents': total_docs,
            'total_tags': total_tags,
            'total_pages': total_pages
        }

    def close(self):
        """Close database connection"""
        self.conn.close()
