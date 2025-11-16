#!/usr/bin/env python3
"""
OCR Server - Stdin/Stdout JSON communication with Electron
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import traceback

from layout_analyzer import LayoutAnalyzer
from text_refiner import TextRefiner


class OCRServer:
    """Main OCR server that handles requests from Electron"""

    def __init__(self):
        self.layout_analyzer = LayoutAnalyzer()
        self.text_refiner = TextRefiner()

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming request and return result"""
        try:
            command = request.get('command')

            if command == 'ocr':
                return self.handle_ocr(request)
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
        """Handle OCR request"""
        image_path = request.get('image_path')

        if not image_path or not Path(image_path).exists():
            return {'status': 'error', 'message': 'Invalid image path'}

        # Phase 1: Basic OCR with PaddleOCR
        layout_result = self.layout_analyzer.analyze(image_path)

        # Phase 1: Simple text extraction (refinement comes in Phase 2)
        text_result = self.text_refiner.refine(layout_result)

        return {
            'status': 'ok',
            'result': {
                'text': text_result['markdown'],
                'chunks': layout_result['chunks'],
                'metadata': {
                    'page_count': 1,
                    'layout_type': layout_result.get('layout_type', 'unknown')
                }
            }
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
