"""TSPL 指令测试"""

import pytest
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from driver.tspl import TSPLCommand
from PIL import Image


class TestTSPLCommand:
    """TSPL 指令测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.tspl = TSPLCommand()
    
    def test_size_command(self):
        """测试 SIZE 指令"""
        result = self.tspl.size(50, 30)
        assert result == "SIZE 50 mm,30 mm\n"
    
    def test_gap_command(self):
        """测试 GAP 指令"""
        result = self.tspl.gap(2, 0)
        assert result == "GAP 2 mm,0 mm\n"
    
    def test_speed_command(self):
        """测试 SPEED 指令"""
        result = self.tspl.speed(3)
        assert result == "SPEED 3\n"
    
    def test_density_command(self):
        """测试 DENSITY 指令"""
        result = self.tspl.density(10)
        assert result == "DENSITY 10\n"
    
    def test_direction_command(self):
        """测试 DIRECTION 指令"""
        result = self.tspl.direction(0)
        assert result == "DIRECTION 0\n"
        
        result = self.tspl.direction(1)
        assert result == "DIRECTION 1\n"
    
    def test_reference_command(self):
        """测试 REFERENCE 指令"""
        result = self.tspl.reference(10, 20)
        assert result == "REFERENCE 10,20\n"
    
    def test_cls_command(self):
        """测试 CLS 指令"""
        result = self.tspl.cls()
        assert result == "CLS\n"
    
    def test_text_command(self):
        """测试 TEXT 指令"""
        result = self.tspl.text(10, 20, "1", 0, 1, 1, "Hello")
        assert result == 'TEXT 10,20,"1",0,1,1,"Hello"\n'
    
    def test_text_command_chinese(self):
        """测试中文 TEXT 指令"""
        result = self.tspl.text(10, 20, "SIMSUN.TTF", 0, 2, 2, "测试文本")
        assert result == 'TEXT 10,20,"SIMSUN.TTF",0,2,2,"测试文本"\n'
    
    def test_barcode_command(self):
        """测试 BARCODE 指令"""
        result = self.tspl.barcode(10, 20, "128", 50, 1, 0, 2, 4, "123456")
        assert result == 'BARCODE 10,20,"128",50,1,0,2,4,"123456"\n'
    
    def test_barcode_code39(self):
        """测试 CODE39 条形码"""
        result = self.tspl.barcode(10, 20, "39", 50, 1, 0, 2, 4, "ABC123")
        assert '"39"' in result
        assert '"ABC123"' in result
    
    def test_qrcode_command(self):
        """测试 QRCODE 指令"""
        result = self.tspl.qrcode(10, 20, "https://example.com", "M", 4)
        assert 'QRCODE 10,20,M,4,A0,"https://example.com"\n' == result
    
    def test_qrcode_different_ecc(self):
        """测试不同纠错级别的二维码"""
        for ecc in ["L", "M", "Q", "H"]:
            result = self.tspl.qrcode(10, 20, "test", ecc, 4)
            assert f',{ecc},' in result
    
    def test_print_command(self):
        """测试 PRINT 指令"""
        result = self.tspl.print(1, 1)
        assert result == "PRINT 1,1\n"
        
        result = self.tspl.print(3, 2)
        assert result == "PRINT 3,2\n"
    
    def test_query_status_command(self):
        """测试状态查询指令"""
        result = self.tspl.query_status()
        assert result == "~T\r\n"
    
    def test_query_sensor_command(self):
        """测试传感器查询指令"""
        result = self.tspl.query_sensor()
        assert result == "~TS\r\n"
    
    def test_calibrate_command(self):
        """测试校准指令"""
        result = self.tspl.calibrate()
        assert result == "CALIBRATE\n"
    
    def test_init_command(self):
        """测试初始化指令"""
        result = self.tspl.init_printer()
        assert result == "INIT\n"
    
    def test_box_command(self):
        """测试 BOX 指令"""
        result = self.tspl.box(10, 20, 100, 50, 2)
        assert result == "BOX 10,20,100,50,2\n"
    
    def test_line_command(self):
        """测试 LINE 指令"""
        result = self.tspl.line(10, 20, 100, 20, 1)
        assert result == "LINE 10,20,100,20,1\n"
    
    def test_reverse_command(self):
        """测试 REVERSE 指令"""
        result = self.tspl.reverse(10, 20, 50, 30)
        assert result == "REVERSE 10,20,50,30\n"
    
    def test_setup_command(self):
        """测试 setup 快捷方法"""
        result = self.tspl.setup(50, 30, 2)
        
        assert "SIZE 50 mm,30 mm\n" in result
        assert "GAP 2 mm,0 mm\n" in result
        assert "CLS\n" in result
        assert "INIT\n" in result
    
    def test_bitmap_command(self):
        """测试 BITMAP 指令"""
        # 创建测试图像
        img = Image.new('L', (8, 8), color=128)
        
        result = self.tspl.bitmap(10, 20, img)
        
        assert "BITMAP 10,20,8,8,down," in result
        # 验证包含十六进制数据
        assert len(result) > 30
    
    def test_encoding(self):
        """测试编码设置"""
        tspl_gbk = TSPLCommand(encoding='gbk')
        tspl_utf8 = TSPLCommand(encoding='utf-8')
        
        assert tspl_gbk.encoding == 'gbk'
        assert tspl_utf8.encoding == 'utf-8'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
