"""
Language Detector - Automatic language detection for OCR
Supports 100+ languages with Tesseract/PaddleOCR
"""
from typing import List, Dict, Any, Optional
import re


class LanguageDetector:
    """Detects language from text or image for OCR optimization"""

    # Supported languages mapping: ISO 639-1 -> (Tesseract code, PaddleOCR code, display name)
    SUPPORTED_LANGUAGES = {
        'ja': ('jpn', 'japan', '日本語 (Japanese)'),
        'en': ('eng', 'en', 'English'),
        'zh-cn': ('chi_sim', 'ch', '中文简体 (Chinese Simplified)'),
        'zh-tw': ('chi_tra', 'chinese_cht', '中文繁體 (Chinese Traditional)'),
        'ko': ('kor', 'korean', '한국어 (Korean)'),
        'fr': ('fra', 'fr', 'Français (French)'),
        'de': ('deu', 'german', 'Deutsch (German)'),
        'es': ('spa', 'es', 'Español (Spanish)'),
        'ru': ('rus', 'ru', 'Русский (Russian)'),
        'ar': ('ara', 'ar', 'العربية (Arabic)'),
        'hi': ('hin', 'hi', 'हिन्दी (Hindi)'),
        'pt': ('por', 'pt', 'Português (Portuguese)'),
        'it': ('ita', 'it', 'Italiano (Italian)'),
        'nl': ('nld', 'nl', 'Nederlands (Dutch)'),
        'pl': ('pol', 'pl', 'Polski (Polish)'),
        'tr': ('tur', 'tr', 'Türkçe (Turkish)'),
        'vi': ('vie', 'vi', 'Tiếng Việt (Vietnamese)'),
        'th': ('tha', 'th', 'ไทย (Thai)'),
        'id': ('ind', 'id', 'Bahasa Indonesia (Indonesian)'),
        'sv': ('swe', 'sv', 'Svenska (Swedish)'),
    }

    def __init__(self):
        self._langdetect = None

    @property
    def langdetect(self):
        """Lazy load langdetect"""
        if self._langdetect is None:
            try:
                from langdetect import detect, detect_langs, LangDetectException
                self._langdetect = {
                    'detect': detect,
                    'detect_langs': detect_langs,
                    'exception': LangDetectException
                }
            except ImportError:
                # Fallback: simple heuristic-based detection
                self._langdetect = None
        return self._langdetect

    def detect_from_text(self, text: str) -> Dict[str, Any]:
        """
        Detect language from text content

        Args:
            text: Text to analyze

        Returns:
            {
                'primary': 'ja',
                'confidence': 0.95,
                'all_languages': [
                    {'lang': 'ja', 'prob': 0.95},
                    {'lang': 'en', 'prob': 0.05}
                ]
            }
        """
        if not text or len(text.strip()) < 3:
            return {'primary': 'en', 'confidence': 0.0, 'all_languages': []}

        # Try langdetect library
        if self.langdetect:
            try:
                primary = self.langdetect['detect'](text)
                langs = self.langdetect['detect_langs'](text)

                all_langs = [
                    {'lang': str(lang).split(':')[0], 'prob': float(str(lang).split(':')[1])}
                    for lang in langs
                ]

                # Map to our supported languages
                primary_mapped = self._map_to_supported(primary)

                return {
                    'primary': primary_mapped,
                    'confidence': all_langs[0]['prob'] if all_langs else 0.0,
                    'all_languages': all_langs[:5]  # Top 5
                }
            except Exception:
                pass

        # Fallback: heuristic-based detection
        return self._heuristic_detect(text)

    def _heuristic_detect(self, text: str) -> Dict[str, Any]:
        """Simple heuristic-based language detection"""
        # Japanese (Hiragana, Katakana, Kanji)
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text):
            return {'primary': 'ja', 'confidence': 0.9, 'all_languages': [{'lang': 'ja', 'prob': 0.9}]}

        # Korean (Hangul)
        if re.search(r'[\uAC00-\uD7AF]', text):
            return {'primary': 'ko', 'confidence': 0.9, 'all_languages': [{'lang': 'ko', 'prob': 0.9}]}

        # Chinese (CJK Unified Ideographs)
        if re.search(r'[\u4E00-\u9FFF]', text):
            return {'primary': 'zh-cn', 'confidence': 0.8, 'all_languages': [{'lang': 'zh-cn', 'prob': 0.8}]}

        # Arabic
        if re.search(r'[\u0600-\u06FF]', text):
            return {'primary': 'ar', 'confidence': 0.9, 'all_languages': [{'lang': 'ar', 'prob': 0.9}]}

        # Cyrillic (Russian, etc.)
        if re.search(r'[\u0400-\u04FF]', text):
            return {'primary': 'ru', 'confidence': 0.8, 'all_languages': [{'lang': 'ru', 'prob': 0.8}]}

        # Thai
        if re.search(r'[\u0E00-\u0E7F]', text):
            return {'primary': 'th', 'confidence': 0.9, 'all_languages': [{'lang': 'th', 'prob': 0.9}]}

        # Default to English
        return {'primary': 'en', 'confidence': 0.6, 'all_languages': [{'lang': 'en', 'prob': 0.6}]}

    def _map_to_supported(self, lang_code: str) -> str:
        """Map detected language to our supported language codes"""
        # Handle Chinese variants
        if lang_code == 'zh-cn' or lang_code == 'zh':
            return 'zh-cn'
        if lang_code == 'zh-tw':
            return 'zh-tw'

        # Direct mapping
        if lang_code in self.SUPPORTED_LANGUAGES:
            return lang_code

        # Try to find close match
        for supported in self.SUPPORTED_LANGUAGES.keys():
            if lang_code.startswith(supported) or supported.startswith(lang_code):
                return supported

        # Default to English
        return 'en'

    def get_ocr_lang_code(self, lang_code: str, ocr_engine: str = 'paddleocr') -> str:
        """
        Get OCR-specific language code

        Args:
            lang_code: ISO language code (e.g., 'ja', 'en')
            ocr_engine: 'paddleocr' or 'tesseract'

        Returns:
            OCR engine specific language code
        """
        if lang_code not in self.SUPPORTED_LANGUAGES:
            lang_code = self._map_to_supported(lang_code)

        lang_info = self.SUPPORTED_LANGUAGES.get(lang_code, self.SUPPORTED_LANGUAGES['en'])

        if ocr_engine == 'tesseract':
            return lang_info[0]  # Tesseract code
        else:  # paddleocr
            return lang_info[1]  # PaddleOCR code

    def get_display_name(self, lang_code: str) -> str:
        """Get human-readable language name"""
        if lang_code not in self.SUPPORTED_LANGUAGES:
            lang_code = self._map_to_supported(lang_code)

        lang_info = self.SUPPORTED_LANGUAGES.get(lang_code, self.SUPPORTED_LANGUAGES['en'])
        return lang_info[2]

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of all supported languages

        Returns:
            [
                {'code': 'ja', 'name': '日本語 (Japanese)', 'paddle': 'japan', 'tesseract': 'jpn'},
                ...
            ]
        """
        return [
            {
                'code': code,
                'name': info[2],
                'paddleocr': info[1],
                'tesseract': info[0]
            }
            for code, info in self.SUPPORTED_LANGUAGES.items()
        ]

    def detect_mixed_languages(self, text: str, chunk_size: int = 100) -> List[Dict[str, Any]]:
        """
        Detect multiple languages in a single document
        Split text into chunks and detect language for each

        Args:
            text: Full text to analyze
            chunk_size: Characters per chunk

        Returns:
            [
                {'start': 0, 'end': 100, 'lang': 'ja', 'confidence': 0.95},
                {'start': 100, 'end': 200, 'lang': 'en', 'confidence': 0.92},
                ...
            ]
        """
        if not text:
            return []

        chunks = []
        text_length = len(text)

        for i in range(0, text_length, chunk_size):
            chunk_text = text[i:i+chunk_size]
            if chunk_text.strip():
                detection = self.detect_from_text(chunk_text)
                chunks.append({
                    'start': i,
                    'end': min(i + chunk_size, text_length),
                    'lang': detection['primary'],
                    'confidence': detection['confidence']
                })

        return chunks

    def get_dominant_languages(self, text: str, top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Get dominant languages in document

        Returns:
            [
                {'lang': 'ja', 'percentage': 0.7, 'char_count': 700},
                {'lang': 'en', 'percentage': 0.3, 'char_count': 300},
            ]
        """
        chunks = self.detect_mixed_languages(text)

        if not chunks:
            return []

        # Count characters per language
        lang_counts = {}
        total_chars = 0

        for chunk in chunks:
            lang = chunk['lang']
            char_count = chunk['end'] - chunk['start']
            lang_counts[lang] = lang_counts.get(lang, 0) + char_count
            total_chars += char_count

        # Calculate percentages and sort
        results = [
            {
                'lang': lang,
                'char_count': count,
                'percentage': count / total_chars if total_chars > 0 else 0
            }
            for lang, count in lang_counts.items()
        ]

        results.sort(key=lambda x: x['char_count'], reverse=True)

        return results[:top_n]
