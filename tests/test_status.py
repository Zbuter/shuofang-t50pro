"""打印机状态解析测试"""

import pytest
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from driver.status import StatusParser, PrinterStatus


class TestStatusParser:
    """状态解析器测试类"""
    
    def test_parse_empty_response(self):
        """测试空响应"""
        status = StatusParser.parse(b"")
        
        assert status.is_ready == False
        assert status.error_message == "无响应"
    
    def test_parse_ready_status(self):
        """测试就绪状态"""
        # 假设 0x00 表示就绪
        status = StatusParser.parse(b"\x00")
        
        assert status.is_ready == True
        assert status.paper_loaded == True
    
    def test_parse_paper_out(self):
        """测试纸张用尽状态"""
        # 假设 0x02 表示纸张用尽
        status = StatusParser.parse(b"\x02")
        
        assert status.paper_loaded == False
        assert status.paper_status == "out"
    
    def test_parse_head_open(self):
        """测试打印头打开状态"""
        # 假设 0x04 表示打印头打开
        status = StatusParser.parse(b"\x04")
        
        assert status.head_status == "open"
    
    def test_parse_cover_open(self):
        """测试盖子打开状态"""
        # 假设 0x20 表示盖子打开
        status = StatusParser.parse(b"\x20")
        
        assert status.cover_open == True
    
    def test_parse_with_temperature(self):
        """测试带温度的状态"""
        # 第一个字节状态，第二个字节温度
        status = StatusParser.parse(b"\x00\x32")  # 0x32 = 50
        
        assert status.head_temp == 50
    
    def test_parse_multiple_errors(self):
        """测试多个错误"""
        # 组合错误标志
        status_code = 0x02 | 0x04  # 纸张用尽 + 打印头打开
        status = StatusParser.parse(bytes([status_code]))
        
        assert status.paper_loaded == False
        assert status.head_status == "open"
    
    def test_parse_ascii_ready(self):
        """测试 ASCII 就绪响应"""
        status = StatusParser.parse_ascii("READY")
        
        assert status.is_ready == True
    
    def test_parse_ascii_ok(self):
        """测试 ASCII OK 响应"""
        status = StatusParser.parse_ascii("OK")
        
        assert status.is_ready == True
    
    def test_parse_ascii_error(self):
        """测试 ASCII 错误响应"""
        status = StatusParser.parse_ascii("ERROR: Paper out")
        
        assert status.is_ready == False
        assert "ERROR" in status.error_message
    
    def test_parse_ascii_paper_out(self):
        """测试 ASCII 纸张用尽响应"""
        status = StatusParser.parse_ascii("PAPER OUT")
        
        assert status.paper_loaded == False
        assert status.paper_status == "out"
    
    def test_parse_ascii_cover_open(self):
        """测试 ASCII 盖子打开响应"""
        status = StatusParser.parse_ascii("COVER OPEN")
        
        assert status.cover_open == True
    
    def test_parse_ascii_head_open(self):
        """测试 ASCII 打印头打开响应"""
        status = StatusParser.parse_ascii("HEAD OPEN")
        
        assert status.head_status == "open"
    
    def test_parse_ascii_with_temp(self):
        """测试 ASCII 带温度响应"""
        status = StatusParser.parse_ascii("READY TEMP: 45")
        
        assert status.head_temp == 45
    
    def test_parse_hex_response(self):
        """测试十六进制响应解析"""
        status = StatusParser.parse_hex_response("00 01 02")
        
        assert status.is_ready == True
    
    def test_parse_hex_response_invalid(self):
        """测试无效十六进制响应"""
        status = StatusParser.parse_hex_response("invalid hex")
        
        assert status.is_ready == False
        assert "解析失败" in status.error_message
    
    def test_status_str_normal(self):
        """测试状态字符串表示（正常）"""
        status = PrinterStatus()
        
        result = str(status)
        
        assert "正常" in result or "就绪" in result
    
    def test_status_str_error(self):
        """测试状态字符串表示（错误）"""
        status = PrinterStatus()
        status.is_ready = False
        status.paper_status = "out"
        status.error_message = "纸张用尽"
        
        result = str(status)
        
        assert "纸张" in result or "错误" in result
    
    def test_printer_status_default(self):
        """测试 PrinterStatus 默认值"""
        status = PrinterStatus()
        
        assert status.is_ready == True
        assert status.is_printing == False
        assert status.paper_status == "normal"
        assert status.paper_loaded == True
        assert status.head_status == "normal"
        assert status.head_temp is None
        assert status.error_code is None
        assert status.cover_open == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
