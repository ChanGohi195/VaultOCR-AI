"""
Phase 9: AI Summarization Engine
Provides multilingual text summarization using transformer models
"""

from typing import Dict, Any, Optional, List
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import logging
import torch

logger = logging.getLogger(__name__)


class SummarizationEngine:
    """AI-powered text summarization engine with multilingual support"""

    # Model configurations for different languages
    MODELS = {
        'en': 'facebook/bart-large-cnn',  # English summarization
        'multilingual': 'csebuetnlp/mT5_multilingual_XLSum',  # 45 languages
        'ja': 'sonoisa/t5-base-japanese',  # Japanese specific
    }

    def __init__(self, default_model: str = 'multilingual'):
        """
        Initialize summarization engine

        Args:
            default_model: Which model to use by default ('en', 'multilingual', 'ja')
        """
        self.default_model = default_model
        self._pipelines = {}
        self._tokenizers = {}
        self._models = {}

        logger.info(f"SummarizationEngine initialized (default: {default_model})")

    def get_pipeline(self, model_type: str = None):
        """Get or create summarization pipeline for specific model"""
        if model_type is None:
            model_type = self.default_model

        if model_type in self._pipelines:
            return self._pipelines[model_type]

        try:
            model_name = self.MODELS.get(model_type, self.MODELS['multilingual'])
            logger.info(f"Loading summarization model: {model_name}")

            # Use CPU by default, GPU if available
            device = 0 if torch.cuda.is_available() else -1

            summarizer = pipeline(
                "summarization",
                model=model_name,
                device=device
            )

            self._pipelines[model_type] = summarizer
            logger.info(f"Model loaded successfully: {model_name}")

            return summarizer
        except Exception as e:
            logger.error(f"Failed to load summarization model {model_type}: {e}")
            raise

    def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 40,
        language: str = 'en',
        ratio: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Summarize text using AI models

        Args:
            text: Input text to summarize
            max_length: Maximum length of summary (tokens)
            min_length: Minimum length of summary (tokens)
            language: Language of the text ('en', 'ja', etc.)
            ratio: Compression ratio (e.g., 0.3 = 30% of original length)

        Returns:
            {
                'summary': str,
                'original_length': int,
                'summary_length': int,
                'compression_ratio': float,
                'model_used': str
            }
        """
        if not text or len(text.strip()) == 0:
            return {
                'error': 'Empty text provided',
                'summary': ''
            }

        # Determine which model to use
        model_type = self._select_model(language)

        try:
            # Calculate adaptive lengths based on input
            original_words = len(text.split())

            if ratio is not None:
                # Calculate lengths based on compression ratio
                target_words = int(original_words * ratio)
                max_length = min(max(target_words * 2, min_length), 512)
                min_length = min(target_words // 2, max_length // 2)
            else:
                # Adaptive limits based on input length
                if original_words < 100:
                    max_length = 50
                    min_length = 20
                elif original_words < 500:
                    max_length = 150
                    min_length = 40
                else:
                    max_length = 300
                    min_length = 80

            # Get summarization pipeline
            summarizer = self.get_pipeline(model_type)

            # Truncate if too long (most models have max input length)
            max_input_length = 1024
            if len(text) > max_input_length * 4:  # rough character estimate
                logger.warning(f"Text too long ({len(text)} chars), truncating")
                text = text[:max_input_length * 4]

            # Generate summary
            result = summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True
            )

            summary_text = result[0]['summary_text']
            summary_words = len(summary_text.split())

            return {
                'summary': summary_text,
                'original_length': original_words,
                'summary_length': summary_words,
                'compression_ratio': summary_words / original_words if original_words > 0 else 0,
                'model_used': self.MODELS.get(model_type, 'unknown'),
                'language': language
            }

        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return {
                'error': str(e),
                'summary': text[:500] + '...' if len(text) > 500 else text,
                'fallback': True
            }

    def summarize_sections(
        self,
        sections: List[Dict[str, Any]],
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Summarize document by sections

        Args:
            sections: List of section dicts with 'title' and 'content'
            language: Document language

        Returns:
            {
                'section_summaries': List[{title, summary, original_length, summary_length}],
                'overall_summary': str,
                'total_compression': float
            }
        """
        section_summaries = []
        total_original = 0
        total_summary = 0

        for section in sections:
            title = section.get('title', 'Untitled')
            content = section.get('content', '')

            if not content:
                continue

            result = self.summarize(content, language=language)

            section_summaries.append({
                'title': title,
                'summary': result.get('summary', ''),
                'original_length': result.get('original_length', 0),
                'summary_length': result.get('summary_length', 0)
            })

            total_original += result.get('original_length', 0)
            total_summary += result.get('summary_length', 0)

        # Generate overall summary from section summaries
        combined_summaries = '\n\n'.join([
            f"{s['title']}: {s['summary']}" for s in section_summaries
        ])

        overall_result = self.summarize(
            combined_summaries,
            max_length=200,
            min_length=50,
            language=language
        )

        return {
            'section_summaries': section_summaries,
            'overall_summary': overall_result.get('summary', ''),
            'total_compression': total_summary / total_original if total_original > 0 else 0
        }

    def _select_model(self, language: str) -> str:
        """Select appropriate model based on language"""
        if language == 'en':
            return 'en'
        elif language == 'ja':
            return 'ja'
        else:
            return 'multilingual'

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages for summarization"""
        return [
            'en', 'ja', 'zh', 'zh-cn', 'zh-tw', 'ko', 'fr', 'de', 'es', 'ru',
            'ar', 'hi', 'pt', 'it', 'nl', 'pl', 'tr', 'vi', 'th', 'id',
            'sw', 'bn', 'mr', 'te', 'ta', 'ur', 'gu', 'kn', 'ml', 'pa',
            'or', 'my', 'km', 'am', 'so', 'az', 'uz', 'ps', 'fa', 'tg',
            'ky', 'ti', 'om', 'ne', 'si'
        ]
