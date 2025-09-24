"""
Watermark processor module
Handles adding watermarks to images
"""

import os
from pathlib import Path
from typing import Tuple, List, Optional
import logging

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None

from src.exif_reader.exif_reader import ExifReader
from src.utils.config import WatermarkConfig


class WatermarkProcessor:
    """Main class for processing watermarks on images"""

    def __init__(self, config: WatermarkConfig, logger: Optional[logging.Logger] = None,
                 show_watermark_info: bool = False):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.exif_reader = ExifReader(logger)
        self.show_watermark_info = show_watermark_info

        if Image is None:
            raise ImportError("Pillow library is required for image processing")

    def process_single_image(self, image_path: Path) -> bool:
        """
        Process a single image file

        Args:
            image_path: Path to the image file

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            self.logger.info(f"Processing image: {image_path.name}")

            # Check if format is supported
            if not self._is_supported_image_format(image_path):
                self.logger.warning(f"Unsupported image format: {image_path.name}")
                return False

            # Get timestamp information for display (if showing watermark info)
            if self.show_watermark_info:
                self._current_timestamp_info = self.exif_reader.get_original_timestamp(image_path)

            # Get date from EXIF
            date_str = self.exif_reader.get_date_taken(image_path)
            if not date_str:
                self.logger.warning(f"No date information found for: {image_path.name}")
                return False

            # Add watermark
            success = self._add_watermark_to_image(image_path, date_str)
            if success:
                self.logger.info(f"Successfully processed: {image_path.name}")
            else:
                self.logger.error(f"Failed to process: {image_path.name}")

            return success

        except Exception as e:
            self.logger.error(f"Error processing {image_path.name}: {e}")
            return False

    def process_directory(self, directory_path: Path) -> Tuple[int, int]:
        """
        Process all images in a directory

        Args:
            directory_path: Path to the directory

        Returns:
            Tuple of (success_count, total_count)
        """
        image_files = self._find_image_files(directory_path)
        total_count = len(image_files)

        if total_count == 0:
            self.logger.warning(f"No supported image files found in: {directory_path}")
            return 0, 0

        self.logger.info(f"Found {total_count} image files to process")

        success_count = 0
        for image_path in image_files:
            if self.process_single_image(image_path):
                success_count += 1

        return success_count, total_count

    def _add_watermark_to_image(self, image_path: Path, date_str: str) -> bool:
        """
        Add watermark to an image

        Args:
            image_path: Path to the source image
            date_str: Date string to use as watermark

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create output directory
            output_dir = self._create_output_directory(image_path)
            if not output_dir:
                return False

            # Open and process image
            with Image.open(image_path) as image:
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')

                # Create a copy for watermarking
                watermarked_image = image.copy()

                # Add watermark
                self._draw_watermark(watermarked_image, date_str)

                # Save the watermarked image
                output_path = output_dir / image_path.name
                watermarked_image.save(
                    output_path,
                    quality=self.config.output_quality,
                    optimize=True
                )

                return True

        except Exception as e:
            self.logger.error(f"Error adding watermark to {image_path.name}: {e}")
            return False

    def _draw_watermark(self, image: Image.Image, text: str):
        """
        Draw watermark text on image

        Args:
            image: PIL Image object
            text: Text to draw as watermark
        """
        draw = ImageDraw.Draw(image)

        # Try to load a font
        font = self._get_font()
        font_info = self._get_font_info(font)

        # Get text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position
        position = self._calculate_text_position(
            image.size, (text_width, text_height)
        )

        # Print watermark information
        if self.show_watermark_info:
            self._print_watermark_info(image, text, font_info, position, (text_width, text_height))

        # Draw text with outline for better visibility
        outline_color = "black" if self.config.color.lower() != "black" else "white"

        # Draw outline
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    draw.text(
                        (position[0] + dx, position[1] + dy),
                        text,
                        font=font,
                        fill=outline_color
                    )

        # Draw main text
        draw.text(position, text, font=font, fill=self.config.color)

    def _get_font(self) -> ImageFont.FreeTypeFont:
        """
        Get font for watermark text

        Returns:
            PIL Font object
        """
        try:
            # Try to load system fonts
            font_paths = [
                # Windows fonts
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                # Linux fonts
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                # macOS fonts
                "/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, self.config.font_size)

            # Fallback to default font
            return ImageFont.load_default()

        except Exception as e:
            self.logger.warning(f"Could not load custom font: {e}")
            return ImageFont.load_default()

    def _get_font_info(self, font) -> dict:
        """
        Get font information

        Args:
            font: PIL Font object

        Returns:
            Dictionary containing font information
        """
        font_info = {
            "type": type(font).__name__,
            "size": self.config.font_size,
            "path": "default"
        }

        try:
            if hasattr(font, 'path'):
                font_info["path"] = font.path
            elif hasattr(font, 'font'):
                if hasattr(font.font, 'family'):
                    font_info["path"] = font.font.family
        except Exception:
            pass

        return font_info

    def _print_watermark_info(self, image: Image.Image, text: str, font_info: dict,
                            position: tuple, text_size: tuple):
        """
        Print detailed watermark information

        Args:
            image: PIL Image object
            text: Watermark text
            font_info: Font information dictionary
            position: Text position (x, y)
            text_size: Text size (width, height)
        """
        self.logger.info("=" * 60)
        self.logger.info("Watermark Details")
        self.logger.info("=" * 60)

        # Image information
        self.logger.info(f"Image Info:")
        self.logger.info(f"   Size: {image.size[0]}x{image.size[1]} pixels")
        self.logger.info(f"   Mode: {image.mode}")

        # Original timestamp information
        if hasattr(self, '_current_timestamp_info') and self._current_timestamp_info:
            timestamp_info = self._current_timestamp_info
            self.logger.info(f"Original Photo Timestamps:")
            self.logger.info(f"   EXIF Data Found: {timestamp_info.get('exif_found', 'No')}")
            if timestamp_info.get('exif_found'):
                self.logger.info(f"   Data Source: {timestamp_info.get('source', 'Unknown')}")
                if timestamp_info.get('datetime_original'):
                    self.logger.info(f"   Original Shot Time: {timestamp_info['datetime_original']}")
                if timestamp_info.get('datetime_digitized'):
                    self.logger.info(f"   Digitized Time: {timestamp_info['datetime_digitized']}")
                if timestamp_info.get('datetime_modified'):
                    self.logger.info(f"   Modified Time: {timestamp_info['datetime_modified']}")
            self.logger.info(f"   File Modification: {timestamp_info.get('file_modification_time', 'Unknown')}")

        # Watermark text information
        self.logger.info(f"Watermark Text:")
        self.logger.info(f"   Content: '{text}'")
        self.logger.info(f"   Length: {len(text)} characters")

        # Font information
        self.logger.info(f"Font Info:")
        self.logger.info(f"   Size: {font_info['size']}px")
        self.logger.info(f"   Type: {font_info['type']}")
        self.logger.info(f"   Path: {font_info['path']}")

        # Position information
        self.logger.info(f"Position Info:")
        self.logger.info(f"   Config Position: {self.config.position}")
        self.logger.info(f"   Actual Coordinates: ({position[0]}, {position[1]})")
        self.logger.info(f"   Text Size: {text_size[0]}x{text_size[1]} pixels")

        # Color information
        self.logger.info(f"Color Info:")
        self.logger.info(f"   Main Color: {self.config.color}")
        outline_color = "black" if self.config.color.lower() != "black" else "white"
        self.logger.info(f"   Outline Color: {outline_color}")

        # Output settings
        self.logger.info(f"Output Settings:")
        self.logger.info(f"   Output Quality: {self.config.output_quality}%")

        self.logger.info("=" * 60)

    def _calculate_text_position(self, image_size: Tuple[int, int],
                               text_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        Calculate text position based on configuration

        Args:
            image_size: (width, height) of the image
            text_size: (width, height) of the text

        Returns:
            (x, y) position for the text
        """
        img_width, img_height = image_size
        text_width, text_height = text_size

        margin = 20  # Margin from edges

        position_map = {
            "top-left": (margin, margin),
            "top-right": (img_width - text_width - margin, margin),
            "bottom-left": (margin, img_height - text_height - margin),
            "bottom-right": (img_width - text_width - margin, img_height - text_height - margin),
            "center": ((img_width - text_width) // 2, (img_height - text_height) // 2)
        }

        return position_map.get(self.config.position, position_map["bottom-right"])

    def _create_output_directory(self, image_path: Path) -> Optional[Path]:
        """
        Create output directory for watermarked images

        Args:
            image_path: Path to the source image

        Returns:
            Path to the output directory or None if creation failed
        """
        try:
            parent_dir = image_path.parent
            dir_name = parent_dir.name
            output_dir = parent_dir / f"{dir_name}_watermark"

            output_dir.mkdir(exist_ok=True)
            return output_dir

        except Exception as e:
            self.logger.error(f"Error creating output directory: {e}")
            return None

    def _find_image_files(self, directory_path: Path) -> List[Path]:
        """
        Find all supported image files in directory

        Args:
            directory_path: Directory to search

        Returns:
            List of image file paths
        """
        image_files = []
        supported_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp']

        try:
            for file_path in directory_path.iterdir():
                if (file_path.is_file() and
                    file_path.suffix.lower() in supported_extensions):
                    image_files.append(file_path)

        except Exception as e:
            self.logger.error(f"Error scanning directory {directory_path}: {e}")

        return sorted(image_files)

    def _is_supported_image_format(self, file_path: Path) -> bool:
        """
        Check if image format is supported

        Args:
            file_path: Path to the image file

        Returns:
            True if supported, False otherwise
        """
        supported_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp']
        return file_path.suffix.lower() in supported_extensions