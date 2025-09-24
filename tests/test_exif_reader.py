"""
Unit tests for EXIF reader module
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import tempfile
import os

from src.exif_reader.exif_reader import ExifReader


class TestExifReader:
    """Test cases for ExifReader class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.exif_reader = ExifReader()

    def test_init_with_logger(self):
        """Test initialization with custom logger"""
        mock_logger = Mock()
        reader = ExifReader(mock_logger)
        assert reader.logger == mock_logger

    def test_init_without_logger(self):
        """Test initialization without custom logger"""
        reader = ExifReader()
        assert reader.logger is not None

    @patch('src.exif_reader.exif_reader.Image', None)
    @patch('src.exif_reader.exif_reader.exifread', None)
    def test_init_no_dependencies(self):
        """Test initialization fails when no dependencies available"""
        with pytest.raises(ImportError):
            ExifReader()

    def test_parse_date_string_exif_format(self):
        """Test parsing EXIF date format"""
        date_str = "2023:12:25 14:30:45"
        result = self.exif_reader._parse_date_string(date_str)
        assert result == "2023-12-25"

    def test_parse_date_string_standard_format(self):
        """Test parsing standard date format"""
        date_str = "2023-12-25"
        result = self.exif_reader._parse_date_string(date_str)
        assert result == "2023-12-25"

    def test_parse_date_string_invalid(self):
        """Test parsing invalid date string"""
        date_str = "invalid_date"
        result = self.exif_reader._parse_date_string(date_str)
        assert result is None

    def test_parse_date_string_empty(self):
        """Test parsing empty date string"""
        result = self.exif_reader._parse_date_string("")
        assert result is None

    def test_get_supported_formats(self):
        """Test getting supported file formats"""
        formats = self.exif_reader.get_supported_formats()
        assert isinstance(formats, list)
        assert '.jpg' in formats or '.jpeg' in formats

    def test_is_supported_format(self):
        """Test checking if file format is supported"""
        jpg_path = Path("test.jpg")
        txt_path = Path("test.txt")

        assert self.exif_reader.is_supported_format(jpg_path) is True
        assert self.exif_reader.is_supported_format(txt_path) is False

    @patch('src.exif_reader.exif_reader.Image')
    def test_get_date_with_pil_success(self, mock_image):
        """Test successful date extraction with PIL"""
        # Mock PIL image and EXIF data
        mock_img = Mock()
        mock_img.getexif.return_value = {36867: "2023:12:25 14:30:45"}
        mock_image.open.return_value.__enter__.return_value = mock_img

        test_path = Path("test.jpg")
        result = self.exif_reader._get_date_with_pil(test_path)
        assert result == "2023-12-25"

    @patch('src.exif_reader.exif_reader.Image')
    def test_get_date_with_pil_no_exif(self, mock_image):
        """Test PIL date extraction with no EXIF data"""
        mock_img = Mock()
        mock_img.getexif.return_value = {}
        mock_image.open.return_value.__enter__.return_value = mock_img

        test_path = Path("test.jpg")
        result = self.exif_reader._get_date_with_pil(test_path)
        assert result is None

    def test_get_date_taken_file_not_exists(self):
        """Test get_date_taken with non-existent file"""
        non_existent_path = Path("non_existent.jpg")
        result = self.exif_reader.get_date_taken(non_existent_path)
        assert result is None

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('src.exif_reader.exif_reader.ExifReader._get_date_with_pil')
    def test_get_date_taken_success(self, mock_pil, mock_is_file, mock_exists):
        """Test successful date extraction"""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_pil.return_value = "2023-12-25"

        test_path = Path("test.jpg")
        result = self.exif_reader.get_date_taken(test_path)
        assert result == "2023-12-25"


@pytest.fixture
def temp_image_file():
    """Create a temporary image file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        # Create a minimal JPEG file
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00')
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        os.unlink(temp_path)


class TestExifReaderIntegration:
    """Integration tests for ExifReader"""

    def test_real_file_processing(self, temp_image_file):
        """Test processing a real file (may not have EXIF data)"""
        reader = ExifReader()
        result = reader.get_date_taken(temp_image_file)
        # Result can be None for files without EXIF data, which is expected
        assert result is None or isinstance(result, str)