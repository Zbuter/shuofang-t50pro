"""图像处理测试"""

import pytest
import sys
import os
from io import BytesIO

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from driver.image import ImageConverter
from PIL import Image


class TestImageConverter:
    """图像转换器测试类"""
    
    def test_to_bitmap_basic(self):
        """测试基本位图转换"""
        # 创建 8x8 黑白图像
        img = Image.new('L', (8, 8), color=0)  # 全黑
        
        bitmap = ImageConverter.to_bitmap(img)
        
        # 8x8 像素 = 8 字节（每行 1 字节）
        assert len(bitmap) == 8
        # 全黑应该是全 1（打印机是反色）
        assert all(b == 0xFF for b in bitmap)
    
    def test_to_bitmap_white(self):
        """测试白色位图转换"""
        # 创建全白图像
        img = Image.new('L', (8, 8), color=255)
        
        bitmap = ImageConverter.to_bitmap(img)
        
        # 全白应该是全 0
        assert len(bitmap) == 8
        assert all(b == 0x00 for b in bitmap)
    
    def test_to_bitmap_non_square(self):
        """测试非正方形图像"""
        img = Image.new('L', (16, 8), color=0)  # 16x8
        
        bitmap = ImageConverter.to_bitmap(img)
        
        # 16 像素宽 = 2 字节每行，8 行 = 16 字节
        assert len(bitmap) == 16
    
    def test_to_bitmap_odd_width(self):
        """测试奇数宽度图像"""
        img = Image.new('L', (9, 8), color=0)  # 9x8
        
        bitmap = ImageConverter.to_bitmap(img)
        
        # 9 像素宽 = 2 字节每行（向上取整），8 行 = 16 字节
        assert len(bitmap) == 16
    
    def test_to_threshold(self):
        """测试阈值二值化"""
        # 创建渐变图像
        img = Image.new('L', (10, 10))
        for x in range(10):
            for y in range(10):
                img.putpixel((x, y), x * 25)  # 0, 25, 50, ..., 225
        
        # 应用阈值 128
        binary = ImageConverter.to_threshold(img, threshold=128)
        
        assert binary.mode == '1'
        
        # 检查像素值
        for x in range(10):
            for y in range(10):
                pixel = binary.getpixel((x, y))
                if x * 25 > 128:
                    assert pixel == 255  # 白
                else:
                    assert pixel == 0  # 黑
    
    def test_to_grayscale(self):
        """测试转灰度图"""
        # RGB 图像
        img_rgb = Image.new('RGB', (10, 10), color=(128, 64, 32))
        
        img_gray = ImageConverter.to_grayscale(img_rgb)
        
        assert img_gray.mode == 'L'
    
    def test_to_grayscale_already_gray(self):
        """测试已经是灰度图的情况"""
        img = Image.new('L', (10, 10))
        
        result = ImageConverter.to_grayscale(img)
        
        assert result.mode == 'L'
        assert result is img  # 应该返回同一个对象
    
    def test_resize_downscale(self):
        """测试缩小图像"""
        img = Image.new('RGB', (100, 100))
        
        # 缩小到 50mm（约 400 像素@203DPI）
        result = ImageConverter.resize(img, max_width=25)  # 25mm ≈ 200 像素
        
        assert result.size[0] <= 200
        assert result.size[1] <= 200
    
    def test_resize_no_change(self):
        """测试不需要缩放的情况"""
        img = Image.new('RGB', (50, 50))
        
        # 限制比原图大
        result = ImageConverter.resize(img, max_width=100)
        
        assert result.size == (50, 50)
    
    def test_from_file(self):
        """测试从文件加载"""
        # 创建临时图像
        img = Image.new('RGB', (100, 100), color='red')
        
        # 保存到内存
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # 从内存加载（模拟文件）
        loaded = Image.open(buffer)
        
        assert loaded.size == (100, 100)
    
    def test_create_text_image(self):
        """测试创建文本图像"""
        img = ImageConverter.create_text_image("Hello", font_size=24)
        
        assert img.mode == 'RGB'
        assert img.size[1] >= 24  # 高度至少是字体大小
    
    def test_create_text_image_custom_size(self):
        """测试自定义尺寸的文本图像"""
        img = ImageConverter.create_text_image(
            "Test",
            font_size=20,
            width=200,
            height=50
        )
        
        assert img.size == (200, 50)
    
    def test_invert(self):
        """测试图像反转"""
        # 创建黑色图像
        img = Image.new('L', (10, 10), color=0)
        
        inverted = ImageConverter.invert(img)
        
        # 反转后应该是白色（255）
        assert inverted.getpixel((0, 0)) == 255
    
    def test_rotate_90(self):
        """测试 90 度旋转"""
        img = Image.new('RGB', (100, 50))
        
        result = ImageConverter.rotate(img, 90)
        
        assert result.size == (50, 100)
    
    def test_rotate_180(self):
        """测试 180 度旋转"""
        img = Image.new('RGB', (100, 50))
        
        result = ImageConverter.rotate(img, 180)
        
        assert result.size == (100, 50)
    
    def test_rotate_270(self):
        """测试 270 度旋转"""
        img = Image.new('RGB', (100, 50))
        
        result = ImageConverter.rotate(img, 270)
        
        assert result.size == (50, 100)
    
    def test_rotate_0(self):
        """测试 0 度旋转"""
        img = Image.new('RGB', (100, 50))
        
        result = ImageConverter.rotate(img, 0)
        
        assert result.size == (100, 50)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
