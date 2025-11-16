"""
OCR Server Handlers - Phase 4 handlers for search, export, etc.
"""
from typing import Dict, Any


def handle_search(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle search request"""
    query = request.get('query', '').strip()
    limit = request.get('limit', 20)

    if not query:
        return {'status': 'error', 'message': 'Query is required'}

    try:
        results = self.search_engine.search(query, limit=limit)

        return {
            'status': 'ok',
            'results': results
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def handle_save_document(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle save document request"""
    try:
        title = request.get('title', 'Untitled')
        file_path = request.get('file_path', '')
        content = request.get('content', '')
        metadata = request.get('metadata', {})
        tags = request.get('tags', [])

        # Save to document manager
        doc_id = self.document_manager.add_document(
            title=title,
            file_path=file_path,
            content=content,
            metadata=metadata,
            tags=tags
        )

        # Index for search
        self.search_engine.add_document(
            doc_id=doc_id,
            title=title,
            content=content,
            path=file_path,
            tags=tags,
            metadata=metadata
        )

        return {
            'status': 'ok',
            'doc_id': doc_id
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def handle_export(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle export request"""
    try:
        format = request.get('format', 'markdown')  # markdown, obsidian, json, notion
        content = request.get('content', '')
        metadata = request.get('metadata', {})
        toc = request.get('toc', [])
        sections = request.get('sections', [])
        paragraphs = request.get('paragraphs', [])
        output_path = request.get('output_path')

        if format == 'markdown':
            result = self.export_manager.export_to_markdown(
                content, metadata, toc, sections, output_path
            )
        elif format == 'obsidian':
            vault_path = request.get('vault_path')
            filename = request.get('filename', 'export.md')
            result = self.export_manager.export_to_obsidian(
                content, metadata, toc, vault_path, filename
            )
        elif format == 'json':
            result = self.export_manager.export_to_json(
                content, metadata, toc, sections, paragraphs, output_path
            )
        elif format == 'notion':
            result = self.export_manager.export_to_notion(
                content, metadata, toc
            )
        else:
            return {'status': 'error', 'message': f'Unknown format: {format}'}

        return {
            'status': 'ok',
            'result': result if isinstance(result, dict) else {'content': result}
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def handle_list_documents(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle list documents request"""
    try:
        limit = request.get('limit', 100)
        offset = request.get('offset', 0)

        documents = self.document_manager.list_documents(limit=limit, offset=offset)
        stats = self.document_manager.get_statistics()

        return {
            'status': 'ok',
            'documents': documents,
            'statistics': stats
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def handle_get_tags(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get tags request"""
    try:
        tags = self.document_manager.get_all_tags()

        return {
            'status': 'ok',
            'tags': tags
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
