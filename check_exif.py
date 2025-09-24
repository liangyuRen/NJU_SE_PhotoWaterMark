#!/usr/bin/env python3
"""
EXIF 信息检查和图片处理测试脚本
"""

import sys
sys.path.append('.')

from pathlib import Path
from src.exif_reader.exif_reader import ExifReader
from src.utils.logger import setup_logger
from PIL import Image
from PIL.ExifTags import TAGS
import os
from datetime import datetime

def check_exif_info(image_path: Path):
    """详细检查图片的EXIF信息"""
    print(f"\n=== 检查图片: {image_path.name} ===")

    if not image_path.exists():
        print("文件不存在")
        return

    try:
        # 使用PIL读取EXIF信息
        with Image.open(image_path) as img:
            print(f"图片尺寸: {img.size}")
            print(f"图片模式: {img.mode}")
            print(f"图片格式: {img.format}")

            exifdata = img.getexif()
            if exifdata:
                print("EXIF 标签:")
                for tag_id, value in exifdata.items():
                    tag = TAGS.get(tag_id, tag_id)
                    print(f"   {tag}: {value}")

                # 检查常见的日期标签
                date_tags = {
                    36867: "DateTimeOriginal",
                    36868: "DateTimeDigitized",
                    306: "DateTime"
                }

                print("\n日期信息检查:")
                found_date = False
                for tag_id, tag_name in date_tags.items():
                    if tag_id in exifdata:
                        print(f"   {tag_name}: {exifdata[tag_id]}")
                        found_date = True

                if not found_date:
                    print("   未找到日期信息")

            else:
                print("没有EXIF数据")

    except Exception as e:
        print(f"读取EXIF失败: {e}")

    # 使用项目的ExifReader检查
    try:
        reader = ExifReader()
        date = reader.get_date_taken(image_path)
        print(f"\nExifReader结果: {date}")
    except Exception as e:
        print(f"ExifReader失败: {e}")

    # 获取文件修改日期作为备选方案
    try:
        file_mtime = os.path.getmtime(image_path)
        file_date = datetime.fromtimestamp(file_mtime).strftime("%Y-%m-%d")
        print(f"文件修改日期: {file_date}")
    except Exception as e:
        print(f"获取文件日期失败: {e}")

def main():
    """主函数"""
    print("EXIF信息检查工具")
    print("=" * 50)

    samples_dir = Path("samples")
    if not samples_dir.exists():
        print("samples目录不存在")
        return

    # 查找所有图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp']
    image_files = []

    for file_path in samples_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)

    if not image_files:
        print("在samples目录中未找到图片文件")
        return

    print(f"找到 {len(image_files)} 个图片文件")

    for image_path in image_files:
        check_exif_info(image_path)

if __name__ == "__main__":
    main()