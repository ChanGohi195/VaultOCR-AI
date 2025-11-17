"""
Built-in Plugin: Spell Correction
Advanced spell checking and correction for OCR text
"""

from plugin_interface import PostprocessorPlugin, PluginPriority
from typing import Dict, Any
import re


class SpellCorrectionPlugin(PostprocessorPlugin):
    """
    Spell correction plugin for OCR text

    Fixes common OCR errors and typos
    Supports multiple languages with customizable dictionaries
    """

    @property
    def name(self) -> str:
        return "spell_correction"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Automatic spell checking and correction for OCR text"

    @property
    def author(self) -> str:
        return "VaultOCR-AI Team"

    @property
    def priority(self) -> PluginPriority:
        return PluginPriority.NORMAL

    @property
    def dependencies(self) -> list:
        return []  # Using lightweight built-in corrections

    @property
    def config_schema(self) -> Dict[str, Any]:
        return {
            'language': {
                'type': 'string',
                'default': 'en',
                'description': 'Language for spell checking (en, ja, etc.)',
                'required': False
            },
            'aggressive': {
                'type': 'bool',
                'default': False,
                'description': 'More aggressive correction (may introduce errors)',
                'required': False
            },
            'preserve_case': {
                'type': 'bool',
                'default': True,
                'description': 'Preserve original case in corrections',
                'required': False
            },
            'custom_replacements': {
                'type': 'dict',
                'default': {},
                'description': 'Custom word replacements {wrong: correct}',
                'required': False
            }
        }

    # Common OCR confusion patterns
    OCR_CORRECTIONS = {
        'en': {
            # Common OCR errors (pattern: replacement)
            r'\bl\b': 'I',  # lowercase l as I
            r'\bO\b': '0',  # O as zero in numbers
            r'rn': 'm',     # rn often misread as m
            r'vv': 'w',     # vv as w
            r'cl': 'd',     # cl as d
            r'li': 'h',     # li as h (context-dependent)

            # Common word-level corrections
            r'\bteh\b': 'the',
            r'\badn\b': 'and',
            r'\bwlth\b': 'with',
            r'\bfrom\b': 'from',
            r'\bthat\b': 'that',
            r'\bthls\b': 'this',
            r'\bflrst\b': 'first',
            r'\bsecond\b': 'second',
            r'\bnumber\b': 'number',
            r'\bw0rd\b': 'word',
        },
        'ja': {
            # Japanese OCR corrections (common misreads)
            '工': '二',  # May be misread
            '―': 'ー',  # Different dash types
            # Add more Japanese-specific corrections
        }
    }

    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """
        Apply spell correction to OCR text

        Args:
            text: Raw OCR text
            context: Processing context

        Returns:
            Corrected text
        """
        if not text:
            return text

        # Get config
        language = self._config.get('language', 'en')
        aggressive = self._config.get('aggressive', False)
        preserve_case = self._config.get('preserve_case', True)
        custom_replacements = self._config.get('custom_replacements', {})

        corrected = text

        try:
            # Apply custom replacements first
            for wrong, correct in custom_replacements.items():
                if preserve_case:
                    corrected = self._case_preserving_replace(corrected, wrong, correct)
                else:
                    corrected = corrected.replace(wrong, correct)

            # Apply language-specific OCR corrections
            if language in self.OCR_CORRECTIONS:
                corrections = self.OCR_CORRECTIONS[language]

                for pattern, replacement in corrections.items():
                    if preserve_case and pattern.startswith(r'\b') and pattern.endswith(r'\b'):
                        # Word-level replacement with case preservation
                        corrected = re.sub(
                            pattern,
                            lambda m: self._preserve_case(m.group(0), replacement),
                            corrected,
                            flags=re.IGNORECASE
                        )
                    else:
                        # Character-level or simple replacement
                        corrected = re.sub(pattern, replacement, corrected)

            # Fix common spacing issues
            corrected = self._fix_spacing(corrected)

            # Fix common punctuation issues
            corrected = self._fix_punctuation(corrected)

            # More aggressive corrections if enabled
            if aggressive:
                corrected = self._aggressive_corrections(corrected)

            return corrected

        except Exception as e:
            print(f"Spell correction failed: {e}")
            return text

    def _case_preserving_replace(self, text: str, old: str, new: str) -> str:
        """Replace text while preserving case"""
        def replace_func(match):
            matched = match.group(0)
            if matched.isupper():
                return new.upper()
            elif matched.istitle():
                return new.title()
            elif matched.islower():
                return new.lower()
            else:
                return new

        return re.sub(re.escape(old), replace_func, text, flags=re.IGNORECASE)

    def _preserve_case(self, original: str, replacement: str) -> str:
        """Preserve case pattern of original in replacement"""
        if original.isupper():
            return replacement.upper()
        elif original.istitle():
            return replacement.title()
        elif original.islower():
            return replacement.lower()
        else:
            return replacement

    def _fix_spacing(self, text: str) -> str:
        """Fix common spacing issues"""
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)

        # Fix space before punctuation
        text = re.sub(r' +([.,!?;:])', r'\1', text)

        # Fix space after punctuation
        text = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', text)

        # Fix paragraph spacing
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text

    def _fix_punctuation(self, text: str) -> str:
        """Fix common punctuation issues"""
        # Fix quotes
        text = re.sub(r'``', '"', text)
        text = re.sub(r"''", '"', text)

        # Fix hyphens/dashes
        text = re.sub(r'--', '—', text)

        # Fix ellipsis
        text = re.sub(r'\.\.\.', '…', text)

        return text

    def _aggressive_corrections(self, text: str) -> str:
        """More aggressive corrections (may introduce errors)"""
        # Fix common word patterns
        corrections = {
            r'\b(\w)(\1{2,})\b': r'\1\1',  # Repeated characters (fff -> ff)
            r'\b([A-Z])\1+\b': r'\1',       # Single repeated capitals (AAA -> A)
        }

        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text)

        return text
