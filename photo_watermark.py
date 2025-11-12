import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import argparse

class WatermarkProcessor:
    def __init__(self, black_watermark_path, white_watermark_path):
        """
        初始化水印处理器
        :param black_watermark_path: 黑色水印图片路径
        :param white_watermark_path: 白色水印图片路径
        """
        # 加载水印图片
        self.black_watermark = self.load_watermark(black_watermark_path)
        self.white_watermark = self.load_watermark(white_watermark_path)
        
        # 定义6个水印位置（左上、中上、右上、左下、中下、右下）
        self.position_ratios = [
            (0.1, 0.1),   # 左上
            (0.5, 0.1),   # 中上
            (0.9, 0.1),   # 右上
            (0.1, 0.9),   # 左下
            (0.5, 0.9),   # 中下
            (0.9, 0.9)    # 右下
        ]
    
    def load_watermark(self, watermark_path):
        """加载水印图片并确保为RGBA格式"""
        watermark = Image.open(watermark_path).convert('RGBA')
        return watermark
    
    def calculate_region_brightness(self, image, region_center, region_size_ratio=0.2):
        """
        计算指定区域的亮度特征
        :param image: 输入图片
        :param region_center: 区域中心点坐标 (x_ratio, y_ratio)
        :param region_size_ratio: 区域大小相对于图片的比例
        :return: 区域的平均亮度和对比度
        """
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        h, w = img_array.shape
        region_w = int(w * region_size_ratio)
        region_h = int(h * region_size_ratio)
        
        center_x = int(w * region_center[0])
        center_y = int(h * region_center[1])
        
        # 计算区域边界
        x1 = max(0, center_x - region_w // 2)
        x2 = min(w, center_x + region_w // 2)
        y1 = max(0, center_y - region_h // 2)
        y2 = min(h, center_y + region_h // 2)
        
        # 提取区域
        region = img_array[y1:y2, x1:x2]
        
        if region.size == 0:
            return 0, 0
        
        # 计算平均亮度
        brightness = np.mean(region)
        
        # 计算对比度（标准差）
        contrast = np.std(region)
        
        return brightness, contrast
    
    def find_best_position(self, image):
        """
        找到最适合添加水印的位置
        :param image: 输入图片
        :return: 最佳位置索引和对应的亮度
        """
        best_score = -1
        best_position_idx = 0
        position_scores = []
        
        for idx, position in enumerate(self.position_ratios):
            brightness, contrast = self.calculate_region_brightness(image, position)
            
            # 计算位置得分：优先选择中等亮度、高对比度的区域
            # 中等亮度（接近128）得分最高，过高或过低都会降低得分
            brightness_score = 1 - abs(brightness - 128) / 128
            contrast_score = min(contrast / 64, 1.0)  # 标准化对比度得分
            
            # 综合得分
            score = brightness_score * 0.6 + contrast_score * 0.4
            position_scores.append((idx, score, brightness))
            
            if score > best_score:
                best_score = score
                best_position_idx = idx
        
        return best_position_idx, position_scores[best_position_idx][2]
    
    def choose_watermark_color(self, region_brightness):
        """
        根据区域亮度选择水印颜色
        :param region_brightness: 区域平均亮度
        :return: 选择的水印图片
        """
        # 如果区域较暗，使用白色水印；如果较亮，使用黑色水印
        if region_brightness < 128:
            return self.white_watermark
        else:
            return self.black_watermark
    
    def resize_watermark(self, watermark, target_width_ratio=0.3):
        """
        根据图片大小调整水印尺寸
        :param watermark: 水印图片
        :param target_width_ratio: 水印宽度相对于图片宽度的比例
        :return: 调整后的水印
        """
        return watermark
    
    def add_watermark_to_image(self, image, output_path=None):
        """
        为单张图片添加水印
        :param image: 输入图片（PIL Image）
        :param output_path: 输出路径
        :return: 添加水印后的图片
        """
        # 确保图片为RGBA格式
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 找到最佳位置
        best_position_idx, region_brightness = self.find_best_position(image)
        position = self.position_ratios[best_position_idx]
        
        # 选择水印颜色
        watermark = self.choose_watermark_color(region_brightness)
        
        # 调整水印大小（水印宽度为图片宽度的10%、高度的10%取较大值）
        img_width, img_height = image.size
        watermark_ratio = 3 / 2  # 水印宽高比
        watermark_width = max(int(img_width * 0.1), int(img_height * 0.1))
        watermark_height = int(watermark_width / watermark_ratio)

        watermark = watermark.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
        
        # 计算水印位置
        pos_x = int(img_width * position[0] - watermark_width // 2)
        pos_y = int(img_height * position[1] - watermark_height // 2)
        
        # 确保位置在图片范围内
        pos_x = max(0, min(pos_x, img_width - watermark_width))
        pos_y = max(0, min(pos_y, img_height - watermark_height))
        
        # 创建水印副本并调整透明度
        watermark_with_alpha = watermark.copy()
        alpha = watermark_with_alpha.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(1)  # 100%透明度
        watermark_with_alpha.putalpha(alpha)
        
        # 合并图片和水印
        result = image.copy()
        result.paste(watermark_with_alpha, (pos_x, pos_y), watermark_with_alpha)
        
        if output_path:
            # 保存为RGB格式（避免某些格式不支持透明度）
            result_rgb = result.convert('RGB')
            result_rgb.save(output_path, quality=95)
            print(f"水印已添加到: {output_path}")
        
        return result
    
    def process_batch(self, input_folder, output_folder, extensions=['.jpg', '.jpeg', '.png', '.bmp']):
        """
        批量处理文件夹中的图片
        :param input_folder: 输入文件夹路径
        :param output_folder: 输出文件夹路径
        :param extensions: 支持的图片格式
        """
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        processed_count = 0
        for filename in os.listdir(input_folder):
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in extensions:
                input_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, filename)
                
                try:
                    # 打开图片
                    image = Image.open(input_path)
                    # 添加水印
                    self.add_watermark_to_image(image, output_path)
                    processed_count += 1
                    print(f"已处理: {filename}")
                except Exception as e:
                    print(f"处理图片 {filename} 时出错: {str(e)}")
        
        print(f"\n批量处理完成！共处理 {processed_count} 张图片。")

def main():
    parser = argparse.ArgumentParser(description='批量图片添加水印工具')
    parser.add_argument('--input', '-i', required=True, help='输入文件夹路径')
    parser.add_argument('--output', '-o', required=True, help='输出文件夹路径')
    parser.add_argument('--black_watermark', '-b', default='black_watermark.png', help='黑色水印文件路径')
    parser.add_argument('--white_watermark', '-w', default='white_watermark.png', help='白色水印文件路径')
    
    args = parser.parse_args()
    
    # 检查水印文件是否存在
    if not os.path.exists(args.black_watermark):
        print(f"错误: 黑色水印文件不存在: {args.black_watermark}")
        return
    
    if not os.path.exists(args.white_watermark):
        print(f"错误: 白色水印文件不存在: {args.white_watermark}")
        return
    
    # 创建水印处理器
    processor = WatermarkProcessor(args.black_watermark, args.white_watermark)
    
    # 批量处理图片
    processor.process_batch(args.input, args.output)

if __name__ == "__main__":
    # 如果直接运行，使用示例
    if not os.path.exists('black_watermark.png') or not os.path.exists('white_watermark.png'):
        print("请准备黑白水印图片文件：black_watermark.png 和 white_watermark.png")
        print("或者使用命令行参数指定水印文件路径")
        print("示例: python watermark.py -i input_folder -o output_folder -b black.png -w white.png")
    else:
        main()