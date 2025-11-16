"""
PDF Processor - Converts PDF to images for OCR processing
"""
from typing import List, Dict, Any
from pathlib import Path
import tempfile
from pdf2image import convert_from_path
from PIL import Image


class PDFProcessor:
    """Handles PDF to image conversion"""

    def __init__(self, dpi: int = 300):
        """
        Initialize PDF processor

        Args:
            dpi: Resolution for image conversion (default 300 for good OCR quality)
        """
        self.dpi = dpi

    def process_pdf(self, pdf_path: str, output_dir: str = None) -> List[Dict[str, Any]]:
        """
        Convert PDF to images

        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save images (uses temp dir if None)

        Returns:
            List of dicts with page info:
            [
                {
                    'page_number': 1,
                    'image_path': '/tmp/page_001.png',
                    'width': 2480,
                    'height': 3508
                },
                ...
            ]
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Use temporary directory if not specified
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix='vaultocr_')
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        # Convert PDF to images
        try:
            images = convert_from_path(
                str(pdf_path),
                dpi=self.dpi,
                fmt='png'
            )
        except Exception as e:
            raise RuntimeError(f"Failed to convert PDF: {e}")

        # Save images and collect metadata
        page_infos = []

        for page_num, image in enumerate(images, start=1):
            # Save image
            image_filename = f"page_{page_num:03d}.png"
            image_path = Path(output_dir) / image_filename
            image.save(image_path, 'PNG')

            page_infos.append({
                'page_number': page_num,
                'image_path': str(image_path),
                'width': image.width,
                'height': image.height
            })

        return page_infos

    def process_single_page(self, pdf_path: str, page_number: int = 1) -> str:
        """
        Extract a single page from PDF as image

        Args:
            pdf_path: Path to PDF file
            page_number: Page number to extract (1-indexed)

        Returns:
            Path to the generated image
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Convert single page
        try:
            images = convert_from_path(
                str(pdf_path),
                dpi=self.dpi,
                first_page=page_number,
                last_page=page_number,
                fmt='png'
            )
        except Exception as e:
            raise RuntimeError(f"Failed to convert PDF page {page_number}: {e}")

        if not images:
            raise ValueError(f"No image generated for page {page_number}")

        # Save to temp file
        temp_dir = Path(tempfile.mkdtemp(prefix='vaultocr_'))
        image_path = temp_dir / f"page_{page_number:03d}.png"
        images[0].save(image_path, 'PNG')

        return str(image_path)
