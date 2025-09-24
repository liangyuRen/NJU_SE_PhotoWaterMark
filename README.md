# 照片水印添加工具 (Photo Watermark Tool)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)]()

基于EXIF拍摄时间为照片批量添加日期水印的命令行工具。

**课程项目**: 南京大学大模型辅助软件工程课程作业1
**开发方式**: Vibe Coding with Claude Code

---

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 基本使用
```bash
# 处理单张图片
python -m src.main samples/test_photo_with_exif.jpg

# 处理整个目录
python -m src.main samples/

# 显示详细水印信息
python -m src.main samples/test_photo_with_exif.jpg --show-watermark-info
```

---

## 📋 命令使用说明

### 基本语法
```bash
python -m src.main <path> [options]
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `path` | string | - | 图片文件路径或目录路径（必需） |
| `--font-size` | int | 36 | 水印字体大小（像素） |
| `--color` | string | white | 水印颜色（支持颜色名或十六进制） |
| `--position` | string | bottom-right | 水印位置 |
| `--output-quality` | int | 95 | 输出图片质量（1-100） |
| `--verbose, -v` | flag | - | 启用详细日志输出 |
| `--show-watermark-info` | flag | - | 显示详细水印信息 |

### 水印位置选项
- `top-left` - 左上角
- `top-right` - 右上角
- `bottom-left` - 左下角
- `bottom-right` - 右下角（默认）
- `center` - 居中

### 颜色选项
- 颜色名称：`white`, `black`, `red`, `blue`, `green`, `yellow` 等
- 十六进制：`#FFFFFF`, `#000000`, `#FF0000` 等

---

## 💡 使用示例

### 1. 基本水印添加
```bash
# 给单张图片添加默认水印（白色、右下角、36px）
python -m src.main samples/test_photo_with_exif.jpg
```

### 2. 批量处理
```bash
# 处理samples目录下的所有图片
python -m src.main samples/ --verbose
```

### 3. 自定义水印样式
```bash
# 红色、居中、60px大字体水印
python -m src.main samples/test_photo_1.jpg --font-size 60 --color red --position center

# 蓝色、左上角、48px水印
python -m src.main samples/test_photo_with_exif.jpg --font-size 48 --color blue --position top-left

# 使用十六进制颜色
python -m src.main samples/test_photo_1.jpg --color "#FF6600" --position center
```

### 4. 详细信息显示
```bash
# 显示完整的EXIF时间戳和水印详情
python -m src.main samples/test_photo_with_exif.jpg --show-watermark-info --verbose
```

### 5. 高质量输出
```bash
# 设置输出质量为85%
python -m src.main samples/ --output-quality 85 --verbose
```

---

## 📁 项目结构

```
NJU_SE_PhotoWaterMark/
├── src/                           # 源代码目录
│   ├── __init__.py               # Python包初始化
│   ├── main.py                   # 程序入口，命令行参数解析
│   ├── watermark/                # 水印处理模块
│   │   ├── __init__.py
│   │   └── watermark_processor.py # 水印添加核心逻辑
│   ├── exif_reader/              # EXIF信息读取模块
│   │   ├── __init__.py
│   │   └── exif_reader.py        # EXIF数据解析和时间提取
│   └── utils/                    # 工具模块
│       ├── __init__.py
│       ├── config.py             # 配置管理（YAML支持）
│       └── logger.py             # 日志系统
├── samples/                      # 测试图片目录
│   ├── README.md                 # 样例图片说明
│   ├── test_photo_1.jpg          # 无EXIF信息的测试图片
│   ├── test_photo_with_exif.jpg  # 带EXIF信息的测试图片
│   └── samples_watermark/        # 输出目录（自动生成）
│       ├── test_photo_1.jpg      # 处理后的带水印图片
│       └── test_photo_with_exif.jpg
├── tests/                        # 单元测试目录
│   ├── test_watermark_processor.py # 水印处理器测试
│   └── test_exif_reader.py       # EXIF读取器测试
├── config/                       # 配置文件目录
│   └── default_config.yaml       # 默认配置文件
├── requirements.txt              # Python依赖列表
├── pyproject.toml               # 项目配置文件
├── SRS.md                       # 软件需求规格说明书
├── requirements_specification.md # 原始需求说明
└── README.md                    # 项目说明文档（本文件）
```

### 目录详细说明

#### 📂 `src/` - 源代码目录
**主要功能**: 包含所有核心代码模块

- **`main.py`**: 程序入口点
  - 命令行参数解析和验证
  - 程序主流程控制
  - 错误处理和日志初始化

- **`watermark/`**: 水印处理模块
  - `watermark_processor.py`: 核心水印添加逻辑
    - 图片加载和处理
    - 字体选择和文字绘制
    - 水印位置计算
    - 输出目录创建和文件保存

- **`exif_reader/`**: EXIF信息读取模块
  - `exif_reader.py`: EXIF数据解析
    - 支持PIL和ExifRead双库读取
    - 时间戳提取和格式化
    - 备选时间机制（文件修改时间）

- **`utils/`**: 工具模块
  - `config.py`: 配置管理
    - YAML配置文件支持
    - 参数验证和默认值处理
  - `logger.py`: 日志系统
    - 多级别日志输出
    - 控制台格式化显示

#### 📂 `samples/` - 测试样例目录
**主要功能**: 存放测试图片和输出结果

- `test_photo_1.jpg`: 无EXIF信息图片（1706x1279像素）
- `test_photo_with_exif.jpg`: 带EXIF信息图片（拍摄时间：2023-08-15）
- `samples_watermark/`: 自动生成的输出目录

#### 📂 `tests/` - 单元测试目录
**主要功能**: 包含所有单元测试代码

- 水印处理器功能测试
- EXIF读取器功能测试
- 各种边界条件和异常情况测试

#### 📂 `config/` - 配置文件目录
**主要功能**: 存放程序配置文件

- `default_config.yaml`: 默认水印样式配置

---

## 🔍 功能特性

### ✅ 已实现功能

1. **EXIF时间读取**
   - 支持DateTimeOriginal、DateTimeDigitized等多种时间标签
   - PIL和ExifRead双库支持，提高兼容性
   - 自动备选机制：EXIF缺失时使用文件修改时间

2. **灵活的水印配置**
   - 5种预设位置选择
   - 自定义字体大小和颜色
   - 自动对比色轮廓，提高可读性

3. **批量处理**
   - 支持单文件和目录批量处理
   - 智能格式识别和跳过
   - 处理进度统计和报告

4. **详细信息显示**
   - 原始EXIF时间戳完整显示
   - 水印配置详情输出
   - 图片基本信息展示

5. **完善的错误处理**
   - 友好的错误提示
   - 单文件失败不影响批量处理
   - 详细的日志输出

6. **跨平台支持**
   - Windows/Linux/macOS兼容
   - 自动系统字体选择
   - 路径处理规范化

---

## 📊 输出说明

### 文件输出
程序会在原图片目录下创建 `原目录名_watermark` 子目录，保存带水印的图片：

```
samples/
├── test_photo_1.jpg          # 原图片
└── samples_watermark/        # 输出目录
    └── test_photo_1.jpg      # 带水印图片
```

### 水印内容格式
- **格式**: YYYY-MM-DD（如：2023-08-15）
- **数据源优先级**:
  1. EXIF DateTimeOriginal（原始拍摄时间）
  2. EXIF DateTimeDigitized（数字化时间）
  3. EXIF DateTime（修改时间）
  4. 文件修改时间（备选）

### 日志输出示例
```
INFO: Processing image: test_photo_with_exif.jpg
INFO: ============================================================
INFO: Watermark Details
INFO: ============================================================
INFO: Image Info:
INFO:    Size: 1200x800 pixels
INFO:    Mode: RGB
INFO: Original Photo Timestamps:
INFO:    EXIF Data Found: True
INFO:    Data Source: PIL
INFO:    Original Shot Time: 2023:08:15 14:30:45
INFO:    Digitized Time: 2023:08:15 14:30:45
INFO: Watermark Text:
INFO:    Content: '2023-08-15'
INFO:    Length: 10 characters
INFO: Font Info:
INFO:    Size: 36px
INFO:    Type: FreeTypeFont
INFO:    Path: C:/Windows/Fonts/arial.ttf
INFO: Position Info:
INFO:    Config Position: bottom-right
INFO:    Actual Coordinates: (996, 754)
INFO:    Text Size: 184x26 pixels
INFO: Color Info:
INFO:    Main Color: white
INFO:    Outline Color: black
INFO: Output Settings:
INFO:    Output Quality: 95%
INFO: ============================================================
INFO: Successfully processed: test_photo_with_exif.jpg
```

---

## 🛠️ 技术栈

- **语言**: Python 3.8+
- **图像处理**: Pillow (PIL)
- **EXIF读取**: Pillow + ExifRead
- **配置管理**: PyYAML
- **测试**: pytest
- **代码质量**: black, flake8, mypy

---

## 📋 系统要求

- **操作系统**: Windows, Linux, macOS
- **Python版本**: 3.8 或更高版本
- **依赖库**:
  ```txt
  Pillow>=10.0.0      # 图像处理
  ExifRead>=3.0.0     # EXIF数据读取
  PyYAML>=6.0.0       # YAML配置文件
  piexif>=1.1.3       # EXIF数据操作（测试用）
  ```

---

## 🐛 故障排除

### 常见问题

**1. 没有找到EXIF拍摄时间**
```
WARNING: No date information found for: image.jpg
INFO: Using fallback date for image.jpg: 2025-09-24
```
- **原因**: 图片没有EXIF拍摄时间信息
- **解决**: 程序自动使用文件修改时间，这是正常行为

**2. 不支持的图片格式**
```
WARNING: Unsupported image format: image.bmp
```
- **原因**: 图片格式不在支持列表中
- **解决**: 使用JPG, JPEG, PNG, TIFF等格式

**3. 模块导入错误**
```
ModuleNotFoundError: No module named 'src'
```
- **原因**: 路径或运行方式不正确
- **解决**: 使用 `python -m src.main` 而不是 `python src/main.py`

### 获取帮助
```bash
# 显示帮助信息
python -m src.main --help

# 使用详细日志查看问题
python -m src.main samples/ --verbose
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 👨‍💻 开发信息

**开发者**: NJU Student RLY
**邮箱**: 211850116@smail.nju.edu.cn
**课程**: 南京大学大模型辅助软件工程
**开发方式**: Vibe Coding with Claude Code
**完成日期**: 2025-09-24

---

**📚 更多信息**:
- [软件需求规格说明书 (SRS.md)](SRS.md)
- [原始需求说明 (requirements_specification.md)](requirements_specification.md)