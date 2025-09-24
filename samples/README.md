# Sample Images Directory

This directory contains sample images for testing the photo watermark tool.

## Recommended test image names:
- `test_photo_1.jpg` - A typical photo with EXIF data
- `test_photo_2.jpeg` - Another photo format variant
- `landscape.jpg` - Wide landscape photo
- `portrait.jpg` - Portrait orientation photo
- `no_exif.png` - Image without EXIF data (for testing error handling)

## Image requirements:
- Formats: JPG, JPEG, PNG, TIFF (formats that can contain EXIF data)
- Size: Any size, but recommended 800x600 or larger for visible watermarks
- EXIF data: Include photos with actual EXIF date information for best testing

## Usage:
```bash
# Test single image
python src/main.py samples/test_photo_1.jpg

# Test entire directory
python src/main.py samples/

# Test with custom options
python src/main.py samples/test_photo_1.jpg --font-size 48 --color red --position center
```

## Output:
Watermarked images will be saved to `samples_watermark/` directory.