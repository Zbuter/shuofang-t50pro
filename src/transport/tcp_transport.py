"""TCP 网络通信实现"""

import socket
from typing import Optional, Tuple
from .base import Transport


class TCPTransport(Transport):
    """TCP 网络通信实现"""
    
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        """
        初始化 TCP 传输
        
        Args:
            host: 服务器地址
            port: 服务器端口
            timeout: 读写超时时间（秒）
        """
        super().__init__(timeout)
        self.host = host
        self.port = port
        self._socket: Optional[socket.socket] = None
    
    def connect(self) -> bool:
        """建立 TCP 连接"""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.host, self.port))
            self._connected = True
            return True
        except socket.error as e:
            raise TransportError(f"TCP 连接失败 {self.host}:{self.port}: {e}")
    
    def disconnect(self) -> None:
        """断开 TCP 连接"""
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            finally:
                self._socket = None
                self._connected = False
    
    def write(self, data: bytes) -> int:
        """写入数据到 TCP socket"""
        if not self._socket:
            raise TransportError("TCP 未连接")
        try:
            return self._socket.sendall(data) or len(data)
        except socket.error as e:
            raise TransportError(f"TCP 写入失败：{e}")
    
    def read(self, size: int = 1024) -> bytes:
        """从 TCP socket 读取数据"""
        if not self._socket:
            raise TransportError("TCP 未连接")
        try:
            return self._socket.recv(size)
        except socket.error as e:
            raise TransportError(f"TCP 读取失败：{e}")
    
    def is_connected(self) -> bool:
        """检查 TCP 连接状态"""
        return self._connected and self._socket is not None
    
    @staticmethod
    def scan_printer(host: str, ports: list = None) -> Optional[Tuple[str, int]]:
        """
        扫描打印机可能开放的端口
        
        Args:
            host: 主机地址
            ports: 要扫描的端口列表，默认使用打印机常用端口
            
        Returns:
            Optional[Tuple[str, int]]: 找到的 (host, port) 或 None
        """
        if ports is None:
            ports = [9100, 515, 631, 8080, 80]  # 打印机常用端口
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    return (host, port)
            except Exception:
                continue
        return None


class TransportError(Exception):
    """通信层异常"""
    pass
