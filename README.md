# photo_watermark 智能图片水印批量处理工具

一个基于 Python 的智能图片水印批量处理工具，能够自动选择最佳水印位置和颜色，确保水印清晰可见且不突兀。

## 功能特点

- 🎯 **智能位置选择**：在6个预设位置中自动选择最适合的区域
- 🎨 **自动颜色适配**：根据背景亮度智能选择黑白水印
- 📁 **批量处理**：支持整个文件夹的图片批量处理
- 🖼️ **多格式支持**：支持 JPG、JPEG、PNG、BMP 等常见图片格式
- ⚡ **自适应大小**：水印尺寸根据图片大小自动调整
- 🔧 **易于使用**：简单的命令行接口，开箱即用

## 安装依赖

```bash
pip install pillow opencv-python numpy
```

## 使用方法

### 1. 准备水印图片

准备两张 PNG 格式的水印图片（建议 3:2 比例）：
- `black_watermark.png` - 黑色水印
- `white_watermark.png` - 白色水印

### 2. 基本使用

```bash
# 批量处理图片
python watermark.py -i input_images -o output_images

# 指定自定义水印文件
python watermark.py -i input_images -o output_images -b black.png -w white.png
```

### 3. 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|---------|
| `--input` | `-i` | 输入图片文件夹路径 | **必需** |
| `--output` | `-o` | 输出图片文件夹路径 | **必需** |
| `--black_watermark` | `-b` | 黑色水印文件路径 | `black_watermark.png` |
| `--white_watermark` | `-w` | 白色水印文件路径 | `white_watermark.png` |

### 4. 使用示例

```bash
# 处理照片文件夹
python watermark.py -i /path/to/photos -o /path/to/watermarked_photos

# 使用自定义水印
python watermark.py -i ./input -o ./output -b my_black_logo.png -w my_white_logo.png
```

## 算法原理

### 位置选择策略
程序在以下6个位置进行评估：
- 左上角 (10%, 10%)
- 中上 (50%, 10%) 
- 右上角 (90%, 10%)
- 左下角 (10%, 90%)
- 中下 (50%, 90%)
- 右下角 (90%, 90%)

### 智能评分系统
每个位置根据以下因素计算得分：
- **亮度得分**：中等亮度区域得分更高
- **对比度得分**：高对比度区域得分更高
- **综合得分** = 亮度得分 × 0.6 + 对比度得分 × 0.4

### 颜色选择逻辑
- **暗色背景** → 使用白色水印
- **亮色背景** → 使用黑色水印

## 程序结构

```
watermark.py
├── WatermarkProcessor 类
│   ├── __init__() - 初始化水印处理器
│   ├── load_watermark() - 加载水印图片
│   ├── calculate_region_brightness() - 计算区域亮度特征
│   ├── find_best_position() - 寻找最佳水印位置
│   ├── choose_watermark_color() - 选择水印颜色
│   ├── add_watermark_to_image() - 为单张图片添加水印
│   └── process_batch() - 批量处理图片
└── main() - 命令行接口
```


## 技术细节

- **图像处理**：使用 OpenCV 和 PIL 进行图像分析处理
- **颜色空间**：RGB 和灰度空间转换
- **水印透明度**：100% 不透明度，可根据需要调整
- **重采样算法**：LANCZOS 高质量重采样

## 注意事项

1. 确保水印图片为 PNG 格式并带有透明度
2. 输入文件夹需要存在且包含图片文件
3. 输出文件夹会自动创建
4. 处理大尺寸图片时可能需要较多内存

## 故障排除

**常见问题：**
- `ModuleNotFoundError: No module named 'cv2'`
  - 解决方案：运行 `pip install opencv-python`

- `错误: 黑色水印文件不存在`
  - 解决方案：确保水印文件存在于指定路径

- 处理过程中内存不足
  - 解决方案：分批处理图片或减小水印尺寸

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！
