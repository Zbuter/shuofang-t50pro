"""通信层抽象基类"""

from abc import ABC, abstractmethod
from typing import Optional


class Transport(ABC):
    """打印机通信传输抽象基类"""
    
    def __init__(self, timeout: float = 5.0):
        """
        初始化通信传输
        
        Args:
            timeout: 读写超时时间（秒）
        """
        self.timeout = timeout
        self._connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """
        建立连接
        
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    def write(self, data: bytes) -> int:
        """
        写入数据
        
        Args:
            data: 要发送的数据
            
        Returns:
            int: 实际写入的字节数
        """
        pass
    
    @abstractmethod
    def read(self, size: int = 1024) -> bytes:
        """
        读取数据
        
        Args:
            size: 最大读取字节数
            
        Returns:
            bytes: 读取的数据
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        检查连接状态
        
        Returns:
            bool: 是否已连接
        """
        pass
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
        return False
