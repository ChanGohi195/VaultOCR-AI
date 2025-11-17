"""
Phase 10: Plugin Interface
Defines the standard plugin API for VaultOCR-AI extensibility
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins supported"""
    PREPROCESSOR = "preprocessor"      # Image preprocessing (before OCR)
    OCR_ENGINE = "ocr_engine"          # Custom OCR engine
    POSTPROCESSOR = "postprocessor"    # Text postprocessing (after OCR)
    EXPORTER = "exporter"              # Custom export format
    ANALYZER = "analyzer"              # Custom analysis/extraction


class PluginPriority(Enum):
    """Plugin execution priority"""
    LOWEST = 0
    LOW = 25
    NORMAL = 50
    HIGH = 75
    HIGHEST = 100


class BasePlugin(ABC):
    """
    Base class for all VaultOCR-AI plugins

    All plugins must inherit from this class and implement required methods
    """

    def __init__(self):
        self._enabled = True
        self._config = {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name (unique identifier)"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version (semantic versioning)"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass

    @property
    @abstractmethod
    def author(self) -> str:
        """Plugin author"""
        pass

    @property
    @abstractmethod
    def plugin_type(self) -> PluginType:
        """Type of plugin"""
        pass

    @property
    def priority(self) -> PluginPriority:
        """Execution priority (default: NORMAL)"""
        return PluginPriority.NORMAL

    @property
    def dependencies(self) -> List[str]:
        """List of required Python packages"""
        return []

    @property
    def config_schema(self) -> Dict[str, Any]:
        """
        Configuration schema for the plugin

        Returns:
            {
                'param_name': {
                    'type': 'string|int|float|bool',
                    'default': value,
                    'description': 'param description',
                    'required': True/False
                }
            }
        """
        return {}

    def configure(self, config: Dict[str, Any]):
        """
        Configure the plugin with user settings

        Args:
            config: Configuration dictionary
        """
        self._config = config
        logger.info(f"Plugin {self.name} configured: {config}")

    def enable(self):
        """Enable the plugin"""
        self._enabled = True
        logger.info(f"Plugin {self.name} enabled")

    def disable(self):
        """Disable the plugin"""
        self._enabled = False
        logger.info(f"Plugin {self.name} disabled")

    @property
    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return self._enabled

    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate configuration against schema

        Returns:
            (is_valid, error_message)
        """
        schema = self.config_schema

        for param, spec in schema.items():
            if spec.get('required', False) and param not in config:
                return False, f"Missing required parameter: {param}"

            if param in config:
                expected_type = spec.get('type')
                value = config[param]

                # Type validation
                if expected_type == 'string' and not isinstance(value, str):
                    return False, f"Parameter {param} must be string"
                elif expected_type == 'int' and not isinstance(value, int):
                    return False, f"Parameter {param} must be int"
                elif expected_type == 'float' and not isinstance(value, (int, float)):
                    return False, f"Parameter {param} must be float"
                elif expected_type == 'bool' and not isinstance(value, bool):
                    return False, f"Parameter {param} must be bool"

        return True, None

    @abstractmethod
    def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """
        Execute the plugin

        Args:
            input_data: Input data (type depends on plugin type)
            context: Execution context (metadata, settings, etc.)

        Returns:
            Processed output (type depends on plugin type)
        """
        pass


class PreprocessorPlugin(BasePlugin):
    """
    Image preprocessing plugin

    Input: PIL Image or numpy array
    Output: Processed PIL Image or numpy array
    """

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.PREPROCESSOR

    @abstractmethod
    def process_image(self, image: Any, context: Dict[str, Any]) -> Any:
        """
        Process image before OCR

        Args:
            image: PIL Image or numpy array
            context: Processing context

        Returns:
            Processed image
        """
        pass

    def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute preprocessing"""
        return self.process_image(input_data, context)


class OCREnginePlugin(BasePlugin):
    """
    Custom OCR engine plugin

    Input: PIL Image or numpy array
    Output: OCR result dict with 'text' and optional 'boxes', 'confidence'
    """

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.OCR_ENGINE

    @abstractmethod
    def recognize_text(self, image: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform OCR on image

        Args:
            image: PIL Image or numpy array
            context: OCR context (language, etc.)

        Returns:
            {
                'text': str,
                'boxes': List[bbox],  # Optional
                'confidence': float,   # Optional
                'words': List[dict]    # Optional
            }
        """
        pass

    def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute OCR"""
        return self.recognize_text(input_data, context)


class PostprocessorPlugin(BasePlugin):
    """
    Text postprocessing plugin

    Input: OCR text (string)
    Output: Processed text (string)
    """

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.POSTPROCESSOR

    @abstractmethod
    def process_text(self, text: str, context: Dict[str, Any]) -> str:
        """
        Process OCR text

        Args:
            text: Raw OCR text
            context: Processing context

        Returns:
            Processed text
        """
        pass

    def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute postprocessing"""
        return self.process_text(input_data, context)


class ExporterPlugin(BasePlugin):
    """
    Custom export format plugin

    Input: Document data
    Output: Export result (file path or content)
    """

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.EXPORTER

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Export format name (e.g., 'docx', 'latex')"""
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension (e.g., '.docx', '.tex')"""
        pass

    @abstractmethod
    def export(self, document: Dict[str, Any], output_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export document to custom format

        Args:
            document: Document data (title, content, metadata, etc.)
            output_path: Output file path
            context: Export context

        Returns:
            {
                'success': bool,
                'output_path': str,
                'message': str
            }
        """
        pass

    def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute export"""
        document = input_data
        output_path = context.get('output_path')
        return self.export(document, output_path, context)


class AnalyzerPlugin(BasePlugin):
    """
    Custom analysis/extraction plugin

    Input: Text or document data
    Output: Analysis results
    """

    @property
    def plugin_type(self) -> PluginType:
        return PluginType.ANALYZER

    @abstractmethod
    def analyze(self, data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze document or text

        Args:
            data: Input data (text, document, etc.)
            context: Analysis context

        Returns:
            Analysis results (format depends on analyzer)
        """
        pass

    def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute analysis"""
        return self.analyze(input_data, context)


class PluginError(Exception):
    """Base exception for plugin errors"""
    pass


class PluginLoadError(PluginError):
    """Raised when plugin fails to load"""
    pass


class PluginExecutionError(PluginError):
    """Raised when plugin execution fails"""
    pass


class PluginConfigError(PluginError):
    """Raised when plugin configuration is invalid"""
    pass
