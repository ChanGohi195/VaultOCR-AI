#!/usr/bin/env python3
"""
OCR Server - Stdin/Stdout JSON communication with Electron
Phase 4: Full-text search, document management, export
Phase 7: Multi-language support
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

            self.search_engine.add_document(
                doc_id=doc_id, title=title, content=content,
                path=file_path, tags=tags, metadata=metadata
            )

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
