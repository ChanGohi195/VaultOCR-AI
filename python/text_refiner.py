"""
Text Refiner - Converts line-level OCR results into paragraph text
Phase 2: Smart paragraph detection, hyphenation, language detection, error correction
"""
from typing import Dict, Any, List
import re
import pysbd


class TextRefiner:
    """Refines OCR text into natural paragraphs"""

    def __init__(self):
        self.segmenter = pysbd.Segmenter(language="en", clean=False)

        # Common OCR error patterns
        self.ocr_corrections = {
            # Letter confusions
            r'\b0\b': 'O',  # 0 -> O (standalone)
            r'\bl\b': 'I',  # l -> I (standalone)
            r'\brn\b': 'm',  # rn -> m
            r'\|': 'I',  # | -> I

            # Common character substitutions
            r'(?<=[a-z])1(?=[a-z])': 'l',  # 1 -> l (between letters)
            r'(?<=[a-z])0(?=[a-z])': 'o',  # 0 -> o (between letters)
        }

    def refine(self, layout_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert layout chunks into clean paragraph text

        Phase 2: Smart paragraph detection, hyphenation handling, error correction
        """
        chunks = layout_result.get('chunks', [])
        layout_type = layout_result.get('layout_type', 'one_column')

        paragraphs = []
        markdown_parts = []

        for chunk in chunks:
            chunk_type = chunk.get('type', 'body')
            lines = chunk.get('lines', [])

            if not lines:
                continue

            # Detect language
            language = self._detect_language(lines)

            # Phase 2: Smart paragraph joining
            paragraph_text = self._smart_paragraph_join(lines, language)

            # Apply OCR error corrections
            paragraph_text = self._correct_ocr_errors(paragraph_text)

            paragraphs.append({
                'type': chunk_type,
                'text': paragraph_text,
                'chunk_id': chunk['chunk_id'],
                'language': language
            })

            # Build markdown
            markdown_parts.append(self._format_markdown(chunk_type, paragraph_text, chunk))

        return {
            'paragraphs': paragraphs,
            'markdown': ''.join(markdown_parts).strip()
        }

    def _detect_language(self, lines: List[Dict]) -> str:
        """Detect if text is primarily Japanese or English"""
        if not lines:
            return 'en'

        combined_text = ' '.join([line['text'] for line in lines[:5]])  # Sample first 5 lines

        # Count Japanese characters (Hiragana, Katakana, Kanji)
        japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', combined_text))
        total_chars = len(combined_text.replace(' ', ''))

        if total_chars == 0:
            return 'en'

        japanese_ratio = japanese_chars / total_chars

        return 'ja' if japanese_ratio > 0.3 else 'en'

    def _smart_paragraph_join(self, lines: List[Dict], language: str) -> str:
        """
        Phase 2: Smart paragraph detection
        - Detect sentence endings
        - Handle hyphenation
        - Preserve intentional line breaks
        """
        if not lines:
            return ""

        if language == 'ja':
            return self._join_japanese_paragraphs(lines)
        else:
            return self._join_english_paragraphs(lines)

    def _join_english_paragraphs(self, lines: List[Dict]) -> str:
        """Join English text lines intelligently"""
        if not lines:
            return ""

        paragraphs = []
        current_paragraph = []

        for i, line in enumerate(lines):
            text = line['text'].strip()

            if not text:
                # Empty line = paragraph break
                if current_paragraph:
                    paragraphs.append(self._merge_lines(current_paragraph))
                    current_paragraph = []
                continue

            # Handle hyphenation (word split across lines)
            if text.endswith('-'):
                # Remove hyphen and continue to next line
                text = text[:-1]
                current_paragraph.append(text)
                continue

            current_paragraph.append(text)

            # Check if this is a paragraph boundary
            if self._is_paragraph_end_english(text, lines[i+1] if i+1 < len(lines) else None):
                paragraphs.append(self._merge_lines(current_paragraph))
                current_paragraph = []

        # Add remaining paragraph
        if current_paragraph:
            paragraphs.append(self._merge_lines(current_paragraph))

        return '\n\n'.join(paragraphs)

    def _join_japanese_paragraphs(self, lines: List[Dict]) -> str:
        """Join Japanese text lines intelligently"""
        if not lines:
            return ""

        paragraphs = []
        current_paragraph = []

        for i, line in enumerate(lines):
            text = line['text'].strip()

            if not text:
                if current_paragraph:
                    paragraphs.append(''.join(current_paragraph))  # No space for Japanese
                    current_paragraph = []
                continue

            current_paragraph.append(text)

            # Check if this is a paragraph boundary (Japanese sentence ending)
            if self._is_paragraph_end_japanese(text, lines[i+1] if i+1 < len(lines) else None):
                paragraphs.append(''.join(current_paragraph))
                current_paragraph = []

        if current_paragraph:
            paragraphs.append(''.join(current_paragraph))

        return '\n\n'.join(paragraphs)

    def _merge_lines(self, lines: List[str]) -> str:
        """Merge English lines with proper spacing"""
        if not lines:
            return ""

        result = []
        for line in lines:
            if result and not result[-1].endswith('-'):
                result.append(' ')
            result.append(line)

        return ''.join(result)

    def _is_paragraph_end_english(self, current_line: str, next_line: Dict | None) -> bool:
        """Detect if current line is the end of a paragraph (English)"""
        # End with sentence-ending punctuation
        if re.search(r'[.!?]"?\s*$', current_line):
            if not next_line:
                return True

            next_text = next_line.get('text', '').strip()

            # Next line starts with capital letter or empty
            if not next_text or next_text[0].isupper():
                return True

            # Next line is indented (new paragraph)
            # This would require bbox analysis - skip for now

        return False

    def _is_paragraph_end_japanese(self, current_line: str, next_line: Dict | None) -> bool:
        """Detect if current line is the end of a paragraph (Japanese)"""
        # Japanese sentence ending marks
        if re.search(r'[。！？]$', current_line):
            if not next_line:
                return True

            next_text = next_line.get('text', '').strip()

            # Next line is empty or starts with indent marker
            if not next_text or next_text.startswith('　'):  # Full-width space
                return True

        return False

    def _correct_ocr_errors(self, text: str) -> str:
        """Apply common OCR error corrections"""
        result = text

        for pattern, replacement in self.ocr_corrections.items():
            result = re.sub(pattern, replacement, result)

        return result

    def _format_markdown(self, chunk_type: str, text: str, chunk: Dict) -> str:
        """Format chunk as Markdown based on type"""
        if chunk_type == 'header':
            return f"# {text}\n\n"
        elif chunk_type == 'footer':
            return f"---\n*{text}*\n\n"
        elif chunk_type == 'body':
            # Check if multi-column
            column = chunk.get('column')
            if column:
                return f"**Column {column}**\n\n{text}\n\n"
            else:
                return f"{text}\n\n"
        else:
            return f"{text}\n\n"
