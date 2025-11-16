#!/usr/bin/env python3
"""
OCR Server - Stdin/Stdout JSON communication with Electron
Phase 2: PDF support, advanced layout detection, smart text refinement
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import traceback

from layout_analyzer import LayoutAnalyzer
from text_refiner import TextRefiner
from pdf_processor import PDFProcessor


class OCRServer:
    """Main OCR server that handles requests from Electron"""

    def __init__(self):
        self.layout_analyzer = LayoutAnalyzer()
        self.text_refiner = TextRefiner()
        self.pdf_processor = PDFProcessor()

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming request and return result"""
        try:
            command = request.get('command')

            if command == 'ocr':
                return self.handle_ocr(request)
            elif command == 'ocr_pdf':
                return self.handle_ocr_pdf(request)
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
        """Handle OCR request for a single image"""
        image_path = request.get('image_path')

        if not image_path or not Path(image_path).exists():
            return {'status': 'error', 'message': 'Invalid image path'}

        # Phase 2: Advanced OCR with layout detection
        layout_result = self.layout_analyzer.analyze(image_path)

        # Phase 2: Smart text refinement
        text_result = self.text_refiner.refine(layout_result)

        return {
            'status': 'ok',
            'result': {
                'text': text_result['markdown'],
                'chunks': layout_result['chunks'],
                'paragraphs': text_result['paragraphs'],
                'metadata': {
                    'page_count': 1,
                    'layout_type': layout_result.get('layout_type', 'unknown')
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

                results = []
                for page_info in pages:
                    page_result = self.handle_ocr({'image_path': page_info['image_path']})

                    if page_result['status'] == 'ok':
                        results.append({
                            'page_number': page_info['page_number'],
                            'text': page_result['result']['text'],
                            'layout_type': page_result['result']['metadata']['layout_type']
                        })

                # Combine all pages
                combined_text = '\n\n---\n\n'.join([
                    f"# Page {r['page_number']}\n\n{r['text']}"
                    for r in results
                ])

                return {
                    'status': 'ok',
                    'result': {
                        'text': combined_text,
                        'pages': results,
                        'metadata': {
                            'page_count': len(results)
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
