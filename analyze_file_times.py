#!/usr/bin/env python3
"""
验证Windows文件属性显示的时间信息
"""

import sys
sys.path.append('.')

import os
from pathlib import Path
from datetime import datetime

def analyze_file_times(file_path: Path):
    """分析文件的各种时间信息"""
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return

    print(f"=== 文件时间分析: {file_path.name} ===")

    try:
        stat = file_path.stat()

        # 获取各种时间戳
        creation_time = datetime.fromtimestamp(stat.st_ctime)
        modification_time = datetime.fromtimestamp(stat.st_mtime)
        access_time = datetime.fromtimestamp(stat.st_atime)

        print(f"文件大小: {stat.st_size:,} 字节")
        print(f"创建时间: {creation_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"修改时间: {modification_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"访问时间: {access_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Windows特有的时间信息 (如果可用)
        try:
            import win32file
            import win32api
            import pywintypes

            handle = win32file.CreateFile(
                str(file_path),
                win32file.GENERIC_READ,
                win32file.FILE_SHARE_READ,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )

            creation, access, write = win32file.GetFileTime(handle)
            win32file.CloseHandle(handle)

            print("\nWindows详细时间信息:")
            print(f"Windows创建时间: {creation}")
            print(f"Windows访问时间: {access}")
            print(f"Windows写入时间: {write}")

        except ImportError:
            print("\nWindows API不可用 (需要 pywin32)")
        except Exception as e:
            print(f"\nWindows API错误: {e}")

    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    file_path = Path("samples/test_photo_1.jpg")
    analyze_file_times(file_path)