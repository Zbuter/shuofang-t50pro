"""USB 串口通信实现"""

import serial
from typing import Optional, List
from .base import Transport


class USBTransport(Transport):
    """USB 虚拟串口通信实现"""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 5.0):
        """
        初始化 USB 传输
        
        Args:
            port: 串口端口（如 '/dev/ttyUSB0' 或 'COM3'）
            baudrate: 波特率，默认 115200
            timeout: 读写超时时间（秒）
        """
        super().__init__(timeout)
        self.port = port
        self.baudrate = baudrate
        self._serial: Optional[serial.Serial] = None
    
    def connect(self) -> bool:
        """建立串口连接"""
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            self._connected = True
            return True
        except serial.SerialException as e:
            raise TransportError(f"无法打开串口 {self.port}: {e}")
    
    def disconnect(self) -> None:
        """断开串口连接"""
        if self._serial and self._serial.is_open:
            self._serial.close()
        self._serial = None
        self._connected = False
    
    def write(self, data: bytes) -> int:
        """写入数据到串口"""
        if not self._serial or not self._serial.is_open:
            raise TransportError("串口未连接")
        try:
            return self._serial.write(data)
        except serial.SerialException as e:
            raise TransportError(f"写入失败：{e}")
    
    def read(self, size: int = 1024) -> bytes:
        """从串口读取数据"""
        if not self._serial or not self._serial.is_open:
            raise TransportError("串口未连接")
        try:
            return self._serial.read(size)
        except serial.SerialException as e:
            raise TransportError(f"读取失败：{e}")
    
    def is_connected(self) -> bool:
        """检查串口连接状态"""
        return self._connected and self._serial is not None and self._serial.is_open
    
    def flush(self):
        """清空缓冲区"""
        if self._serial and self._serial.is_open:
            self._serial.flushInput()
            self._serial.flushOutput()
    
    @staticmethod
    def scan_ports() -> List[str]:
        """
        扫描可用的串口端口
        
        Returns:
            List[str]: 可用端口列表
        """
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]


class TransportError(Exception):
    """通信层异常"""
    pass
