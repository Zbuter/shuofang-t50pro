"""打印机状态解析模块"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PrinterStatus:
    """打印机状态数据结构"""
    
    # 基本状态
    is_ready: bool = True
    is_printing: bool = False
    
    # 纸张状态
    paper_status: str = "normal"  # normal/out/error
    paper_loaded: bool = True
    
    # 打印头状态
    head_status: str = "normal"  # normal/open/error
    head_temp: Optional[int] = None  # 温度（摄氏度）
    
    # 错误信息
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    
    # 其他状态
    cover_open: bool = False
    cutter_status: str = "normal"  # normal/error（如果支持切刀）
    
    def __str__(self) -> str:
        """字符串表示"""
        status_parts = []
        
        if self.is_ready:
            status_parts.append("就绪")
        else:
            status_parts.append("未就绪")
        
        if self.paper_status != "normal":
            status_parts.append(f"纸张：{self.paper_status}")
        
        if self.head_status != "normal":
            status_parts.append(f"打印头：{self.head_status}")
        
        if self.cover_open:
            status_parts.append("盖子打开")
        
        if self.error_message:
            status_parts.append(f"错误：{self.error_message}")
        
        return ", ".join(status_parts) if status_parts else "打印机正常"


class StatusParser:
    """打印机状态解析器"""
    
    # 状态字节定义（根据实际设备响应调整）
    STATUS_READY = 0x00
    STATUS_PRINTING = 0x01
    STATUS_PAPER_OUT = 0x02
    STATUS_HEAD_OPEN = 0x04
    STATUS_HEAD_HOT = 0x08
    STATUS_ERROR = 0x10
    STATUS_COVER_OPEN = 0x20
    
    @classmethod
    def parse(cls, status_bytes: bytes) -> PrinterStatus:
        """
        解析打印机状态响应
        
        Args:
            status_bytes: 打印机返回的状态字节
            
        Returns:
            PrinterStatus: 状态对象
        """
        status = PrinterStatus()
        
        if not status_bytes:
            status.is_ready = False
            status.error_message = "无响应"
            return status
        
        # 解析状态字节（具体格式需根据实际设备调整）
        # 这里假设是单字节状态码
        if len(status_bytes) >= 1:
            status_code = status_bytes[0]
            
            status.is_ready = (status_code & cls.STATUS_READY) == 0
            status.is_printing = (status_code & cls.STATUS_PRINTING) != 0
            status.paper_loaded = (status_code & cls.STATUS_PAPER_OUT) == 0
            status.head_status = "open" if (status_code & cls.STATUS_HEAD_OPEN) else "normal"
            
            if status_code & cls.STATUS_HEAD_HOT:
                status.head_status = "hot"
            
            if status_code & cls.STATUS_ERROR:
                status.error_code = status_code
                status.error_message = cls._decode_error(status_code)
            
            status.cover_open = (status_code & cls.STATUS_COVER_OPEN) != 0
        
        # 如果有更多字节，解析温度等信息
        if len(status_bytes) >= 2:
            status.head_temp = status_bytes[1]
        
        # 检查纸张状态
        if not status.paper_loaded:
            status.paper_status = "out"
        
        return status
    
    @classmethod
    def parse_ascii(cls, response: str) -> PrinterStatus:
        """
        解析 ASCII 格式的状态响应
        
        Args:
            response: ASCII 响应字符串
            
        Returns:
            PrinterStatus: 状态对象
        """
        status = PrinterStatus()
        
        # 常见响应格式解析
        response = response.strip().upper()
        
        if "READY" in response or "OK" in response:
            status.is_ready = True
        elif "ERROR" in response or "FAIL" in response:
            status.is_ready = False
            status.error_message = response
        elif "PAPER OUT" in response:
            status.paper_status = "out"
            status.paper_loaded = False
            status.is_ready = False
        elif "COVER OPEN" in response:
            status.cover_open = True
            status.is_ready = False
        elif "HEAD OPEN" in response:
            status.head_status = "open"
            status.is_ready = False
        else:
            # 尝试解析温度
            if "TEMP" in response:
                try:
                    import re
                    match = re.search(r'TEMP[:\s]*(\d+)', response, re.I)
                    if match:
                        status.head_temp = int(match.group(1))
                except:
                    pass
        
        return status
    
    @staticmethod
    def _decode_error(status_code: int) -> str:
        """解码错误代码"""
        errors = []
        
        if status_code & StatusParser.STATUS_PAPER_OUT:
            errors.append("纸张用尽")
        if status_code & StatusParser.STATUS_HEAD_OPEN:
            errors.append("打印头打开")
        if status_code & StatusParser.STATUS_HEAD_HOT:
            errors.append("打印头过热")
        if status_code & StatusParser.STATUS_COVER_OPEN:
            errors.append("盖子打开")
        
        return "; ".join(errors) if errors else "未知错误"
    
    @classmethod
    def parse_hex_response(cls, hex_str: str) -> PrinterStatus:
        """
        解析十六进制格式的状态响应
        
        Args:
            hex_str: 十六进制字符串（如 "00 01 02"）
            
        Returns:
            PrinterStatus: 状态对象
        """
        try:
            # 移除空格并转换为字节
            hex_clean = hex_str.replace(" ", "")
            status_bytes = bytes.fromhex(hex_clean)
            return cls.parse(status_bytes)
        except Exception as e:
            status = PrinterStatus()
            status.is_ready = False
            status.error_message = f"解析失败：{e}"
            return status
