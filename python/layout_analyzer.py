"""
Layout Analyzer - Detects text regions and layout structure using PaddleOCR
Phase 7: Multi-language support with automatic language detection
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import cv2
import numpy as np
from image_preprocessor import ImagePreprocessor
from language_detector import LanguageDetector


class LayoutAnalyzer:
    """Analyzes document layout using PaddleOCR with multi-language support"""

    def __init__(self, use_preprocessing: bool = True, default_lang: str = 'en'):
        # Lazy import to avoid loading on module import
        self._ocr_instances = {}  # Cache OCR instances per language
        self._current_lang = default_lang
        self.use_preprocessing = use_preprocessing
        self.preprocessor = ImagePreprocessor() if use_preprocessing else None
        self.language_detector = LanguageDetector()

    def get_ocr(self, lang: str = None):
        """
        Get PaddleOCR instance for specified language (lazy load and cache)

        Args:
            lang: Language code (e.g., 'en', 'ja', 'ch'). If None, uses current language.

        Returns:
            PaddleOCR instance
        """
        if lang is None:
            lang = self._current_lang

        # Convert to PaddleOCR language code
        paddle_lang = self.language_detector.get_ocr_lang_code(lang, 'paddleocr')

        # Return cached instance if available
        if paddle_lang in self._ocr_instances:
            return self._ocr_instances[paddle_lang]

        # Create new instance
        from paddleocr import PaddleOCR
        ocr_instance = PaddleOCR(
            use_angle_cls=True,
            lang=paddle_lang,
            use_gpu=False,  # Set to True if GPU available
            show_log=False
        )

        # Cache it
        self._ocr_instances[paddle_lang] = ocr_instance
        return ocr_instance

    @property
    def ocr(self):
        """Backward compatibility: get OCR instance for current language"""
        return self.get_ocr()

    def analyze(self, image_path: str, lang: Optional[str] = None, auto_detect: bool = True) -> Dict[str, Any]:
        """
        Analyze layout and extract text from image with multi-language support

        Args:
            image_path: Path to image file
            lang: Language code (e.g., 'ja', 'en', 'zh-cn'). If None and auto_detect=True, auto-detects.
            auto_detect: Enable automatic language detection

        Returns:
            {
                'layout_type': 'one_column' | 'two_column' | 'complex',
                'detected_language': 'ja',  # Auto-detected or specified language
                'language_confidence': 0.95,
                'mixed_languages': [{'lang': 'ja', 'percentage': 0.7}, ...],  # If mixed
                'chunks': [
                    {
                        'chunk_id': 'c001',
                        'type': 'body' | 'header' | 'footer',
                        'bbox': [x1, y1, x2, y2],
                        'lines': [
                            {'text': '...', 'confidence': 0.95, 'lang': 'ja'},
                            ...
                        ],
                        'order': 1
                    },
                    ...
                ]
            }
        """
        # Load image
        image = cv2.imread(str(image_path))

        # Apply preprocessing if enabled
        if self.use_preprocessing and self.preprocessor:
            image = self.preprocessor.preprocess(
                image,
                denoise=True,
                deskew=True,
                enhance_contrast=True,
                binarize=False  # PaddleOCRは二値化済み画像よりグレースケールの方が良い
            )
            # Convert back to BGR for PaddleOCR
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Determine language to use
        target_lang = lang if lang else self._current_lang

        # Run PaddleOCR with specified language
        ocr_instance = self.get_ocr(target_lang)
        result = ocr_instance.ocr(image, cls=True)

        if not result or not result[0]:
            return {
                'layout_type': 'unknown',
                'detected_language': target_lang,
                'language_confidence': 0.0,
                'mixed_languages': [],
                'chunks': []
            }

        # Extract text and bounding boxes
        lines = []
        full_text = []
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

            text = text_info[0]
            full_text.append(text)

            lines.append({
                'text': text,
                'confidence': float(text_info[1]),
                'bbox': bbox_rect
            })

        # Auto-detect language from extracted text if enabled
        detected_lang = target_lang
        lang_confidence = 1.0
        mixed_languages = []

        if auto_detect and full_text:
            combined_text = ' '.join(full_text)
            detection_result = self.language_detector.detect_from_text(combined_text)
            detected_lang = detection_result['primary']
            lang_confidence = detection_result['confidence']

            # Check for mixed languages
            dominant_langs = self.language_detector.get_dominant_languages(combined_text, top_n=3)
            if len(dominant_langs) > 1 and dominant_langs[1]['percentage'] > 0.15:
                # Significant mixed language content (>15%)
                mixed_languages = dominant_langs

                # Detect language per line for mixed documents
                for line in lines:
                    line_detection = self.language_detector.detect_from_text(line['text'])
                    line['lang'] = line_detection['primary']
                    line['lang_confidence'] = line_detection['confidence']

        # Phase 2: Smart layout detection
        # 1. Detect layout type based on X-coordinates
        layout_type, columns = self._detect_layout_type(lines)

        # 2. Separate header/footer from body
        header_lines, body_lines, footer_lines = self._separate_regions(lines)

        # 3. Create chunks based on detected columns
        chunks = self._create_chunks(header_lines, body_lines, footer_lines, columns, layout_type)

        return {
            'layout_type': layout_type,
            'detected_language': detected_lang,
            'language_confidence': lang_confidence,
            'mixed_languages': mixed_languages,
            'chunks': chunks
        }

    def _detect_layout_type(self, lines: List[Dict]) -> tuple:
        """
        Detect layout type and column boundaries

        Returns:
            (layout_type, column_boundaries)
            layout_type: 'one_column', 'two_column', 'three_column', 'complex'
            column_boundaries: List of (x_start, x_end) for each column
        """
        if not lines:
            return 'unknown', []

        # Get page width
        page_width = max(line['bbox'][2] for line in lines)

        # Cluster lines by X-coordinate centers
        x_centers = [((line['bbox'][0] + line['bbox'][2]) / 2) for line in lines]

        # Use histogram to detect columns
        hist, edges = np.histogram(x_centers, bins=50)

        # Find peaks in histogram (column centers)
        from scipy.signal import find_peaks
        try:
            peaks, _ = find_peaks(hist, height=len(lines) * 0.05, distance=5)
        except ImportError:
            # Fallback if scipy not available
            peaks = self._simple_peak_detection(hist)

        num_columns = len(peaks)

        if num_columns <= 1:
            layout_type = 'one_column'
            columns = [(0, page_width)]
        elif num_columns == 2:
            layout_type = 'two_column'
            columns = self._create_column_boundaries(peaks, edges, page_width)
        elif num_columns == 3:
            layout_type = 'three_column'
            columns = self._create_column_boundaries(peaks, edges, page_width)
        else:
            layout_type = 'complex'
            columns = self._create_column_boundaries(peaks, edges, page_width)

        return layout_type, columns

    def _simple_peak_detection(self, hist: np.ndarray) -> List[int]:
        """Simple peak detection without scipy"""
        peaks = []
        threshold = np.max(hist) * 0.3
        for i in range(1, len(hist) - 1):
            if hist[i] > threshold and hist[i] > hist[i-1] and hist[i] > hist[i+1]:
                peaks.append(i)
        return peaks

    def _create_column_boundaries(self, peaks: List[int], edges: np.ndarray, page_width: float) -> List[tuple]:
        """Create column boundaries from detected peaks"""
        if len(peaks) == 0:
            return [(0, page_width)]

        columns = []
        peak_positions = [edges[p] for p in peaks]
        peak_positions.sort()

        # Create boundaries between peaks
        for i, peak in enumerate(peak_positions):
            if i == 0:
                x_start = 0
            else:
                x_start = (peak_positions[i-1] + peak) / 2

            if i == len(peak_positions) - 1:
                x_end = page_width
            else:
                x_end = (peak + peak_positions[i+1]) / 2

            columns.append((x_start, x_end))

        return columns

    def _separate_regions(self, lines: List[Dict]) -> tuple:
        """Separate header, body, and footer regions"""
        if not lines:
            return [], [], []

        # Sort lines by Y coordinate
        sorted_lines = sorted(lines, key=lambda l: l['bbox'][1])

        # Get page height
        page_height = max(line['bbox'][3] for line in lines)

        # Simple heuristic: top 10% = header, bottom 10% = footer
        header_threshold = page_height * 0.1
        footer_threshold = page_height * 0.9

        header_lines = []
        body_lines = []
        footer_lines = []

        for line in sorted_lines:
            y_center = (line['bbox'][1] + line['bbox'][3]) / 2

            if y_center < header_threshold:
                header_lines.append(line)
            elif y_center > footer_threshold:
                footer_lines.append(line)
            else:
                body_lines.append(line)

        return header_lines, body_lines, footer_lines

    def _create_chunks(self, header_lines: List[Dict], body_lines: List[Dict],
                      footer_lines: List[Dict], columns: List[tuple],
                      layout_type: str) -> List[Dict]:
        """Create chunks from detected regions and columns"""
        chunks = []
        chunk_id = 1

        # Header chunk
        if header_lines:
            chunks.append({
                'chunk_id': f'c{chunk_id:03d}',
                'type': 'header',
                'bbox': self._get_combined_bbox(header_lines),
                'lines': header_lines,
                'order': chunk_id
            })
            chunk_id += 1

        # Body chunks (split by columns)
        if layout_type == 'one_column':
            if body_lines:
                chunks.append({
                    'chunk_id': f'c{chunk_id:03d}',
                    'type': 'body',
                    'bbox': self._get_combined_bbox(body_lines),
                    'lines': body_lines,
                    'order': chunk_id
                })
                chunk_id += 1
        else:
            # Multi-column: assign lines to columns
            column_lines = [[] for _ in columns]

            for line in body_lines:
                x_center = (line['bbox'][0] + line['bbox'][2]) / 2

                # Find which column this line belongs to
                for i, (col_start, col_end) in enumerate(columns):
                    if col_start <= x_center <= col_end:
                        column_lines[i].append(line)
                        break

            # Create chunks for each column
            for i, col_lines in enumerate(column_lines):
                if col_lines:
                    chunks.append({
                        'chunk_id': f'c{chunk_id:03d}',
                        'type': 'body',
                        'bbox': self._get_combined_bbox(col_lines),
                        'lines': sorted(col_lines, key=lambda l: l['bbox'][1]),
                        'order': chunk_id,
                        'column': i + 1
                    })
                    chunk_id += 1

        # Footer chunk
        if footer_lines:
            chunks.append({
                'chunk_id': f'c{chunk_id:03d}',
                'type': 'footer',
                'bbox': self._get_combined_bbox(footer_lines),
                'lines': footer_lines,
                'order': chunk_id
            })

        return chunks

    def _get_combined_bbox(self, lines: List[Dict]) -> List[float]:
        """Get bounding box that encompasses all lines"""
        if not lines:
            return [0, 0, 0, 0]

        x1 = min(line['bbox'][0] for line in lines)
        y1 = min(line['bbox'][1] for line in lines)
        x2 = max(line['bbox'][2] for line in lines)
        y2 = max(line['bbox'][3] for line in lines)

        return [x1, y1, x2, y2]

