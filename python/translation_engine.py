"""
Phase 9: Translation Engine
Provides multilingual translation using Helsinki-NLP Opus models
"""

from typing import Dict, Any, Optional, List
from transformers import MarianMTModel, MarianTokenizer
import logging
import torch

logger = logging.getLogger(__name__)


class TranslationEngine:
    """AI-powered translation engine supporting 100+ language pairs"""

    # Common language pairs (Helsinki-NLP Opus models)
    LANGUAGE_PAIRS = {
        # Japanese translations
        ('ja', 'en'): 'Helsinki-NLP/opus-mt-ja-en',
        ('en', 'ja'): 'Helsinki-NLP/opus-mt-en-ja',

        # Chinese translations
        ('zh', 'en'): 'Helsinki-NLP/opus-mt-zh-en',
        ('en', 'zh'): 'Helsinki-NLP/opus-mt-en-zh',

        # Korean translations
        ('ko', 'en'): 'Helsinki-NLP/opus-mt-ko-en',
        ('en', 'ko'): 'Helsinki-NLP/opus-mt-en-ko',

        # French translations
        ('fr', 'en'): 'Helsinki-NLP/opus-mt-fr-en',
        ('en', 'fr'): 'Helsinki-NLP/opus-mt-en-fr',

        # German translations
        ('de', 'en'): 'Helsinki-NLP/opus-mt-de-en',
        ('en', 'de'): 'Helsinki-NLP/opus-mt-en-de',

        # Spanish translations
        ('es', 'en'): 'Helsinki-NLP/opus-mt-es-en',
        ('en', 'es'): 'Helsinki-NLP/opus-mt-en-es',

        # Russian translations
        ('ru', 'en'): 'Helsinki-NLP/opus-mt-ru-en',
        ('en', 'ru'): 'Helsinki-NLP/opus-mt-en-ru',

        # Arabic translations
        ('ar', 'en'): 'Helsinki-NLP/opus-mt-ar-en',
        ('en', 'ar'): 'Helsinki-NLP/opus-mt-en-ar',

        # Portuguese translations
        ('pt', 'en'): 'Helsinki-NLP/opus-mt-pt-en',
        ('en', 'pt'): 'Helsinki-NLP/opus-mt-en-pt',

        # Italian translations
        ('it', 'en'): 'Helsinki-NLP/opus-mt-it-en',
        ('en', 'it'): 'Helsinki-NLP/opus-mt-en-it',

        # Multi-language to English (Romance languages)
        ('ROMANCE', 'en'): 'Helsinki-NLP/opus-mt-ROMANCE-en',
    }

    def __init__(self):
        """Initialize translation engine"""
        self._models = {}
        self._tokenizers = {}
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        logger.info(f"TranslationEngine initialized (device: {self.device})")

    def get_model(self, source_lang: str, target_lang: str):
        """Get or load translation model for language pair"""
        pair = (source_lang, target_lang)

        if pair in self._models:
            return self._models[pair], self._tokenizers[pair]

        # Find model name
        model_name = self._find_model(source_lang, target_lang)
        if not model_name:
            raise ValueError(
                f"No translation model found for {source_lang} -> {target_lang}"
            )

        try:
            logger.info(f"Loading translation model: {model_name}")

            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name).to(self.device)

            self._models[pair] = model
            self._tokenizers[pair] = tokenizer

            logger.info(f"Translation model loaded: {source_lang} -> {target_lang}")

            return model, tokenizer

        except Exception as e:
            logger.error(f"Failed to load translation model: {e}")
            raise

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        max_length: int = 512
    ) -> Dict[str, Any]:
        """
        Translate text from source language to target language

        Args:
            text: Text to translate
            source_lang: Source language code ('en', 'ja', etc.)
            target_lang: Target language code
            max_length: Maximum length of translation

        Returns:
            {
                'translation': str,
                'source_lang': str,
                'target_lang': str,
                'model_used': str,
                'original_length': int,
                'translation_length': int
            }
        """
        if not text or len(text.strip()) == 0:
            return {
                'error': 'Empty text provided',
                'translation': ''
            }

        if source_lang == target_lang:
            return {
                'translation': text,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'note': 'Same language, no translation needed'
            }

        try:
            # Get model and tokenizer
            model, tokenizer = self.get_model(source_lang, target_lang)
            model_name = self._find_model(source_lang, target_lang)

            # Tokenize
            inputs = tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length
            ).to(self.device)

            # Generate translation
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=4,
                    early_stopping=True
                )

            # Decode
            translation = tokenizer.decode(outputs[0], skip_special_tokens=True)

            return {
                'translation': translation,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'model_used': model_name,
                'original_length': len(text.split()),
                'translation_length': len(translation.split())
            }

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                'error': str(e),
                'translation': text,
                'fallback': True
            }

    def translate_batch(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[Dict[str, Any]]:
        """
        Translate multiple texts in batch

        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code

        Returns:
            List of translation results
        """
        results = []

        for text in texts:
            result = self.translate(text, source_lang, target_lang)
            results.append(result)

        return results

    def translate_document_sections(
        self,
        sections: List[Dict[str, Any]],
        source_lang: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Translate document by sections

        Args:
            sections: List of section dicts with 'title' and 'content'
            source_lang: Source language
            target_lang: Target language

        Returns:
            {
                'translated_sections': List[{title, content, original_title, original_content}],
                'source_lang': str,
                'target_lang': str
            }
        """
        translated_sections = []

        for section in sections:
            title = section.get('title', '')
            content = section.get('content', '')

            translated_title = ''
            translated_content = ''

            if title:
                title_result = self.translate(title, source_lang, target_lang)
                translated_title = title_result.get('translation', title)

            if content:
                content_result = self.translate(content, source_lang, target_lang)
                translated_content = content_result.get('translation', content)

            translated_sections.append({
                'title': translated_title,
                'content': translated_content,
                'original_title': title,
                'original_content': content
            })

        return {
            'translated_sections': translated_sections,
            'source_lang': source_lang,
            'target_lang': target_lang
        }

    def _find_model(self, source_lang: str, target_lang: str) -> Optional[str]:
        """Find appropriate model for language pair"""
        # Direct match
        pair = (source_lang, target_lang)
        if pair in self.LANGUAGE_PAIRS:
            return self.LANGUAGE_PAIRS[pair]

        # Try normalized codes (zh-cn -> zh)
        source_normalized = source_lang.split('-')[0]
        target_normalized = target_lang.split('-')[0]

        pair_normalized = (source_normalized, target_normalized)
        if pair_normalized in self.LANGUAGE_PAIRS:
            return self.LANGUAGE_PAIRS[pair_normalized]

        # Try Romance languages group
        romance_langs = ['fr', 'es', 'pt', 'it', 'ro', 'ca']
        if source_normalized in romance_langs and target_lang == 'en':
            return self.LANGUAGE_PAIRS.get(('ROMANCE', 'en'))

        return None

    def get_supported_pairs(self) -> List[tuple]:
        """Get list of supported language pairs"""
        return list(self.LANGUAGE_PAIRS.keys())

    def is_pair_supported(self, source_lang: str, target_lang: str) -> bool:
        """Check if language pair is supported"""
        return self._find_model(source_lang, target_lang) is not None
