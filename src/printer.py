"""主打印机类"""

from typing import Optional, Union, List
from PIL import Image

from .transport import Transport, USBTransport, BLETransport, TCPTransport
from .driver import TSPLCommand, StatusParser, PrinterStatus
from .service import PrintJob, DeviceManager


class Printer:
    """硕方 T50Pro 标签打印机主类"""
    
    def __init__(self, transport: Transport = None):
        """
        初始化打印机
        
        Args:
            transport: 通信传输实例，可选
        """
        self.transport: Optional[Transport] = transport
        self.tspl = TSPLCommand()
        self._connected = False
    
    @classmethod
    def usb(cls, port: str, baudrate: int = 115200) -> 'Printer':
        """
        创建 USB 连接的打印机实例
        
        Args:
            port: 串口端口
            baudrate: 波特率
            
        Returns:
            Printer: 打印机实例
        """
        transport = USBTransport(port, baudrate)
        return cls(transport)
    
    @classmethod
    def ble(cls, address: str) -> 'Printer':
        """
        创建蓝牙连接的打印机实例
        
        Args:
            address: 蓝牙设备地址
            
        Returns:
            Printer: 打印机实例
        """
        transport = BLETransport(address)
        return cls(transport)
    
    @classmethod
    def tcp(cls, host: str, port: int = 9100) -> 'Printer':
        """
        创建网络连接的打印机实例
        
        Args:
            host: 主机地址
            port: 端口号
            
        Returns:
            Printer: 打印机实例
        """
        transport = TCPTransport(host, port)
        return cls(transport)
    
    def connect(self) -> bool:
        """
        连接打印机
        
        Returns:
            bool: 连接是否成功
        """
        if not self.transport:
            raise PrinterError("未配置通信传输")
        
        self._connected = self.transport.connect()
        return self._connected
    
    def disconnect(self):
        """断开连接"""
        if self.transport:
            self.transport.disconnect()
            self._connected = False
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._connected and self.transport is not None and self.transport.is_connected()
    
    def print_job(self, job: PrintJob, count: int = 1) -> bool:
        """
        打印任务
        
        Args:
            job: 打印任务
            count: 打印份数
            
        Returns:
            bool: 是否成功
        """
        if not self.is_connected():
            raise PrinterError("打印机未连接")
        
        try:
            # 渲染指令
            commands = job.render()
            # 添加打印指令
            commands += self.tspl.print(count)
            
            # 发送指令（编码为 GBK）
            self.transport.write(commands.encode('gbk'))
            
            return True
        except Exception as e:
            raise PrinterError(f"打印失败：{e}")
    
    def print_text(self, text: str, x: int = 10, y: int = 10,
                   font: str = "1", size: int = 1,
                   width: int = 50, height: int = 30) -> bool:
        """
        快捷打印文本
        
        Args:
            text: 文本内容
            x: X 坐标
            y: Y 坐标
            font: 字体
            size: 大小倍数
            width: 标签宽度
            height: 标签高度
            
        Returns:
            bool: 是否成功
        """
        job = PrintJob(width, height)
        job.add_text(text, x, y, font, size)
        return self.print_job(job)
    
    def print_barcode(self, content: str, barcode_type: str = "128",
                      x: int = 10, y: int = 10, height: int = 40,
                      width: int = 50, height_mm: int = 30) -> bool:
        """
        快捷打印条形码
        
        Args:
            content: 条形码内容
            barcode_type: 条形码类型
            x: X 坐标
            y: Y 坐标
            height: 条形码高度
            width: 标签宽度
            height_mm: 标签高度
            
        Returns:
            bool: 是否成功
        """
        job = PrintJob(width, height_mm)
        job.add_barcode(content, x, y, barcode_type, height)
        return self.print_job(job)
    
    def print_qrcode(self, content: str, x: int = 10, y: int = 10,
                     ecc: str = "M", size: int = 4,
                     width: int = 50, height: int = 30) -> bool:
        """
        快捷打印二维码
        
        Args:
            content: 二维码内容
            x: X 坐标
            y: Y 坐标
            ecc: 纠错级别
            size: 模块大小
            width: 标签宽度
            height: 标签高度
            
        Returns:
            bool: 是否成功
        """
        job = PrintJob(width, height)
        job.add_qrcode(content, x, y, ecc, size)
        return self.print_job(job)
    
    def print_image(self, image: Union[Image, str],
                    x: int = 10, y: int = 10,
                    max_width: int = None, max_height: int = None,
                    width: int = 50, height: int = 30) -> bool:
        """
        快捷打印图片
        
        Args:
            image: PIL Image 或文件路径
            x: X 坐标
            y: Y 坐标
            max_width: 最大宽度
            max_height: 最大高度
            width: 标签宽度
            height: 标签高度
            
        Returns:
            bool: 是否成功
        """
        job = PrintJob(width, height)
        job.add_image(image, x, y, max_width, max_height)
        return self.print_job(job)
    
    def get_status(self) -> PrinterStatus:
        """
        获取打印机状态
        
        Returns:
            PrinterStatus: 状态对象
        """
        if not self.is_connected():
            raise PrinterError("打印机未连接")
        
        try:
            # 发送状态查询
            self.transport.write(self.tspl.query_status().encode('gbk'))
            
            # 读取响应
            response = self.transport.read(256)
            
            # 解析状态
            return StatusParser.parse(response)
        except Exception as e:
            raise PrinterError(f"获取状态失败：{e}")
    
    def calibrate(self) -> bool:
        """
        校准标签纸
        
        Returns:
            bool: 是否成功
        """
        if not self.is_connected():
            raise PrinterError("打印机未连接")
        
        try:
            commands = self.tspl.calibrate()
            self.transport.write(commands.encode('gbk'))
            return True
        except Exception as e:
            raise PrinterError(f"校准失败：{e}")
    
    def reset(self) -> bool:
        """
        重置打印机
        
        Returns:
            bool: 是否成功
        """
        if not self.is_connected():
            raise PrinterError("打印机未连接")
        
        try:
            commands = self.tspl.init_printer()
            self.transport.write(commands.encode('gbk'))
            return True
        except Exception as e:
            raise PrinterError(f"重置失败：{e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
        return False


class PrinterError(Exception):
    """打印机异常"""
    pass
