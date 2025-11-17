"""
Phase 9: Searchable PDF Generator
Creates searchable PDF files from OCR results with text overlay
"""

from typing import Dict, Any, Optional, List
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)


class SearchablePDFGenerator:
    """Generate searchable PDF from images and OCR text"""

    def __init__(self, page_size='A4'):
        """
        Initialize PDF generator

        Args:
            page_size: Default page size ('A4' or 'letter')
        """
        self.page_size = A4 if page_size == 'A4' else letter

        # Try to register Unicode fonts for multi-language support
        try:
            # These fonts support Japanese/Chinese/Korean characters
            # In production, you'd bundle these fonts with the app
            pass
        except Exception as e:
            logger.warning(f"Could not load custom fonts: {e}")

        logger.info(f"SearchablePDFGenerator initialized (page_size: {page_size})")

    def create_from_images(
        self,
        images: List[str],
        ocr_results: List[Dict[str, Any]],
        output_path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create searchable PDF from images and OCR results

        Args:
            images: List of image file paths
            ocr_results: List of OCR results (one per image)
            output_path: Output PDF file path
            metadata: PDF metadata (title, author, subject, keywords)

        Returns:
            {
                'success': bool,
                'output_path': str,
                'page_count': int,
                'file_size': int
            }
        """
        try:
            c = canvas.Canvas(output_path, pagesize=self.page_size)

            # Set metadata
            if metadata:
                if 'title' in metadata:
                    c.setTitle(metadata['title'])
                if 'author' in metadata:
                    c.setAuthor(metadata['author'])
                if 'subject' in metadata:
                    c.setSubject(metadata['subject'])
                if 'keywords' in metadata:
                    c.setKeywords(metadata['keywords'])

            page_count = 0

            # Process each page
            for idx, (image_path, ocr_result) in enumerate(zip(images, ocr_results)):
                try:
                    self._add_page(c, image_path, ocr_result)
                    page_count += 1

                    # Start new page if not last
                    if idx < len(images) - 1:
                        c.showPage()

                except Exception as e:
                    logger.error(f"Failed to process page {idx + 1}: {e}")
                    continue

            # Save PDF
            c.save()

            # Get file size
            import os
            file_size = os.path.getsize(output_path)

            logger.info(f"Searchable PDF created: {output_path} ({page_count} pages, {file_size} bytes)")

            return {
                'success': True,
                'output_path': output_path,
                'page_count': page_count,
                'file_size': file_size
            }

        except Exception as e:
            logger.error(f"Failed to create searchable PDF: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _add_page(
        self,
        c: canvas.Canvas,
        image_path: str,
        ocr_result: Dict[str, Any]
    ):
        """Add a single page with image and text overlay"""
        # Load image
        img = Image.open(image_path)
        img_width, img_height = img.size

        # Calculate scaling to fit page
        page_width, page_height = self.page_size
        scale = min(page_width / img_width, page_height / img_height)

        # Draw image
        c.drawInlineImage(
            image_path,
            0, 0,
            width=img_width * scale,
            height=img_height * scale
        )

        # Add invisible text layer for searchability
        if 'text' in ocr_result:
            self._add_text_overlay(c, ocr_result, img_width, img_height, scale)

    def _add_text_overlay(
        self,
        c: canvas.Canvas,
        ocr_result: Dict[str, Any],
        img_width: int,
        img_height: int,
        scale: float
    ):
        """
        Add invisible text overlay at correct positions

        This makes the PDF searchable while keeping original image visible
        """
        # Set text rendering mode to invisible (mode 3)
        c.setFillColorRGB(0, 0, 0, alpha=0)  # Transparent black

        # Extract word-level bounding boxes if available
        if 'words' in ocr_result:
            # Detailed word positioning
            for word_info in ocr_result['words']:
                text = word_info.get('text', '')
                bbox = word_info.get('bbox')  # [x1, y1, x2, y2]

                if not text or not bbox:
                    continue

                # Convert coordinates (OCR coords are top-left origin, PDF is bottom-left)
                x1, y1, x2, y2 = bbox
                x = x1 * scale
                y = (img_height - y2) * scale  # Flip Y axis
                width = (x2 - x1) * scale
                height = (y2 - y1) * scale

                # Estimate font size from bbox height
                font_size = height * 0.8

                try:
                    c.setFont("Helvetica", font_size)
                    c.drawString(x, y, text)
                except Exception as e:
                    logger.debug(f"Could not draw word '{text}': {e}")

        else:
            # Fallback: just add text at bottom of page (still searchable)
            text = ocr_result.get('text', '')
            if text:
                # Split into lines and add with small spacing
                c.setFont("Helvetica", 8)
                lines = text.split('\n')

                y_position = 10
                for line in lines[:50]:  # Limit to 50 lines
                    if line.strip():
                        try:
                            c.drawString(10, y_position, line[:200])  # Limit line length
                            y_position += 10
                        except Exception as e:
                            logger.debug(f"Could not draw line: {e}")

    def create_from_text(
        self,
        text: str,
        output_path: str,
        metadata: Optional[Dict[str, str]] = None,
        font_size: int = 12,
        line_spacing: int = 14
    ) -> Dict[str, Any]:
        """
        Create PDF from plain text (for export functionality)

        Args:
            text: Text content
            output_path: Output PDF file path
            metadata: PDF metadata
            font_size: Font size for text
            line_spacing: Line spacing in points

        Returns:
            Result dictionary
        """
        try:
            c = canvas.Canvas(output_path, pagesize=self.page_size)

            # Set metadata
            if metadata:
                if 'title' in metadata:
                    c.setTitle(metadata['title'])
                if 'author' in metadata:
                    c.setAuthor(metadata['author'])

            page_width, page_height = self.page_size
            margin = 0.75 * inch
            usable_width = page_width - 2 * margin
            usable_height = page_height - 2 * margin

            c.setFont("Helvetica", font_size)

            # Split text into lines
            lines = []
            for paragraph in text.split('\n'):
                if not paragraph.strip():
                    lines.append('')
                else:
                    # Word wrap
                    words = paragraph.split()
                    current_line = ''

                    for word in words:
                        test_line = current_line + ' ' + word if current_line else word
                        text_width = c.stringWidth(test_line, "Helvetica", font_size)

                        if text_width <= usable_width:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = word

                    if current_line:
                        lines.append(current_line)

            # Draw lines across pages
            y_position = page_height - margin
            page_count = 1

            for line in lines:
                if y_position < margin:
                    # Start new page
                    c.showPage()
                    c.setFont("Helvetica", font_size)
                    y_position = page_height - margin
                    page_count += 1

                c.drawString(margin, y_position, line)
                y_position -= line_spacing

            c.save()

            import os
            file_size = os.path.getsize(output_path)

            logger.info(f"Text PDF created: {output_path} ({page_count} pages)")

            return {
                'success': True,
                'output_path': output_path,
                'page_count': page_count,
                'file_size': file_size
            }

        except Exception as e:
            logger.error(f"Failed to create text PDF: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def merge_pdfs(
        self,
        pdf_paths: List[str],
        output_path: str
    ) -> Dict[str, Any]:
        """
        Merge multiple PDFs into one

        Args:
            pdf_paths: List of PDF file paths to merge
            output_path: Output merged PDF path

        Returns:
            Result dictionary
        """
        try:
            from PyPDF2 import PdfMerger

            merger = PdfMerger()

            for pdf_path in pdf_paths:
                merger.append(pdf_path)

            merger.write(output_path)
            merger.close()

            import os
            file_size = os.path.getsize(output_path)

            logger.info(f"PDFs merged: {output_path} ({len(pdf_paths)} files)")

            return {
                'success': True,
                'output_path': output_path,
                'input_count': len(pdf_paths),
                'file_size': file_size
            }

        except Exception as e:
            logger.error(f"Failed to merge PDFs: {e}")
            return {
                'success': False,
                'error': str(e)
            }
