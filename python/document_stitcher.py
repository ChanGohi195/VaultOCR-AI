"""
Document Stitcher - Combines multiple pages into coherent document
Handles page-spanning paragraphs, heading detection, and reading order
"""
from typing import Dict, Any, List, Tuple
import re


class DocumentStitcher:
    """Stitches multiple OCR pages into a single coherent document"""

    def __init__(self):
        # Heading patterns (numbered sections, all caps, etc.)
        self.heading_patterns = [
            r'^\d+\.?\s+[A-Z]',  # "1. Introduction", "2 Methods"
            r'^[A-Z][A-Z\s]{3,}$',  # "INTRODUCTION", "METHODS AND RESULTS"
            r'^Chapter\s+\d+',  # "Chapter 1"
            r'^第[0-9一二三四五六七八九十百]+章',  # "第1章", "第一章"
            r'^[IVX]+\.\s+[A-Z]',  # "I. Introduction"
        ]

    def stitch_pages(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine multiple page results into single document

        Args:
            pages: List of page OCR results
                [{
                    'page_number': 1,
                    'paragraphs': [...],
                    'layout_type': 'two_column',
                    'chunks': [...]
                }, ...]

        Returns:
            {
                'paragraphs': [...],  # Combined paragraphs
                'sections': [...],    # Detected sections
                'toc': [...],        # Table of contents (headings)
                'markdown': '...'
            }
        """
        if not pages:
            return {'paragraphs': [], 'sections': [], 'toc': [], 'markdown': ''}

        # Extract all paragraphs with metadata
        all_paragraphs = []
        for page in pages:
            page_num = page.get('page_number', 0)
            for para in page.get('paragraphs', []):
                para_copy = para.copy()
                para_copy['page_number'] = page_num
                all_paragraphs.append(para_copy)

        # Connect page-spanning paragraphs
        connected_paragraphs = self._connect_page_breaks(all_paragraphs)

        # Detect headings
        paragraphs_with_headings = self._detect_headings(connected_paragraphs)

        # Build sections
        sections = self._build_sections(paragraphs_with_headings)

        # Generate table of contents
        toc = self._generate_toc(paragraphs_with_headings)

        # Generate final markdown
        markdown = self._generate_markdown(paragraphs_with_headings)

        return {
            'paragraphs': paragraphs_with_headings,
            'sections': sections,
            'toc': toc,
            'markdown': markdown
        }

    def _connect_page_breaks(self, paragraphs: List[Dict]) -> List[Dict]:
        """Connect paragraphs that span across page boundaries"""
        if len(paragraphs) <= 1:
            return paragraphs

        result = []
        i = 0

        while i < len(paragraphs):
            current = paragraphs[i]
            current_text = current['text']

            # Check if this paragraph should be merged with next
            if i + 1 < len(paragraphs):
                next_para = paragraphs[i + 1]

                # Only merge if on consecutive pages
                if next_para.get('page_number', 0) == current.get('page_number', 0) + 1:
                    if self._should_merge_paragraphs(current_text, next_para['text']):
                        # Merge paragraphs
                        merged = current.copy()
                        merged['text'] = self._merge_paragraph_text(
                            current_text,
                            next_para['text'],
                            current.get('language', 'en')
                        )
                        merged['page_span'] = [
                            current.get('page_number', 0),
                            next_para.get('page_number', 0)
                        ]
                        result.append(merged)
                        i += 2  # Skip next paragraph (already merged)
                        continue

            result.append(current)
            i += 1

        return result

    def _should_merge_paragraphs(self, text1: str, text2: str) -> bool:
        """Determine if two paragraphs should be merged"""
        text1 = text1.strip()
        text2 = text2.strip()

        if not text1 or not text2:
            return False

        # Don't merge if first paragraph ends with strong punctuation
        if re.search(r'[.!?。！？]\s*$', text1):
            # But check if next paragraph continues a list or similar
            if re.match(r'^[\d•\-\*]', text2):
                return False
            # If next starts with lowercase (English), likely continuation
            if text2[0].islower():
                return True
            return False

        # Don't merge if next paragraph looks like a heading
        for pattern in self.heading_patterns:
            if re.match(pattern, text2):
                return False

        # Merge if first paragraph ends mid-sentence
        # (no punctuation, or ends with comma/semicolon)
        if re.search(r'[,;、]\s*$', text1):
            return True

        # Merge if first paragraph doesn't end with punctuation
        if not re.search(r'[.!?。！？:：]\s*$', text1):
            return True

        return False

    def _merge_paragraph_text(self, text1: str, text2: str, language: str) -> str:
        """Merge two paragraph texts intelligently"""
        text1 = text1.strip()
        text2 = text2.strip()

        if language == 'ja':
            # Japanese: no space needed
            return text1 + text2
        else:
            # English: add space
            return text1 + ' ' + text2

    def _detect_headings(self, paragraphs: List[Dict]) -> List[Dict]:
        """Detect which paragraphs are headings"""
        result = []

        for para in paragraphs:
            text = para['text'].strip()

            # Check heading patterns
            is_heading = False
            heading_level = 0

            for i, pattern in enumerate(self.heading_patterns):
                if re.match(pattern, text):
                    is_heading = True
                    heading_level = min(i + 1, 3)  # h1, h2, or h3
                    break

            # Additional heuristics
            if not is_heading and len(text) < 100:
                # Short paragraph might be heading
                # Check if all caps (English)
                if text.isupper() and len(text.split()) <= 6:
                    is_heading = True
                    heading_level = 2

                # Check if starts with number pattern
                elif re.match(r'^\d+(\.\d+)*\s+[A-ZA-Z]', text):
                    is_heading = True
                    heading_level = text.count('.') + 1

            para_copy = para.copy()
            para_copy['is_heading'] = is_heading
            para_copy['heading_level'] = heading_level if is_heading else 0
            result.append(para_copy)

        return result

    def _build_sections(self, paragraphs: List[Dict]) -> List[Dict]:
        """Build document sections based on headings"""
        sections = []
        current_section = None

        for para in paragraphs:
            if para.get('is_heading'):
                # Start new section
                if current_section:
                    sections.append(current_section)

                current_section = {
                    'title': para['text'],
                    'level': para['heading_level'],
                    'paragraphs': [],
                    'page_start': para.get('page_number', 0)
                }
            elif current_section:
                current_section['paragraphs'].append(para)

        # Add last section
        if current_section:
            sections.append(current_section)

        return sections

    def _generate_toc(self, paragraphs: List[Dict]) -> List[Dict]:
        """Generate table of contents from headings"""
        toc = []

        for i, para in enumerate(paragraphs):
            if para.get('is_heading'):
                toc.append({
                    'index': i,
                    'title': para['text'],
                    'level': para['heading_level'],
                    'page': para.get('page_number', 0)
                })

        return toc

    def _generate_markdown(self, paragraphs: List[Dict]) -> str:
        """Generate final markdown document"""
        parts = []

        for para in paragraphs:
            text = para['text']

            if para.get('is_heading'):
                # Heading
                level = para['heading_level']
                parts.append(f"{'#' * level} {text}\n")
            elif para.get('type') == 'footer':
                # Footer (italic, smaller)
                parts.append(f"*{text}*\n")
            else:
                # Regular paragraph
                parts.append(f"{text}\n")

            parts.append('\n')  # Add spacing

        return ''.join(parts).strip()
