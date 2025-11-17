"""
Built-in Plugin: Adaptive Binarization
Advanced binarization using adaptive thresholding for challenging documents
"""

from plugin_interface import PreprocessorPlugin, PluginPriority
from typing import Dict, Any
import numpy as np
from PIL import Image
import cv2


class AdaptiveBinarizationPlugin(PreprocessorPlugin):
    """
    Adaptive binarization plugin

    Uses adaptive thresholding algorithms (Otsu, Sauvola, etc.)
    Handles varying lighting conditions, shadows, and faded text
    """

    @property
    def name(self) -> str:
        return "adaptive_binarization"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Adaptive binarization for challenging documents with uneven lighting"

    @property
    def author(self) -> str:
        return "VaultOCR-AI Team"

    @property
    def priority(self) -> PluginPriority:
        return PluginPriority.NORMAL

    @property
    def dependencies(self) -> list:
        return ['opencv-python>=4.8.0', 'numpy']

    @property
    def config_schema(self) -> Dict[str, Any]:
        return {
            'method': {
                'type': 'string',
                'default': 'adaptive_gaussian',
                'description': 'Binarization method (adaptive_gaussian, adaptive_mean, otsu, sauvola)',
                'required': False
            },
            'block_size': {
                'type': 'int',
                'default': 11,
                'description': 'Block size for adaptive threshold (must be odd)',
                'required': False
            },
            'c_value': {
                'type': 'int',
                'default': 2,
                'description': 'Constant subtracted from weighted mean',
                'required': False
            },
            'denoise_first': {
                'type': 'bool',
                'default': True,
                'description': 'Apply denoising before binarization',
                'required': False
            }
        }

    def process_image(self, image: Any, context: Dict[str, Any]) -> Any:
        """
        Apply adaptive binarization to image

        Args:
            image: PIL Image or numpy array
            context: Processing context

        Returns:
            Binarized image
        """
        # Get config
        method = self._config.get('method', 'adaptive_gaussian')
        block_size = self._config.get('block_size', 11)
        c_value = self._config.get('c_value', 2)
        denoise_first = self._config.get('denoise_first', True)

        # Ensure block size is odd
        if block_size % 2 == 0:
            block_size += 1

        # Convert to numpy array if PIL Image
        if isinstance(image, Image.Image):
            img_array = np.array(image)
            is_pil = True
        else:
            img_array = image
            is_pil = False

        try:
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array.copy()

            # Optional denoising
            if denoise_first:
                gray = cv2.fastNlMeansDenoising(gray, h=10)

            # Apply binarization based on method
            if method == 'adaptive_gaussian':
                binary = cv2.adaptiveThreshold(
                    gray,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    block_size,
                    c_value
                )
            elif method == 'adaptive_mean':
                binary = cv2.adaptiveThreshold(
                    gray,
                    255,
                    cv2.ADAPTIVE_THRESH_MEAN_C,
                    cv2.THRESH_BINARY,
                    block_size,
                    c_value
                )
            elif method == 'otsu':
                # Otsu's binarization
                _, binary = cv2.threshold(
                    gray,
                    0,
                    255,
                    cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
            elif method == 'sauvola':
                # Sauvola's binarization (approximate)
                binary = self._sauvola_threshold(gray, window_size=block_size)
            else:
                # Fallback to adaptive gaussian
                binary = cv2.adaptiveThreshold(
                    gray,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    block_size,
                    c_value
                )

            # Optional: morphological operations to clean up
            if self._config.get('cleanup', True):
                # Remove small noise
                kernel = np.ones((2, 2), np.uint8)
                binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
                binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

            # Convert back to PIL if needed
            if is_pil:
                return Image.fromarray(binary)
            else:
                return binary

        except Exception as e:
            print(f"Adaptive binarization failed: {e}")
            return image

    def _sauvola_threshold(self, image: np.ndarray, window_size: int = 15, k: float = 0.2, r: float = 128) -> np.ndarray:
        """
        Sauvola's adaptive thresholding

        Args:
            image: Grayscale image
            window_size: Local window size
            k: Parameter controlling threshold
            r: Dynamic range of standard deviation

        Returns:
            Binary image
        """
        # Calculate local mean
        mean = cv2.blur(image.astype(np.float32), (window_size, window_size))

        # Calculate local standard deviation
        mean_sq = cv2.blur((image.astype(np.float32) ** 2), (window_size, window_size))
        std = np.sqrt(mean_sq - mean ** 2)

        # Sauvola threshold
        threshold = mean * (1 + k * ((std / r) - 1))

        # Apply threshold
        binary = np.where(image > threshold, 255, 0).astype(np.uint8)

        return binary
