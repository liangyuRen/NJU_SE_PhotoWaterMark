"""
EXIF data reader module
Handles reading and parsing EXIF metadata from image files
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import logging

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    Image = None
    TAGS = None

try:
    import exifread
except ImportError:
    exifread = None


class ExifReader:
    """Class to read EXIF data from image files"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required libraries are available"""
        if Image is None and exifread is None:
            raise ImportError("Either Pillow or exifread library is required")

    def get_original_timestamp(self, image_path: Path) -> Optional[dict]:
        """
        Extract original timestamp information from image EXIF data

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing timestamp information or None if not found
        """
        if not image_path.exists() or not image_path.is_file():
            self.logger.error(f"Image file not found: {image_path}")
            return None

        timestamp_info = {
            "file_path": str(image_path),
            "exif_found": False,
            "datetime_original": None,
            "datetime_digitized": None,
            "datetime_modified": None,
            "file_modification_time": None,
            "source": None
        }

        # Try PIL first
        if Image is not None:
            exif_data = self._get_full_exif_with_pil(image_path)
            if exif_data:
                timestamp_info.update(exif_data)

        # Try exifread as fallback
        if not timestamp_info["exif_found"] and exifread is not None:
            exif_data = self._get_full_exif_with_exifread(image_path)
            if exif_data:
                timestamp_info.update(exif_data)

        # Always get file modification time as fallback
        try:
            import os
            from datetime import datetime
            file_mtime = os.path.getmtime(image_path)
            timestamp_info["file_modification_time"] = datetime.fromtimestamp(file_mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            self.logger.error(f"Error getting file modification time for {image_path.name}: {e}")

        return timestamp_info

    def get_date_taken(self, image_path: Path, use_fallback: bool = True) -> Optional[str]:
        """
        Extract date taken from image EXIF data

        Args:
            image_path: Path to the image file
            use_fallback: If True, use file modification date when EXIF date is not available

        Returns:
            Date string in format "YYYY-MM-DD" or None if not found and no fallback
        """
        if not image_path.exists() or not image_path.is_file():
            self.logger.error(f"Image file not found: {image_path}")
            return None

        # Try PIL first
        if Image is not None:
            date = self._get_date_with_pil(image_path)
            if date:
                return date

        # Try exifread as fallback
        if exifread is not None:
            date = self._get_date_with_exifread(image_path)
            if date:
                return date

        # Use fallback date if enabled
        if use_fallback:
            fallback_date = self._get_fallback_date(image_path)
            if fallback_date:
                self.logger.info(f"Using fallback date for {image_path.name}: {fallback_date}")
                return fallback_date

        self.logger.warning(f"No date information found in EXIF data: {image_path.name}")
        return None

    def _get_date_with_pil(self, image_path: Path) -> Optional[str]:
        """Get date using PIL/Pillow"""
        try:
            with Image.open(image_path) as image:
                exifdata = image.getexif()

                if not exifdata:
                    return None

                # First try to get DateTimeOriginal and DateTimeDigitized from Exif IFD
                try:
                    exif_ifd = exifdata.get_ifd(0x8769)  # Exif IFD
                    if exif_ifd:
                        # Priority order: DateTimeOriginal, DateTimeDigitized
                        for tag_id in [36867, 36868]:  # DateTimeOriginal, DateTimeDigitized
                            if tag_id in exif_ifd:
                                date_str = exif_ifd[tag_id]
                                parsed_date = self._parse_date_string(date_str)
                                if parsed_date:
                                    return parsed_date
                except Exception as e:
                    self.logger.debug(f"Could not access Exif IFD: {e}")

                # Fallback to main EXIF data
                date_tags = [36867, 36868, 306]  # DateTimeOriginal, DateTimeDigitized, DateTime
                for tag_id in date_tags:
                    if tag_id in exifdata:
                        date_str = exifdata[tag_id]
                        parsed_date = self._parse_date_string(date_str)
                        if parsed_date:
                            return parsed_date

        except Exception as e:
            self.logger.error(f"Error reading EXIF with PIL from {image_path.name}: {e}")

        return None

    def _get_date_with_exifread(self, image_path: Path) -> Optional[str]:
        """Get date using exifread library"""
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, stop_tag='DateTimeOriginal')

                # Try different date tags
                date_tags = [
                    'EXIF DateTimeOriginal',
                    'EXIF DateTimeDigitized',
                    'Image DateTime'
                ]

                for tag_name in date_tags:
                    if tag_name in tags:
                        date_str = str(tags[tag_name])
                        return self._parse_date_string(date_str)

        except Exception as e:
            self.logger.error(f"Error reading EXIF with exifread from {image_path.name}: {e}")

        return None

    def _get_full_exif_with_pil(self, image_path: Path) -> Optional[dict]:
        """Get full EXIF timestamp information using PIL/Pillow"""
        try:
            with Image.open(image_path) as image:
                exifdata = image.getexif()

                if not exifdata:
                    return None

                timestamp_info = {
                    "exif_found": True,
                    "source": "PIL"
                }

                # Common date tags to check in main EXIF data
                main_date_tags = {
                    306: "datetime_modified"        # DateTime
                }

                for tag_id, field_name in main_date_tags.items():
                    if tag_id in exifdata:
                        timestamp_info[field_name] = str(exifdata[tag_id])

                # Try to get Exif sub-IFD data for DateTimeOriginal and DateTimeDigitized
                try:
                    exif_ifd = exifdata.get_ifd(0x8769)  # Exif IFD
                    if exif_ifd:
                        exif_date_tags = {
                            36867: "datetime_original",     # DateTimeOriginal
                            36868: "datetime_digitized"     # DateTimeDigitized
                        }

                        for tag_id, field_name in exif_date_tags.items():
                            if tag_id in exif_ifd:
                                timestamp_info[field_name] = str(exif_ifd[tag_id])
                except Exception as e:
                    self.logger.debug(f"Could not access Exif IFD: {e}")
                    # Fallback: try to access through the main exifdata
                    for tag_id, field_name in [(36867, "datetime_original"), (36868, "datetime_digitized")]:
                        if tag_id in exifdata:
                            timestamp_info[field_name] = str(exifdata[tag_id])

                return timestamp_info if any(v for k, v in timestamp_info.items() if k.startswith('datetime_')) else None

        except Exception as e:
            self.logger.error(f"Error reading full EXIF with PIL from {image_path.name}: {e}")

        return None

    def _get_full_exif_with_exifread(self, image_path: Path) -> Optional[dict]:
        """Get full EXIF timestamp information using exifread library"""
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f)

                if not tags:
                    return None

                timestamp_info = {
                    "exif_found": True,
                    "source": "exifread"
                }

                # Try different date tags
                date_tag_mappings = {
                    'EXIF DateTimeOriginal': "datetime_original",
                    'EXIF DateTimeDigitized': "datetime_digitized",
                    'Image DateTime': "datetime_modified"
                }

                for tag_name, field_name in date_tag_mappings.items():
                    if tag_name in tags:
                        timestamp_info[field_name] = str(tags[tag_name])

                return timestamp_info

        except Exception as e:
            self.logger.error(f"Error reading full EXIF with exifread from {image_path.name}: {e}")

        return None

    def _parse_date_string(self, date_str: str) -> Optional[str]:
        """
        Parse date string from EXIF and convert to YYYY-MM-DD format

        Args:
            date_str: Date string from EXIF (typically "YYYY:MM:DD HH:MM:SS")

        Returns:
            Date string in format "YYYY-MM-DD" or None if parsing fails
        """
        if not date_str:
            return None

        try:
            # Common EXIF date format: "YYYY:MM:DD HH:MM:SS"
            if ':' in date_str and ' ' in date_str:
                date_part = date_str.split(' ')[0]
                date_obj = datetime.strptime(date_part, "%Y:%m:%d")
                return date_obj.strftime("%Y-%m-%d")

            # Try other common formats
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"]:
                try:
                    date_obj = datetime.strptime(date_str[:10], fmt)
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing date string '{date_str}': {e}")

        return None

    def _get_fallback_date(self, image_path: Path) -> Optional[str]:
        """
        Get fallback date from file modification time

        Args:
            image_path: Path to the image file

        Returns:
            Date string in format "YYYY-MM-DD" or None if failed
        """
        try:
            import os
            from datetime import datetime

            file_mtime = os.path.getmtime(image_path)
            file_date = datetime.fromtimestamp(file_mtime).strftime("%Y-%m-%d")
            return file_date
        except Exception as e:
            self.logger.error(f"Error getting fallback date for {image_path.name}: {e}")
            return None

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported image formats

        Returns:
            List of file extensions (with dots)
        """
        if Image is not None:
            # Get formats supported by PIL
            formats = []
            for ext, format_name in Image.registered_extensions().items():
                if ext.lower() in ['.jpg', '.jpeg', '.tiff', '.tif']:
                    formats.append(ext.lower())
            return formats
        else:
            # Default supported formats
            return ['.jpg', '.jpeg', '.tiff', '.tif']

    def is_supported_format(self, file_path: Path) -> bool:
        """
        Check if file format is supported for EXIF reading

        Args:
            file_path: Path to the image file

        Returns:
            True if format is supported, False otherwise
        """
        return file_path.suffix.lower() in self.get_supported_formats()