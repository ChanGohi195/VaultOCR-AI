"""
Text Refiner - Converts line-level OCR results into paragraph text
"""
from typing import Dict, Any, List


class TextRefiner:
    """Refines OCR text into natural paragraphs"""

    def refine(self, layout_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert layout chunks into clean paragraph text

        Phase 1: Simple line joining
        Phase 2: Smart paragraph detection, hyphenation handling, etc.
        """
        chunks = layout_result.get('chunks', [])

        paragraphs = []
        markdown_parts = []

        for chunk in chunks:
            chunk_type = chunk.get('type', 'body')
            lines = chunk.get('lines', [])

            # Phase 1: Simple joining with newlines
            paragraph_text = self._simple_join(lines)

            paragraphs.append({
                'type': chunk_type,
                'text': paragraph_text,
                'chunk_id': chunk['chunk_id']
            })

            # Build markdown
            if chunk_type == 'header':
                markdown_parts.append(f"# {paragraph_text}\n\n")
            elif chunk_type == 'body':
                markdown_parts.append(f"{paragraph_text}\n\n")
            else:
                markdown_parts.append(f"{paragraph_text}\n\n")

        return {
            'paragraphs': paragraphs,
            'markdown': ''.join(markdown_parts).strip()
        }

    def _simple_join(self, lines: List[Dict]) -> str:
        """Phase 1: Simply join lines with newlines"""
        if not lines:
            return ""

        text_lines = [line['text'] for line in lines]
        return '\n'.join(text_lines)

    def _smart_paragraph_join(self, lines: List[Dict]) -> str:
        """
        Phase 2: Smart paragraph detection
        - Detect sentence endings
        - Handle hyphenation
        - Preserve intentional line breaks
        """
        # TODO: Implement in Phase 2
        pass
