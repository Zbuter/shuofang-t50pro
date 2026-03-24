"""图像处理模块"""

from PIL import Image
from typing import Union
import io


class ImageConverter:
    """图像转换器 - 将图像转换为打印机位图格式"""
    
    @staticmethod
    def to_bitmap(image: Image) -> bytes:
        """
        将 PIL Image 转换为打印机位图数据
        
        Args:
            image: PIL Image 对象
            
        Returns:
            bytes: 位图数据（1bpp，每行补齐到字节边界）
        """
        # 转换为灰度图
        if image.mode != 'L':
            image = image.convert('L')
        
        width, height = image.size
        
        # 计算每行字节数（向上取整到字节边界）
        row_bytes = (width + 7) // 8
        
        bitmap_data = bytearray()
        
        for y in range(height):
            row_data = 0
            bit_count = 0
            
            for x in range(width):
                # 获取像素值（0-255）
                pixel = image.getpixel((x, y))
                # 二值化：大于 128 为白 (0)，否则为黑 (1)
                bit = 0 if pixel > 128 else 1
                # 组装字节（MSB first）
                row_data = (row_data << 1) | bit
                bit_count += 1
            
            # 补齐剩余位
            if bit_count < 8:
                row_data <<= (8 - bit_count)
            
            bitmap_data.append(row_data)
        
        return bytes(bitmap_data)
    
    @staticmethod
    def to_threshold(image: Image, threshold: int = 128) -> Image:
        """
        将图像二值化
        
        Args:
            image: PIL Image 对象
            threshold: 阈值（0-255）
            
        Returns:
            Image: 二值化后的图像（模式 '1'）
        """
        if image.mode != 'L':
            image = image.convert('L')
        
        # 应用阈值
        return image.point(lambda p: 255 if p > threshold else 0, mode='1')
    
    @staticmethod
    def to_grayscale(image: Image) -> Image:
        """
        转换为灰度图
        
        Args:
            image: PIL Image 对象
            
        Returns:
            Image: 灰度图像
        """
        if image.mode == 'L':
            return image
        return image.convert('L')
    
    @staticmethod
    def resize(image: Image, max_width: int = None, 
               max_height: int = None, 
               dpi: int = 203) -> Image:
        """
        调整图像大小
        
        Args:
            image: PIL Image 对象
            max_width: 最大宽度（mm），None 表示不限制
            max_height: 最大高度（mm），None 表示不限制
            dpi: 打印机 DPI（默认 203）
            
        Returns:
            Image: 调整后的图像
        """
        if max_width is None and max_height is None:
            return image
        
        # 计算最大像素尺寸
        max_width_px = int(max_width * dpi / 25.4) if max_width else None
        max_height_px = int(max_height * dpi / 25.4) if max_height else None
        
        orig_width, orig_height = image.size
        
        # 计算缩放比例
        scale = 1.0
        if max_width_px and orig_width > max_width_px:
            scale = min(scale, max_width_px / orig_width)
        if max_height_px and orig_height > max_height_px:
            scale = min(scale, max_height_px / orig_height)
        
        if scale < 1.0:
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            # 使用 LANCZOS 重采样保证质量
            return image.resize((new_width, new_height), Image.LANCZOS)
        
        return image
    
    @staticmethod
    def from_file(filepath: str, max_width: int = None,
                  max_height: int = None) -> Image:
        """
        从文件加载图像并调整大小
        
        Args:
            filepath: 图像文件路径
            max_width: 最大宽度（mm）
            max_height: 最大高度（mm）
            
        Returns:
            Image: 加载并调整后的图像
        """
        image = Image.open(filepath)
        return ImageConverter.resize(image, max_width, max_height)
    
    @staticmethod
    def create_text_image(text: str, font_size: int = 24,
                          width: int = None, height: int = None) -> Image:
        """
        创建文本图像
        
        Args:
            text: 文本内容
            font_size: 字体大小
            width: 图像宽度（像素）
            height: 图像高度（像素）
            
        Returns:
            Image: 文本图像
        """
        # 估算文本尺寸
        # 简单估算：每个字符约 font_size * 0.6 宽
        if width is None:
            width = max(100, int(len(text) * font_size * 0.6))
        if height is None:
            height = font_size + 10
        
        # 创建白色背景图像
        image = Image.new('RGB', (width, height), color='white')
        
        # 尝试加载中文字体
        try:
            from PIL import ImageFont
            # 常见中文字体路径
            font_paths = [
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                "C:/Windows/Fonts/simsun.ttc",
                "/System/Library/Fonts/PingFang.ttc",
            ]
            font = None
            for path in font_paths:
                try:
                    font = ImageFont.truetype(path, font_size)
                    break
                except:
                    continue
            if font is None:
                font = ImageFont.load_default()
        except ImportError:
            font = ImageFont.load_default()
        
        # 绘制文本
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        
        # 计算文本位置（居中）
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            text_width, text_height = draw.textsize(text, font=font)
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='black', font=font)
        
        return image
    
    @staticmethod
    def invert(image: Image) -> Image:
        """
        反转图像（黑白互换）
        
        Args:
            image: PIL Image 对象
            
        Returns:
            Image: 反转后的图像
        """
        from PIL import ImageOps
        return ImageOps.invert(image.convert('L'))
    
    @staticmethod
    def rotate(image: Image, angle: int) -> Image:
        """
        旋转图像
        
        Args:
            image: PIL Image 对象
            angle: 旋转角度（90, 180, 270）
            
        Returns:
            Image: 旋转后的图像
        """
        if angle == 90:
            return image.transpose(Image.ROTATE_90)
        elif angle == 180:
            return image.transpose(Image.ROTATE_180)
        elif angle == 270:
            return image.transpose(Image.ROTATE_270)
        return image
