#!/usr/bin/env python3
"""
================================================================================
照片水印添加工具 - 主程序入口
================================================================================

项目名称：Photo Watermark Tool
课程：南京大学大模型辅助软件工程课程作业1
功能：基于图片EXIF信息中的拍摄时间，为照片批量添加日期水印

主要功能：
1. 解析命令行参数，获取用户输入的图片路径和水印配置
2. 读取图片文件的EXIF信息，提取拍摄日期
3. 根据用户配置（字体大小、颜色、位置）添加日期水印
4. 将带水印的图片保存到指定目录

使用方式：
    python main.py <图片路径> [选项]

示例：
    python main.py ./photos --font-size 24 --color red --position top-left

作者：南京大学学生
日期：2025年
版本：1.0.0
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from src.watermark.watermark_processor import WatermarkProcessor
from src.utils.config import WatermarkConfig
from src.utils.logger import setup_logger


def parse_arguments():
    """
    解析命令行参数

    功能：
        - 创建参数解析器，定义程序接受的所有命令行参数
        - 设置参数的类型、默认值、帮助信息等
        - 验证参数的有效性

    参数说明：
        path: 必需参数，图片文件或包含图片的目录路径
        --font-size: 可选，水印字体大小，默认36
        --color: 可选，水印文字颜色，默认白色
        --position: 可选，水印位置，支持5个位置选择
        --output-quality: 可选，输出图片质量(1-100)，默认95
        --verbose: 可选，启用详细日志输出

    Returns:
        argparse.Namespace: 解析后的参数对象

    异常：
        SystemExit: 当参数解析失败时退出程序
    """
    parser = argparse.ArgumentParser(
        description="Add date watermarks to photos based on EXIF data"
    )

    parser.add_argument(
        "path",
        type=str,
        help="Path to image file or directory containing images"
    )

    parser.add_argument(
        "--font-size",
        type=int,
        default=36,
        help="Font size for watermark text (default: 36)"
    )

    parser.add_argument(
        "--color",
        type=str,
        default="white",
        help="Watermark text color (default: white)"
    )

    parser.add_argument(
        "--position",
        type=str,
        choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
        default="bottom-right",
        help="Watermark position (default: bottom-right)"
    )

    parser.add_argument(
        "--output-quality",
        type=int,
        default=95,
        help="Output image quality (1-100, default: 95)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()

    # Setup logging
    logger = setup_logger(verbose=args.verbose)

    # Validate input path
    input_path = Path(args.path)
    if not input_path.exists():
        logger.error(f"Path does not exist: {input_path}")
        sys.exit(1)

    # Create configuration
    config = WatermarkConfig(
        font_size=args.font_size,
        color=args.color,
        position=args.position,
        output_quality=args.output_quality
    )

    # Process images
    processor = WatermarkProcessor(config, logger)

    try:
        if input_path.is_file():
            success = processor.process_single_image(input_path)
            if not success:
                sys.exit(1)
        else:
            success_count, total_count = processor.process_directory(input_path)
            logger.info(f"Processed {success_count}/{total_count} images successfully")

            if success_count == 0:
                sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()