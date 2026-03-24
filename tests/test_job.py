"""打印任务测试"""

import pytest
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from service.job import PrintJob


class TestPrintJob:
    """打印任务测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.job = PrintJob(50, 30)
    
    def test_create_job(self):
        """测试创建打印任务"""
        job = PrintJob(50, 30)
        
        assert job.width == 50
        assert job.height == 30
        assert job.gap == 2
        assert len(job.elements) == 0
    
    def test_add_text(self):
        """测试添加文本"""
        self.job.add_text("Hello", 10, 10)
        
        assert len(self.job.elements) == 1
        assert self.job.elements[0]["type"] == "text"
        assert self.job.elements[0]["content"] == "Hello"
        assert self.job.elements[0]["x"] == 10
        assert self.job.elements[0]["y"] == 10
    
    def test_add_text_chain(self):
        """测试链式调用添加文本"""
        result = self.job.add_text("Line1", 10, 10).add_text("Line2", 10, 20)
        
        assert result is self.job
        assert len(self.job.elements) == 2
    
    def test_add_barcode(self):
        """测试添加条形码"""
        self.job.add_barcode("123456", 10, 10, type="128")
        
        assert len(self.job.elements) == 1
        assert self.job.elements[0]["type"] == "barcode"
        assert self.job.elements[0]["content"] == "123456"
        assert self.job.elements[0]["barcode_type"] == "128"
    
    def test_add_qrcode(self):
        """测试添加二维码"""
        self.job.add_qrcode("https://example.com", 10, 10)
        
        assert len(self.job.elements) == 1
        assert self.job.elements[0]["type"] == "qrcode"
        assert self.job.elements[0]["content"] == "https://example.com"
    
    def test_add_box(self):
        """测试添加矩形框"""
        self.job.add_box(5, 5, 40, 20, thickness=2)
        
        assert len(self.job.elements) == 1
        assert self.job.elements[0]["type"] == "box"
        assert self.job.elements[0]["width"] == 40
        assert self.job.elements[0]["thickness"] == 2
    
    def test_add_line(self):
        """测试添加直线"""
        self.job.add_line(10, 10, 40, 10, thickness=1)
        
        assert len(self.job.elements) == 1
        assert self.job.elements[0]["type"] == "line"
        assert self.job.elements[0]["x1"] == 10
        assert self.job.elements[0]["x2"] == 40
    
    def test_set_speed(self):
        """测试设置速度"""
        self.job.set_speed(3)
        
        assert self.job.speed == 3
    
    def test_set_speed_bounds(self):
        """测试速度边界"""
        self.job.set_speed(0)  # 应该被限制为 1
        assert self.job.speed == 1
        
        self.job.set_speed(10)  # 应该被限制为 5
        assert self.job.speed == 5
    
    def test_set_density(self):
        """测试设置浓度"""
        self.job.set_density(12)
        
        assert self.job.density == 12
    
    def test_set_direction(self):
        """测试设置方向"""
        self.job.set_direction(1)
        
        assert self.job.direction == 1
    
    def test_set_reference(self):
        """测试设置参考点"""
        self.job.set_reference(5, 10)
        
        assert self.job.reference_x == 5
        assert self.job.reference_y == 10
    
    def test_clear(self):
        """测试清空"""
        self.job.add_text("Test", 10, 10)
        assert len(self.job.elements) == 1
        
        self.job.clear()
        
        assert len(self.job.elements) == 0
    
    def test_render_basic(self):
        """测试基本渲染"""
        self.job.add_text("Hello", 10, 10)
        
        result = self.job.render()
        
        assert "SIZE 50 mm,30 mm" in result
        assert 'TEXT 10,10' in result
        assert '"Hello"' in result
        assert "PRINT" in result
    
    def test_render_multiple_elements(self):
        """测试渲染多个元素"""
        self.job.add_text("Title", 10, 5)
        self.job.add_barcode("123", 10, 15)
        self.job.add_qrcode("test", 10, 25)
        
        result = self.job.render()
        
        assert 'TEXT 10,5' in result
        assert 'BARCODE' in result
        assert 'QRCODE' in result
    
    def test_to_dict(self):
        """测试转换为字典"""
        self.job.add_text("Test", 10, 10)
        self.job.set_speed(3)
        
        data = self.job.to_dict()
        
        assert data["width"] == 50
        assert data["height"] == 30
        assert data["speed"] == 3
        assert len(data["elements"]) == 1
    
    def test_to_json(self):
        """测试转换为 JSON"""
        self.job.add_text("测试", 10, 10)
        
        json_str = self.job.to_json()
        
        assert "测试" in json_str
        assert "50" in json_str
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "width": 60,
            "height": 40,
            "gap": 3,
            "speed": 4,
            "elements": [
                {
                    "type": "text",
                    "content": "Test",
                    "x": 10,
                    "y": 10
                }
            ]
        }
        
        job = PrintJob.from_dict(data)
        
        assert job.width == 60
        assert job.height == 40
        assert job.speed == 4
        assert len(job.elements) == 1
    
    def test_from_json(self):
        """测试从 JSON 创建"""
        json_str = '''
        {
            "width": 50,
            "height": 30,
            "gap": 2,
            "elements": []
        }
        '''
        
        job = PrintJob.from_json(json_str)
        
        assert job.width == 50
        assert job.height == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
