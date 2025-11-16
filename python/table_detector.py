"""
Table Detector - Detects and extracts tables from images using OpenCV
Completely free, no API calls
"""
from typing import Dict, Any, List, Tuple
import cv2
import numpy as np
from pathlib import Path


class TableDetector:
    """Detects tables in document images using OpenCV"""

    def __init__(self, min_table_area: int = 10000):
        """
        Initialize table detector

        Args:
            min_table_area: Minimum area (pixels²) for a valid table
        """
        self.min_table_area = min_table_area

    def detect_tables(self, image_path: str, chunks: List[Dict]) -> List[Dict]:
        """
        Detect tables in image

        Args:
            image_path: Path to image file
            chunks: Existing text chunks from OCR

        Returns:
            List of table regions with structure:
            [{
                'bbox': [x1, y1, x2, y2],
                'type': 'table',
                'rows': int,
                'cols': int,
                'cells': [[cell_text, ...], ...]
            }, ...]
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return []

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect table regions
        table_regions = self._detect_table_regions(gray)

        # Extract table structure for each region
        tables = []
        for region in table_regions:
            table_data = self._extract_table_structure(
                gray, region, chunks
            )
            if table_data:
                tables.append(table_data)

        return tables

    def _detect_table_regions(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect potential table regions using line detection

        Returns:
            List of (x, y, w, h) bounding boxes
        """
        # Threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Detect horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)

        # Detect vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)

        # Combine lines
        table_mask = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0)

        # Find contours
        contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by area
        table_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= self.min_table_area:
                x, y, w, h = cv2.boundingRect(contour)
                table_regions.append((x, y, w, h))

        return table_regions

    def _extract_table_structure(
        self,
        gray: np.ndarray,
        region: Tuple[int, int, int, int],
        chunks: List[Dict]
    ) -> Dict[str, Any] | None:
        """
        Extract table structure (rows, columns) from a region

        Args:
            gray: Grayscale image
            region: (x, y, w, h) of table region
            chunks: Text chunks from OCR

        Returns:
            Table data dict or None
        """
        x, y, w, h = region

        # Extract table region
        table_img = gray[y:y+h, x:x+w]

        # Detect grid lines
        rows = self._detect_grid_lines(table_img, horizontal=True)
        cols = self._detect_grid_lines(table_img, horizontal=False)

        if len(rows) < 2 or len(cols) < 2:
            # Not enough grid lines for a table
            return None

        # Find text in each cell
        cells = self._extract_cell_text(x, y, rows, cols, chunks)

        return {
            'bbox': [x, y, x + w, y + h],
            'type': 'table',
            'rows': len(rows) - 1,
            'cols': len(cols) - 1,
            'cells': cells,
            'markdown': self._cells_to_markdown(cells)
        }

    def _detect_grid_lines(self, image: np.ndarray, horizontal: bool = True) -> List[int]:
        """
        Detect horizontal or vertical grid lines

        Returns:
            List of line positions (y-coords for horizontal, x-coords for vertical)
        """
        # Use Hough Line Transform
        edges = cv2.Canny(image, 50, 150)

        if horizontal:
            # Detect horizontal lines
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        else:
            # Detect vertical lines
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

        lines_img = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # Project to axis
        if horizontal:
            projection = np.sum(lines_img, axis=1)
        else:
            projection = np.sum(lines_img, axis=0)

        # Find peaks (line positions)
        threshold = np.max(projection) * 0.3
        positions = []

        for i, val in enumerate(projection):
            if val > threshold:
                # Check if this is a new peak
                if not positions or i - positions[-1] > 10:
                    positions.append(i)

        return sorted(positions)

    def _extract_cell_text(
        self,
        table_x: int,
        table_y: int,
        rows: List[int],
        cols: List[int],
        chunks: List[Dict]
    ) -> List[List[str]]:
        """
        Extract text from each cell using OCR chunks

        Returns:
            2D list of cell texts: [[cell00, cell01, ...], [cell10, ...], ...]
        """
        cells = []

        for i in range(len(rows) - 1):
            row = []
            y1 = table_y + rows[i]
            y2 = table_y + rows[i + 1]

            for j in range(len(cols) - 1):
                x1 = table_x + cols[j]
                x2 = table_x + cols[j + 1]

                # Find text chunks that fall in this cell
                cell_text = self._find_text_in_bbox(x1, y1, x2, y2, chunks)
                row.append(cell_text)

            cells.append(row)

        return cells

    def _find_text_in_bbox(
        self,
        x1: int, y1: int, x2: int, y2: int,
        chunks: List[Dict]
    ) -> str:
        """Find text from chunks that falls within bounding box"""
        texts = []

        for chunk in chunks:
            for line in chunk.get('lines', []):
                bbox = line.get('bbox', [])
                if len(bbox) != 4:
                    continue

                # Check if line center is within cell
                line_x = (bbox[0] + bbox[2]) / 2
                line_y = (bbox[1] + bbox[3]) / 2

                if x1 <= line_x <= x2 and y1 <= line_y <= y2:
                    texts.append(line['text'])

        return ' '.join(texts).strip()

    def _cells_to_markdown(self, cells: List[List[str]]) -> str:
        """Convert cell matrix to Markdown table"""
        if not cells:
            return ""

        lines = []

        # Header row (first row)
        if cells:
            header = '| ' + ' | '.join(cells[0]) + ' |'
            separator = '|' + '|'.join(['---'] * len(cells[0])) + '|'
            lines.append(header)
            lines.append(separator)

        # Data rows
        for row in cells[1:]:
            line = '| ' + ' | '.join(row) + ' |'
            lines.append(line)

        return '\n'.join(lines)
