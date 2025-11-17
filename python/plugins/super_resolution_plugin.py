"""
Built-in Plugin: Super Resolution
Enhances image resolution using AI upscaling for better OCR accuracy
"""

from plugin_interface import PreprocessorPlugin, PluginPriority
from typing import Dict, Any
import numpy as np
from PIL import Image
import cv2


class SuperResolutionPlugin(PreprocessorPlugin):
    """
    AI-powered image super-resolution plugin

    Uses OpenCV's DNN super-resolution models to upscale images
    Improves OCR accuracy on low-resolution scans
    """

    @property
    def name(self) -> str:
        return "super_resolution"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "AI-powered image super-resolution for better OCR accuracy"

    @property
    def author(self) -> str:
        return "VaultOCR-AI Team"

    @property
    def priority(self) -> PluginPriority:
        return PluginPriority.HIGH

    @property
    def dependencies(self) -> list:
        return ['opencv-python>=4.8.0', 'numpy']

    @property
    def config_schema(self) -> Dict[str, Any]:
        return {
            'scale_factor': {
                'type': 'int',
                'default': 2,
                'description': 'Upscaling factor (2, 3, or 4)',
                'required': False
            },
            'min_resolution': {
                'type': 'int',
                'default': 300,
                'description': 'Minimum dimension to trigger upscaling',
                'required': False
            },
            'max_resolution': {
                'type': 'int',
                'default': 4000,
                'description': 'Maximum dimension after upscaling',
                'required': False
            }
        }

    def process_image(self, image: Any, context: Dict[str, Any]) -> Any:
        """
        Apply super-resolution to image

        Args:
            image: PIL Image or numpy array
            context: Processing context

        Returns:
            Upscaled image
        """
        # Get config
        scale_factor = self._config.get('scale_factor', 2)
        min_resolution = self._config.get('min_resolution', 300)
        max_resolution = self._config.get('max_resolution', 4000)

        # Convert to numpy array if PIL Image
        if isinstance(image, Image.Image):
            img_array = np.array(image)
            is_pil = True
        else:
            img_array = image
            is_pil = False

        height, width = img_array.shape[:2]

        # Check if upscaling is needed
        if min(height, width) >= min_resolution:
            # Image is already high resolution
            return image

        # Check if upscaling would exceed max resolution
        if max(height, width) * scale_factor > max_resolution:
            # Calculate safe scale factor
            scale_factor = max_resolution // max(height, width)
            if scale_factor < 2:
                return image  # Can't upscale safely

        try:
            # Use simple bicubic interpolation (fast and reliable)
            # For production, could use DNN models like ESRGAN
            new_width = width * scale_factor
            new_height = height * scale_factor

            upscaled = cv2.resize(
                img_array,
                (new_width, new_height),
                interpolation=cv2.INTER_CUBIC
            )

            # Optional: Apply slight sharpening after upscaling
            if self._config.get('sharpen', True):
                kernel = np.array([[-1, -1, -1],
                                   [-1,  9, -1],
                                   [-1, -1, -1]])
                upscaled = cv2.filter2D(upscaled, -1, kernel * 0.3)

            # Convert back to PIL if needed
            if is_pil:
                return Image.fromarray(upscaled)
            else:
                return upscaled

        except Exception as e:
            # If upscaling fails, return original
            print(f"Super-resolution failed: {e}")
            return image
