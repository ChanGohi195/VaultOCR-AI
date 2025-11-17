#!/usr/bin/env python3
"""
OCR Server - Stdin/Stdout JSON communication with Electron
Phase 4: Full-text search, document management, export
Phase 7: Multi-language support
Phase 8: Vector search, semantic search
Phase 9: AI summarization, translation, custom templates, searchable PDF
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import traceback
import numpy as np

from layout_analyzer import LayoutAnalyzer
from text_refiner import TextRefiner
from pdf_processor import PDFProcessor
from document_stitcher import DocumentStitcher
from table_detector import TableDetector
from reading_order import ReadingOrderOptimizer
from search_engine import SearchEngine
from document_manager import DocumentManager
from export_manager import ExportManager
from batch_processor import BatchProcessor
from vector_search import VectorSearchEngine
from summarization_engine import SummarizationEngine
from translation_engine import TranslationEngine
from template_engine import TemplateEngine
from pdf_generator import SearchablePDFGenerator


class OCRServer:
    """Main OCR server that handles requests from Electron"""

    def __init__(self):
        self.layout_analyzer = LayoutAnalyzer()
        self.text_refiner = TextRefiner()
        self.pdf_processor = PDFProcessor()
        self.document_stitcher = DocumentStitcher()
        self.table_detector = TableDetector()
        self.reading_order_optimizer = ReadingOrderOptimizer()

        # Phase 4: Search and management
        self.search_engine = SearchEngine()
        self.document_manager = DocumentManager()
        self.export_manager = ExportManager()

        # Phase 5: Batch processing
        self.batch_processor = BatchProcessor(
            ocr_handler=self._ocr_single_file,
            document_manager=self.document_manager,
            search_engine=self.search_engine
        )

        # Phase 8: Vector search
        self.vector_search = VectorSearchEngine()

        # Phase 9: AI features and PDF generation
        self.summarization_engine = SummarizationEngine()
        self.translation_engine = TranslationEngine()
        self.template_engine = TemplateEngine()
        self.pdf_generator = SearchablePDFGenerator()

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming request and return result"""
        try:
            command = request.get('command')

            if command == 'ocr':
                return self.handle_ocr(request)
            elif command == 'ocr_pdf':
                return self.handle_ocr_pdf(request)
            elif command == 'search':
                return self.handle_search(request)
            elif command == 'save_document':
                return self.handle_save_document(request)
            elif command == 'export':
                return self.handle_export(request)
            elif command == 'list_documents':
                return self.handle_list_documents(request)
            elif command == 'get_tags':
                return self.handle_get_tags(request)
            elif command == 'get_document':
                return self.handle_get_document(request)
            elif command == 'batch_ocr':
                return self.handle_batch_ocr(request)
            elif command == 'get_supported_languages':
                return self.handle_get_supported_languages(request)
            elif command == 'semantic_search':
                return self.handle_semantic_search(request)
            elif command == 'hybrid_search':
                return self.handle_hybrid_search(request)
            elif command == 'find_similar':
                return self.handle_find_similar(request)
            elif command == 'index_document_vector':
                return self.handle_index_document_vector(request)
            # Phase 9: AI features
            elif command == 'summarize':
                return self.handle_summarize(request)
            elif command == 'translate':
                return self.handle_translate(request)
            elif command == 'extract_template':
                return self.handle_extract_template(request)
            elif command == 'generate_searchable_pdf':
                return self.handle_generate_searchable_pdf(request)
            elif command == 'get_templates':
                return self.handle_get_templates(request)
            elif command == 'get_translation_pairs':
                return self.handle_get_translation_pairs(request)
            elif command == 'ping':
                return {'status': 'ok', 'message': 'pong'}
            else:
                return {'status': 'error', 'message': f'Unknown command: {command}'}

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()
            }

    def handle_ocr(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OCR request for a single image with multi-language support"""
        image_path = request.get('image_path')
        lang = request.get('lang')  # Phase 7: Language parameter
        auto_detect = request.get('auto_detect', True)  # Phase 7: Auto-detect language

        if not image_path or not Path(image_path).exists():
            return {'status': 'error', 'message': 'Invalid image path'}

        # Phase 7: Multi-language OCR with layout detection
        layout_result = self.layout_analyzer.analyze(
            image_path,
            lang=lang,
            auto_detect=auto_detect
        )

        # Phase 3: Optimize reading order
        layout_result['chunks'] = self.reading_order_optimizer.optimize_reading_order(
            layout_result['chunks'],
            layout_result.get('layout_type', 'one_column')
        )

        # Phase 3: Detect tables
        tables = self.table_detector.detect_tables(image_path, layout_result['chunks'])
        layout_result['tables'] = tables

        # Phase 2: Smart text refinement
        text_result = self.text_refiner.refine(layout_result)

        # Calculate confidence metrics
        confidence_metrics = self._calculate_confidence_metrics(layout_result['chunks'])

        return {
            'status': 'ok',
            'result': {
                'text': text_result['markdown'],
                'chunks': layout_result['chunks'],
                'paragraphs': text_result['paragraphs'],
                'tables': tables,
                'metadata': {
                    'page_count': 1,
                    'layout_type': layout_result.get('layout_type', 'unknown'),
                    'detected_language': layout_result.get('detected_language', 'en'),
                    'language_confidence': layout_result.get('language_confidence', 0.0),
                    'mixed_languages': layout_result.get('mixed_languages', []),
                    'table_count': len(tables),
                    'confidence': confidence_metrics
                }
            }
        }

    def handle_ocr_pdf(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OCR request for PDF file"""
        pdf_path = request.get('pdf_path')
        page_number = request.get('page_number')  # Optional: specific page

        if not pdf_path or not Path(pdf_path).exists():
            return {'status': 'error', 'message': 'Invalid PDF path'}

        try:
            # Convert PDF to image(s)
            if page_number:
                # Single page
                image_path = self.pdf_processor.process_single_page(pdf_path, page_number)
                return self.handle_ocr({'image_path': image_path})
            else:
                # All pages
                pages = self.pdf_processor.process_pdf(pdf_path)

                # Process each page
                page_results = []
                for page_info in pages:
                    page_result = self.handle_ocr({'image_path': page_info['image_path']})

                    if page_result['status'] == 'ok':
                        page_results.append({
                            'page_number': page_info['page_number'],
                            'text': page_result['result']['text'],
                            'paragraphs': page_result['result']['paragraphs'],
                            'chunks': page_result['result']['chunks'],
                            'layout_type': page_result['result']['metadata']['layout_type'],
                            'tables': page_result['result'].get('tables', [])
                        })

                # Phase 3: Stitch pages together
                stitched = self.document_stitcher.stitch_pages(page_results)

                return {
                    'status': 'ok',
                    'result': {
                        'text': stitched['markdown'],
                        'pages': page_results,
                        'paragraphs': stitched['paragraphs'],
                        'sections': stitched['sections'],
                        'toc': stitched['toc'],
                        'metadata': {
                            'page_count': len(page_results),
                            'section_count': len(stitched['sections']),
                            'total_tables': sum(len(p.get('tables', [])) for p in page_results)
                        }
                    }
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'PDF processing failed: {str(e)}',
                'traceback': traceback.format_exc()
            }

    def run(self):
        """Main event loop - read from stdin, write to stdout"""
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self.process_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                error_response = {
                    'status': 'error',
                    'message': f'Invalid JSON: {str(e)}'
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    'status': 'error',
                    'message': str(e),
                    'traceback': traceback.format_exc()
                }
                print(json.dumps(error_response), flush=True)


if __name__ == '__main__':
    server = OCRServer()
    server.run()

    # Phase 4 handlers
    def handle_search(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search request"""
        query = request.get('query', '').strip()
        limit = request.get('limit', 20)

        if not query:
            return {'status': 'error', 'message': 'Query is required'}

        try:
            results = self.search_engine.search(query, limit=limit)
            return {'status': 'ok', 'results': results}
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

            doc_id = self.document_manager.add_document(
                title=title, file_path=file_path, content=content,
                metadata=metadata, tags=tags
            )

            # Add to keyword search index
            self.search_engine.add_document(
                doc_id=doc_id, title=title, content=content,
                path=file_path, tags=tags, metadata=metadata
            )

            # Phase 8: Add to vector search index
            self.vector_search.add_document(
                doc_id=doc_id, title=title, content=content,
                metadata={'path': file_path, 'tags': tags, **metadata}
            )
            self.vector_search.save_index()

            return {'status': 'ok', 'doc_id': doc_id}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def handle_export(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle export request"""
        try:
            format = request.get('format', 'markdown')
            content = request.get('content', '')
            metadata = request.get('metadata', {})
            toc = request.get('toc', [])
            sections = request.get('sections', [])
            output_path = request.get('output_path')

            if format == 'markdown':
                result = self.export_manager.export_to_markdown(
                    content, metadata, toc, sections, output_path
                )
            elif format == 'obsidian':
                result = self.export_manager.export_to_obsidian(
                    content, metadata, toc,
                    request.get('vault_path'), request.get('filename', 'export.md')
                )
            elif format == 'json':
                result = self.export_manager.export_to_json(
                    content, metadata, toc, sections,
                    request.get('paragraphs', []), output_path
                )
            else:
                return {'status': 'error', 'message': f'Unknown format: {format}'}

            return {'status': 'ok', 'result': result if isinstance(result, dict) else {'content': result}}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def handle_list_documents(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list documents request"""
        try:
            documents = self.document_manager.list_documents(
                limit=request.get('limit', 100), offset=request.get('offset', 0)
            )
            return {'status': 'ok', 'documents': documents,
                    'statistics': self.document_manager.get_statistics()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def handle_get_tags(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get tags request"""
        try:
            return {'status': 'ok', 'tags': self.document_manager.get_all_tags()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def handle_get_document(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get document request"""
        try:
            doc_id = request.get('doc_id')
            if not doc_id:
                return {'status': 'error', 'message': 'doc_id is required'}

            document = self.document_manager.get_document(doc_id)
            if not document:
                return {'status': 'error', 'message': f'Document {doc_id} not found'}

            return {'status': 'ok', 'document': document}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def handle_batch_ocr(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch OCR request"""
        try:
            file_paths = request.get('file_paths', [])
            auto_save = request.get('auto_save', True)
            tags = request.get('tags', [])

            if not file_paths:
                return {'status': 'error', 'message': 'file_paths is required'}

            # バッチ処理実行
            results = self.batch_processor.process_batch(
                file_paths=file_paths,
                auto_save=auto_save,
                tags=tags
            )

            return {
                'status': 'ok',
                'result': results
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _ocr_single_file(self, file_path: str) -> Dict[str, Any]:
        """
        単一ファイルのOCR処理（バッチ処理用内部メソッド）

        Args:
            file_path: 処理するファイルパス

        Returns:
            OCR結果
        """
        # PDFまたは画像を判定
        if file_path.lower().endswith('.pdf'):
            # PDF処理
            request = {'pdf_path': file_path}
            response = self.handle_ocr_pdf(request)
        else:
            # 画像処理
            request = {'image_path': file_path}
            response = self.handle_ocr(request)

        if response.get('status') == 'ok':
            return response.get('result', {})
        else:
            raise Exception(response.get('message', 'OCR failed'))

    def _calculate_confidence_metrics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        信頼度メトリクスを計算

        Args:
            chunks: レイアウトチャンク

        Returns:
            信頼度メトリクス
        """
        all_confidences = []
        low_confidence_count = 0
        total_lines = 0

        for chunk in chunks:
            for line in chunk.get('lines', []):
                confidence = line.get('confidence', 0)
                all_confidences.append(confidence)
                total_lines += 1
                if confidence < 0.8:  # 信頼度80%未満を低信頼度とする
                    low_confidence_count += 1

        if not all_confidences:
            return {
                'average': 0.0,
                'min': 0.0,
                'max': 0.0,
                'low_confidence_ratio': 0.0
            }

        return {
            'average': float(np.mean(all_confidences)),
            'min': float(np.min(all_confidences)),
            'max': float(np.max(all_confidences)),
            'low_confidence_ratio': float(low_confidence_count / total_lines) if total_lines > 0 else 0.0,
            'total_lines': total_lines,
            'low_confidence_lines': low_confidence_count
        }

    def handle_get_supported_languages(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get list of supported languages for OCR

        Returns:
            {
                'status': 'ok',
                'languages': [
                    {'code': 'ja', 'name': '日本語 (Japanese)', 'paddleocr': 'japan', 'tesseract': 'jpn'},
                    ...
                ]
            }
        """
        try:
            languages = self.layout_analyzer.language_detector.get_supported_languages()

            return {
                'status': 'ok',
                'languages': languages
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # Phase 8: Vector Search Handlers

    def handle_semantic_search(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle semantic search request (vector-based)

        Args:
            request: {
                'query': str,
                'top_k': int (optional, default 10),
                'threshold': float (optional, default 0.0)
            }

        Returns:
            {
                'status': 'ok',
                'results': [
                    {'doc_id': str, 'title': str, 'content': str, 'score': float, 'metadata': dict},
                    ...
                ]
            }
        """
        try:
            query = request.get('query', '').strip()
            top_k = request.get('top_k', 10)
            threshold = request.get('threshold', 0.0)

            if not query:
                return {'status': 'error', 'message': 'Query is required'}

            results = self.vector_search.search(query, top_k=top_k, threshold=threshold)

            return {
                'status': 'ok',
                'results': results
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def handle_hybrid_search(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle hybrid search (keyword + vector)

        Combines keyword-based and semantic search results

        Args:
            request: {
                'query': str,
                'top_k': int (optional, default 10),
                'keyword_weight': float (optional, default 0.5),
                'semantic_weight': float (optional, default 0.5)
            }

        Returns:
            {
                'status': 'ok',
                'results': [merged and ranked results]
            }
        """
        try:
            query = request.get('query', '').strip()
            top_k = request.get('top_k', 10)
            keyword_weight = request.get('keyword_weight', 0.5)
            semantic_weight = request.get('semantic_weight', 0.5)

            if not query:
                return {'status': 'error', 'message': 'Query is required'}

            # Get keyword search results
            keyword_results = self.search_engine.search(query, limit=top_k * 2)

            # Get semantic search results
            semantic_results = self.vector_search.search(query, top_k=top_k * 2)

            # Merge and rank results
            merged = self._merge_search_results(
                keyword_results, semantic_results,
                keyword_weight, semantic_weight,
                top_k
            )

            return {
                'status': 'ok',
                'results': merged
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def handle_find_similar(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find similar documents to a given document

        Args:
            request: {
                'doc_id': str,
                'top_k': int (optional, default 5)
            }

        Returns:
            {
                'status': 'ok',
                'results': [similar documents with scores]
            }
        """
        try:
            doc_id = request.get('doc_id')
            top_k = request.get('top_k', 5)

            if not doc_id:
                return {'status': 'error', 'message': 'doc_id is required'}

            results = self.vector_search.find_similar(doc_id, top_k=top_k)

            return {
                'status': 'ok',
                'results': results
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def handle_index_document_vector(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manually index a document in vector search

        Args:
            request: {
                'doc_id': str,
                'title': str,
                'content': str,
                'metadata': dict (optional)
            }

        Returns:
            {'status': 'ok'}
        """
        try:
            doc_id = request.get('doc_id')
            title = request.get('title', '')
            content = request.get('content', '')
            metadata = request.get('metadata', {})

            if not doc_id:
                return {'status': 'error', 'message': 'doc_id is required'}

            self.vector_search.add_document(
                doc_id=doc_id,
                title=title,
                content=content,
                metadata=metadata
            )
            self.vector_search.save_index()

            return {'status': 'ok'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _merge_search_results(self, keyword_results: List[Dict], semantic_results: List[Dict],
                              keyword_weight: float, semantic_weight: float,
                              top_k: int) -> List[Dict]:
        """
        Merge keyword and semantic search results using weighted scoring

        Args:
            keyword_results: Results from keyword search
            semantic_results: Results from semantic search
            keyword_weight: Weight for keyword scores
            semantic_weight: Weight for semantic scores
            top_k: Number of results to return

        Returns:
            Merged and ranked results
        """
        # Normalize scores and combine
        doc_scores = {}

        # Process keyword results
        for result in keyword_results:
            doc_id = result.get('doc_id')
            score = result.get('score', 0.0)
            doc_scores[doc_id] = {
                'keyword_score': score * keyword_weight,
                'semantic_score': 0.0,
                'data': result
            }

        # Process semantic results
        for result in semantic_results:
            doc_id = result.get('doc_id')
            score = result.get('score', 0.0)

            if doc_id in doc_scores:
                doc_scores[doc_id]['semantic_score'] = score * semantic_weight
            else:
                doc_scores[doc_id] = {
                    'keyword_score': 0.0,
                    'semantic_score': score * semantic_weight,
                    'data': result
                }

        # Calculate combined scores and sort
        merged_results = []
        for doc_id, scores in doc_scores.items():
            combined_score = scores['keyword_score'] + scores['semantic_score']
            result = scores['data'].copy()
            result['score'] = combined_score
            result['keyword_score'] = scores['keyword_score']
            result['semantic_score'] = scores['semantic_score']
            merged_results.append(result)

        # Sort by combined score and return top_k
        merged_results.sort(key=lambda x: x['score'], reverse=True)
        return merged_results[:top_k]

    # Phase 9: AI feature handlers
    def handle_summarize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text summarization request"""
        try:
            text = request.get('text', '')
            max_length = request.get('max_length', 150)
            min_length = request.get('min_length', 40)
            language = request.get('language', 'en')
            ratio = request.get('ratio')

            if not text:
                return {'status': 'error', 'message': 'Text is required'}

            result = self.summarization_engine.summarize(
                text=text,
                max_length=max_length,
                min_length=min_length,
                language=language,
                ratio=ratio
            )

            return {'status': 'ok', 'result': result}

        except Exception as e:
            return {'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}

    def handle_translate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle translation request"""
        try:
            text = request.get('text', '')
            source_lang = request.get('source_lang', 'en')
            target_lang = request.get('target_lang', 'ja')
            max_length = request.get('max_length', 512)

            if not text:
                return {'status': 'error', 'message': 'Text is required'}

            result = self.translation_engine.translate(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                max_length=max_length
            )

            return {'status': 'ok', 'result': result}

        except Exception as e:
            return {'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}

    def handle_extract_template(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle template extraction request"""
        try:
            text = request.get('text', '')
            template_name = request.get('template')  # Optional: auto-detect if None

            if not text:
                return {'status': 'error', 'message': 'Text is required'}

            result = self.template_engine.extract(text, template_name)

            return {'status': 'ok', 'result': result}

        except Exception as e:
            return {'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}

    def handle_generate_searchable_pdf(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle searchable PDF generation request"""
        try:
            mode = request.get('mode', 'text')  # 'text' or 'images'

            if mode == 'text':
                text = request.get('text', '')
                output_path = request.get('output_path')
                metadata = request.get('metadata', {})
                font_size = request.get('font_size', 12)
                line_spacing = request.get('line_spacing', 14)

                if not text or not output_path:
                    return {'status': 'error', 'message': 'Text and output_path are required'}

                result = self.pdf_generator.create_from_text(
                    text=text,
                    output_path=output_path,
                    metadata=metadata,
                    font_size=font_size,
                    line_spacing=line_spacing
                )

            elif mode == 'images':
                images = request.get('images', [])
                ocr_results = request.get('ocr_results', [])
                output_path = request.get('output_path')
                metadata = request.get('metadata', {})

                if not images or not output_path:
                    return {'status': 'error', 'message': 'Images and output_path are required'}

                result = self.pdf_generator.create_from_images(
                    images=images,
                    ocr_results=ocr_results,
                    output_path=output_path,
                    metadata=metadata
                )
            else:
                return {'status': 'error', 'message': f'Invalid mode: {mode}'}

            return {'status': 'ok', 'result': result}

        except Exception as e:
            return {'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}

    def handle_get_templates(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of available document templates"""
        try:
            templates = self.template_engine.list_templates()
            return {'status': 'ok', 'templates': templates}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def handle_get_translation_pairs(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of supported translation language pairs"""
        try:
            pairs = self.translation_engine.get_supported_pairs()
            # Convert tuples to dicts for JSON serialization
            pairs_list = [{'source': pair[0], 'target': pair[1]} for pair in pairs]
            return {'status': 'ok', 'pairs': pairs_list}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}
