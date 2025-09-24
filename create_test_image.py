#!/usr/bin/env python3
"""
生成带有EXIF拍摄时间的测试图片
"""

import sys
sys.path.append('.')

from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import piexif
from datetime import datetime
from pathlib import Path
import os

def create_test_image_with_exif():
    """创建一个带有EXIF拍摄时间的测试图片"""

    # 创建一个简单的测试图片
    width, height = 1200, 800
    image = Image.new('RGB', (width, height), color='lightblue')

    # 在图片上绘制一些内容
    draw = ImageDraw.Draw(image)

    # 尝试加载字体
    try:
        font_large = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 48)
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 绘制文字
    draw.text((50, 50), "测试图片 - Test Image", font=font_large, fill='navy')
    draw.text((50, 120), "包含EXIF拍摄时间信息", font=font_small, fill='darkblue')
    draw.text((50, 160), "With EXIF DateTime Information", font=font_small, fill='darkblue')

    # 绘制一个简单的图形
    draw.rectangle([50, 250, 350, 450], outline='red', width=3)
    draw.ellipse([400, 250, 700, 550], outline='green', width=3)
    draw.line([50, 600, 700, 600], fill='purple', width=5)

    # 添加拍摄时间信息
    current_time = datetime.now()
    test_datetime = "2023:08:15 14:30:45"  # 设置一个测试拍摄时间

    draw.text((50, 650), f"模拟拍摄时间: {test_datetime}", font=font_small, fill='black')
    draw.text((50, 680), f"生成时间: {current_time.strftime('%Y:%m:%d %H:%M:%S')}", font=font_small, fill='gray')

    # 创建EXIF数据
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Make: "TestCamera",
            piexif.ImageIFD.Model: "TestModel",
            piexif.ImageIFD.Software: "Python PIL + piexif",
            piexif.ImageIFD.DateTime: current_time.strftime("%Y:%m:%d %H:%M:%S"),
            piexif.ImageIFD.XResolution: (72, 1),
            piexif.ImageIFD.YResolution: (72, 1),
            piexif.ImageIFD.ResolutionUnit: 2,
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: test_datetime,  # 原始拍摄时间
            piexif.ExifIFD.DateTimeDigitized: test_datetime,  # 数字化时间
            piexif.ExifIFD.ExifVersion: b"0231",
            piexif.ExifIFD.ComponentsConfiguration: b"\\x01\\x02\\x03\\x00",
            piexif.ExifIFD.FlashpixVersion: b"0100",
            piexif.ExifIFD.ColorSpace: 1,
            piexif.ExifIFD.PixelXDimension: width,
            piexif.ExifIFD.PixelYDimension: height,
        },
        "GPS": {},
        "1st": {},
        "thumbnail": None
    }

    # 转换为EXIF字节
    exif_bytes = piexif.dump(exif_dict)

    # 保存图片
    output_path = Path("samples/test_photo_with_exif.jpg")
    image.save(output_path, "JPEG", exif=exif_bytes, quality=95)

    print(f"成功创建带EXIF的测试图片: {output_path}")
    print(f"设置的拍摄时间: {test_datetime}")
    print(f"文件大小: {output_path.stat().st_size:,} 字节")

    return output_path

if __name__ == "__main__":
    try:
        # 检查是否安装了piexif
        import piexif
        print("piexif库已可用")
    except ImportError:
        print("需要安装piexif库")
        print("请运行: pip install piexif")
        sys.exit(1)

    create_test_image_with_exif()