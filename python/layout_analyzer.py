"""
Layout Analyzer - Detects text regions and layout structure using PaddleOCR
"""
from typing import Dict, Any, List
from pathlib import Path
import cv2
import numpy as np


class LayoutAnalyzer:
    """Analyzes document layout using PaddleOCR"""

    def __init__(self):
        # Lazy import to avoid loading on module import
        self._ocr = None

    @property
    def ocr(self):
        """Lazy load PaddleOCR"""
        if self._ocr is None:
            from paddleocr import PaddleOCR
            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en',  # Phase 2: Add multi-language support
                use_gpu=False,  # Set to True if GPU available
                show_log=False
            )
        return self._ocr

    def analyze(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze layout and extract text from image

        Returns:
            {
                'layout_type': 'one_column' | 'two_column' | 'complex',
                'chunks': [
                    {
                        'chunk_id': 'c001',
                        'type': 'body' | 'header' | 'footer',
                        'bbox': [x1, y1, x2, y2],
                        'lines': [
                            {'text': '...', 'confidence': 0.95},
                            ...
                        ],
                        'order': 1
                    },
                    ...
                ]
            }
        """
        # Run PaddleOCR
        result = self.ocr.ocr(image_path, cls=True)

        if not result or not result[0]:
            return {
                'layout_type': 'unknown',
                'chunks': []
            }

        # Extract text and bounding boxes
        lines = []
        for line in result[0]:
            bbox = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text_info = line[1]  # (text, confidence)

            # Convert bbox to [x1, y1, x2, y2] format
            x_coords = [p[0] for p in bbox]
            y_coords = [p[1] for p in bbox]
            bbox_rect = [
                min(x_coords),
                min(y_coords),
                max(x_coords),
                max(y_coords)
            ]

            lines.append({
                'text': text_info[0],
                'confidence': float(text_info[1]),
                'bbox': bbox_rect
            })

        # Phase 1: Simple chunking (group all lines into one body chunk)
        # Phase 2: Implement proper layout detection
        chunks = self._simple_chunking(lines)

        # Detect layout type (Phase 1: simple heuristic)
        layout_type = self._detect_layout_type(chunks)

        return {
            'layout_type': layout_type,
            'chunks': chunks
        }

    def _simple_chunking(self, lines: List[Dict]) -> List[Dict]:
        """Phase 1: Simple chunking - group all lines into one chunk"""
        if not lines:
            return []

        return [{
            'chunk_id': 'c001',
            'type': 'body',
            'bbox': self._get_combined_bbox(lines),
            'lines': lines,
            'order': 1
        }]

    def _get_combined_bbox(self, lines: List[Dict]) -> List[float]:
        """Get bounding box that encompasses all lines"""
        if not lines:
            return [0, 0, 0, 0]

        x1 = min(line['bbox'][0] for line in lines)
        y1 = min(line['bbox'][1] for line in lines)
        x2 = max(line['bbox'][2] for line in lines)
        y2 = max(line['bbox'][3] for line in lines)

        return [x1, y1, x2, y2]

    def _detect_layout_type(self, chunks: List[Dict]) -> str:
        """Phase 1: Always return 'one_column'"""
        # Phase 2: Implement proper layout detection
        return 'one_column'
