"""TSPL 指令集生成器"""

from typing import Optional, Union
from PIL import Image


class TSPLCommand:
    """TSPL (Tag Printer Standard Language) 指令生成器"""
    
    # 条形码类型常量
    BARCODE_CODE39 = "39"
    BARCODE_CODE128 = "128"
    BARCODE_EAN13 = "EAN13"
    BARCODE_EAN8 = "EAN8"
    BARCODE_UPCA = "UPCA"
    BARCODE_UPCE = "UPCE"
    BARCODE_ITF = "25"
    BARCODE_CODABAR = "CODABAR"
    BARCODE_CODE93 = "93"
    
    # 二维码纠错级别
    QR_ECC_L = "L"
    QR_ECC_M = "M"
    QR_ECC_Q = "Q"
    QR_ECC_H = "H"
    
    def __init__(self, encoding: str = 'gbk'):
        """
        初始化 TSPL 指令生成器
        
        Args:
            encoding: 字符编码，默认 gbk（中文打印机常用）
        """
        self.encoding = encoding
    
    def size(self, width: int, height: int) -> str:
        """
        设置标签尺寸
        
        Args:
            width: 标签宽度（mm）
            height: 标签高度（mm）
            
        Returns:
            str: TSPL SIZE 指令
        """
        return f"SIZE {width} mm,{height} mm\n"
    
    def gap(self, gap: int, offset: int = 0) -> str:
        """
        设置标签间隙
        
        Args:
            gap: 间隙长度（mm）
            offset: 垂直偏移（mm）
            
        Returns:
            str: TSPL GAP 指令
        """
        return f"GAP {gap} mm,{offset} mm\n"
    
    def speed(self, speed: int) -> str:
        """
        设置打印速度
        
        Args:
            speed: 速度等级（1-5）
            
        Returns:
            str: TSPL SPEED 指令
        """
        return f"SPEED {speed}\n"
    
    def density(self, density: int) -> str:
        """
        设置打印浓度
        
        Args:
            density: 浓度等级（1-15）
            
        Returns:
            str: TSPL DENSITY 指令
        """
        return f"DENSITY {density}\n"
    
    def direction(self, direction: int = 0) -> str:
        """
        设置打印方向
        
        Args:
            direction: 0=正常，1=旋转 180 度
            
        Returns:
            str: TSPL DIRECTION 指令
        """
        return f"DIRECTION {direction}\n"
    
    def reference(self, x: int, y: int) -> str:
        """
        设置参考坐标
        
        Args:
            x: X 轴参考点（mm）
            y: Y 轴参考点（mm）
            
        Returns:
            str: TSPL REFERENCE 指令
        """
        return f"REFERENCE {x},{y}\n"
    
    def cls(self) -> str:
        """
        清除缓冲区
        
        Returns:
            str: TSPL CLS 指令
        """
        return "CLS\n"
    
    def text(self, x: int, y: int, font: str = "1", 
             rotation: int = 0, x_mul: int = 1, y_mul: int = 1,
             content: str = "") -> str:
        """
        打印文本
        
        Args:
            x: X 坐标（mm）
            y: Y 坐标（mm）
            font: 字体类型（1-8 或字体文件名如 SIMSUN.TTF）
            rotation: 旋转角度（0, 90, 180, 270）
            x_mul: X 方向放大倍数
            y_mul: Y 方向放大倍数
            content: 文本内容
            
        Returns:
            str: TSPL TEXT 指令
        """
        return f'TEXT {x},{y},"{font}",{rotation},{x_mul},{y_mul},"{content}"\n'
    
    def barcode(self, x: int, y: int, type: str, height: int = 40,
                readable: int = 1, rotation: int = 0,
                narrow: int = 2, wide: int = 4,
                content: str = "") -> str:
        """
        打印条形码
        
        Args:
            x: X 坐标（mm）
            y: Y 坐标（mm）
            type: 条形码类型（见 BARCODE_* 常量）
            height: 条形码高度（点）
            readable: 是否显示可读文本（0/1）
            rotation: 旋转角度（0, 90, 180, 270）
            narrow: 窄条宽度（点）
            wide: 宽条宽度（点）
            content: 条形码内容
            
        Returns:
            str: TSPL BARCODE 指令
        """
        return f'BARCODE {x},{y},"{type}",{height},{readable},{rotation},{narrow},{wide},"{content}"\n'
    
    def qrcode(self, x: int, y: int, content: str,
               ecc: str = "M", size: int = 4,
               rotation: int = 0) -> str:
        """
        打印二维码
        
        Args:
            x: X 坐标（mm）
            y: Y 坐标（mm）
            content: 二维码内容
            ecc: 纠错级别（L/M/Q/H）
            size: 模块大小（1-10）
            rotation: 旋转角度（0, 90, 180, 270）
            
        Returns:
            str: TSPL QRCODE 指令
        """
        return f'QRCODE {x},{y},{ecc},{size},A{rotation},"{content}"\n'
    
    def bitmap(self, x: int, y: int, image: Image, 
               mode: str = "down") -> str:
        """
        打印位图
        
        Args:
            x: X 坐标（mm）
            y: Y 坐标（mm）
            image: PIL Image 对象
            mode: 扫描模式（down=从上到下，up=从下到上）
            
        Returns:
            str: TSPL BITMAP 指令（包含图像数据）
        """
        from .image import ImageConverter
        
        # 转换图像为位图数据
        bitmap_data = ImageConverter.to_bitmap(image)
        width, height = image.size
        
        # BITMAP 指令格式：BITMAP x,y,width,height,mode,data
        # 数据为十六进制
        hex_data = bitmap_data.hex().upper()
        
        return f"BITMAP {x},{y},{width},{height},{mode},{hex_data}\n"
    
    def reverse(self, x: int, y: int, width: int, height: int) -> str:
        """
        反白打印区域
        
        Args:
            x: X 坐标
            y: Y 坐标
            width: 宽度
            height: 高度
            
        Returns:
            str: TSPL REVERSE 指令
        """
        return f"REVERSE {x},{y},{width},{height}\n"
    
    def box(self, x: int, y: int, width: int, height: int, 
            thickness: int = 1) -> str:
        """
        打印矩形框
        
        Args:
            x: X 坐标
            y: Y 坐标
            width: 宽度
            height: 高度
            thickness: 线宽
            
        Returns:
            str: TSPL BOX 指令
        """
        return f"BOX {x},{y},{width},{height},{thickness}\n"
    
    def line(self, x1: int, y1: int, x2: int, y2: int,
             thickness: int = 1) -> str:
        """
        打印直线
        
        Args:
            x1: 起点 X
            y1: 起点 Y
            x2: 终点 X
            y2: 终点 Y
            thickness: 线宽
            
        Returns:
            str: TSPL LINE 指令
        """
        return f"LINE {x1},{y1},{x2},{y2},{thickness}\n"
    
    def print(self, count: int = 1, copy: int = 1) -> str:
        """
        执行打印
        
        Args:
            count: 打印份数
            copy: 每份副本数
            
        Returns:
            str: TSPL PRINT 指令
        """
        return f"PRINT {count},{copy}\n"
    
    def query_status(self) -> str:
        """
        查询打印机状态
        
        Returns:
            str: 状态查询指令
        """
        return "~T\r\n"
    
    def query_sensor(self) -> str:
        """
        查询传感器状态
        
        Returns:
            str: 传感器查询指令
        """
        return "~TS\r\n"
    
    def calibrate(self) -> str:
        """
        校准标签纸
        
        Returns:
            str: 校准指令
        """
        return "CALIBRATE\n"
    
    def init_printer(self) -> str:
        """
        初始化打印机
        
        Returns:
            str: 初始化指令
        """
        return "INIT\n"
    
    def setup(self, width: int, height: int, gap: int = 2) -> str:
        """
        快速设置打印机参数
        
        Args:
            width: 标签宽度（mm）
            height: 标签高度（mm）
            gap: 间隙（mm）
            
        Returns:
            str: 完整的设置指令序列
        """
        commands = []
        commands.append(self.init_printer())
        commands.append(self.size(width, height))
        commands.append(self.gap(gap))
        commands.append(self.direction(0))
        commands.append(self.cls())
        return "".join(commands)
