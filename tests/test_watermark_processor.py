"""
Unit tests for watermark processor module
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from src.watermark.watermark_processor import WatermarkProcessor
from src.utils.config import WatermarkConfig


class TestWatermarkProcessor:
    """Test cases for WatermarkProcessor class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = WatermarkConfig()
        self.mock_logger = Mock()
        self.processor = WatermarkProcessor(self.config, self.mock_logger)

    @patch('src.watermark.watermark_processor.Image', None)
    def test_init_no_pillow(self):
        """Test initialization fails without Pillow"""
        with pytest.raises(ImportError):
            WatermarkProcessor(self.config)

    def test_calculate_text_position_bottom_right(self):
        """Test text position calculation for bottom-right"""
        image_size = (800, 600)
        text_size = (100, 30)

        position = self.processor._calculate_text_position(image_size, text_size)
        expected = (800 - 100 - 20, 600 - 30 - 20)  # margin = 20
        assert position == expected

    def test_calculate_text_position_center(self):
        """Test text position calculation for center"""
        self.processor.config.position = "center"
        image_size = (800, 600)
        text_size = (100, 30)

        position = self.processor._calculate_text_position(image_size, text_size)
        expected = ((800 - 100) // 2, (600 - 30) // 2)
        assert position == expected

    def test_calculate_text_position_top_left(self):
        """Test text position calculation for top-left"""
        self.processor.config.position = "top-left"
        image_size = (800, 600)
        text_size = (100, 30)

        position = self.processor._calculate_text_position(image_size, text_size)
        expected = (20, 20)  # margin = 20
        assert position == expected

    def test_is_supported_image_format(self):
        """Test image format support checking"""
        jpg_path = Path("test.jpg")
        png_path = Path("test.png")
        txt_path = Path("test.txt")

        assert self.processor._is_supported_image_format(jpg_path) is True
        assert self.processor._is_supported_image_format(png_path) is True
        assert self.processor._is_supported_image_format(txt_path) is False

    @patch('pathlib.Path.mkdir')
    def test_create_output_directory(self, mock_mkdir):
        """Test output directory creation"""
        image_path = Path("/test/images/photo.jpg")
        mock_mkdir.return_value = None

        result = self.processor._create_output_directory(image_path)
        expected_path = Path("/test/images/images_watermark")

        assert result == expected_path
        mock_mkdir.assert_called_once_with(exist_ok=True)

    @patch('pathlib.Path.iterdir')
    def test_find_image_files(self, mock_iterdir):
        """Test finding image files in directory"""
        # Mock directory contents
        mock_files = [
            Mock(is_file=lambda: True, suffix=".jpg"),
            Mock(is_file=lambda: True, suffix=".png"),
            Mock(is_file=lambda: True, suffix=".txt"),
            Mock(is_file=lambda: False, suffix=".jpg"),  # Not a file
        ]
        mock_iterdir.return_value = mock_files

        directory_path = Path("/test/images")
        result = self.processor._find_image_files(directory_path)

        # Should find 2 image files (.jpg and .png)
        assert len(result) == 2

    @patch('src.watermark.watermark_processor.WatermarkProcessor._is_supported_image_format')
    @patch('src.exif_reader.exif_reader.ExifReader.get_date_taken')
    @patch('src.watermark.watermark_processor.WatermarkProcessor._add_watermark_to_image')
    def test_process_single_image_success(self, mock_add_watermark, mock_get_date, mock_supported):
        """Test successful single image processing"""
        mock_supported.return_value = True
        mock_get_date.return_value = "2023-12-25"
        mock_add_watermark.return_value = True

        image_path = Path("test.jpg")
        result = self.processor.process_single_image(image_path)

        assert result is True
        mock_add_watermark.assert_called_once_with(image_path, "2023-12-25")

    @patch('src.watermark.watermark_processor.WatermarkProcessor._is_supported_image_format')
    def test_process_single_image_unsupported_format(self, mock_supported):
        """Test processing unsupported image format"""
        mock_supported.return_value = False

        image_path = Path("test.txt")
        result = self.processor.process_single_image(image_path)

        assert result is False

    @patch('src.watermark.watermark_processor.WatermarkProcessor._is_supported_image_format')
    @patch('src.exif_reader.exif_reader.ExifReader.get_date_taken')
    def test_process_single_image_no_date(self, mock_get_date, mock_supported):
        """Test processing image with no date information"""
        mock_supported.return_value = True
        mock_get_date.return_value = None

        image_path = Path("test.jpg")
        result = self.processor.process_single_image(image_path)

        assert result is False

    @patch('src.watermark.watermark_processor.WatermarkProcessor._find_image_files')
    @patch('src.watermark.watermark_processor.WatermarkProcessor.process_single_image')
    def test_process_directory(self, mock_process_single, mock_find_files):
        """Test directory processing"""
        # Mock found files
        mock_files = [Path("image1.jpg"), Path("image2.jpg"), Path("image3.jpg")]
        mock_find_files.return_value = mock_files

        # Mock processing results (2 success, 1 failure)
        mock_process_single.side_effect = [True, True, False]

        directory_path = Path("/test/images")
        success_count, total_count = self.processor.process_directory(directory_path)

        assert success_count == 2
        assert total_count == 3
        assert mock_process_single.call_count == 3

    @patch('src.watermark.watermark_processor.WatermarkProcessor._find_image_files')
    def test_process_directory_no_images(self, mock_find_files):
        """Test processing directory with no images"""
        mock_find_files.return_value = []

        directory_path = Path("/test/empty")
        success_count, total_count = self.processor.process_directory(directory_path)

        assert success_count == 0
        assert total_count == 0


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestWatermarkProcessorIntegration:
    """Integration tests for WatermarkProcessor"""

    def test_config_validation(self):
        """Test processor works with valid configuration"""
        config = WatermarkConfig(
            font_size=24,
            color="red",
            position="center",
            output_quality=85
        )
        logger = Mock()

        processor = WatermarkProcessor(config, logger)
        assert processor.config.font_size == 24
        assert processor.config.color == "red"
        assert processor.config.position == "center"
        assert processor.config.output_quality == 85