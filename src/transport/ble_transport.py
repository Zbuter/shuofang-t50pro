"""蓝牙 BLE 通信实现"""

import asyncio
from typing import Optional, List, Dict
from .base import Transport


class BLETransport(Transport):
    """蓝牙 BLE 通信实现"""
    
    # 硕方打印机 BLE 服务 UUID（需根据实际设备确认）
    SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
    WRITE_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
    READ_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"
    
    def __init__(self, address: str, timeout: float = 5.0):
        """
        初始化 BLE 传输
        
        Args:
            address: 蓝牙设备地址（如 'AA:BB:CC:DD:EE:FF'）
            timeout: 读写超时时间（秒）
        """
        super().__init__(timeout)
        self.address = address
        self._client = None
        self._write_char = None
        self._read_char = None
        self._read_buffer = bytearray()
        self._read_event = asyncio.Event()
    
    async def connect(self) -> bool:
        """建立 BLE 连接"""
        try:
            from bleak import BleakClient
            
            self._client = BleakClient(self.address, timeout=self.timeout)
            await self._client.connect()
            
            # 发现服务和特征值
            services = self._client.services
            for service in services:
                if service.uuid.lower() == self.SERVICE_UUID.lower():
                    for char in service.characteristics:
                        if char.uuid.lower() == self.WRITE_UUID.lower():
                            self._write_char = char
                        elif char.uuid.lower() == self.READ_UUID.lower():
                            self._read_char = char
                            # 设置通知回调
                            await self._client.start_notify(char, self._notification_handler)
                    break
            
            if not self._write_char:
                raise TransportError("未找到写入特征值")
            
            self._connected = True
            return True
            
        except Exception as e:
            raise TransportError(f"BLE 连接失败：{e}")
    
    async def disconnect(self) -> None:
        """断开 BLE 连接"""
        if self._client:
            try:
                if self._read_char:
                    await self._client.stop_notify(self._read_char.uuid)
                await self._client.disconnect()
            except Exception:
                pass
            finally:
                self._client = None
                self._connected = False
    
    async def write(self, data: bytes) -> int:
        """写入数据到 BLE 设备"""
        if not self._client or not self._client.is_connected:
            raise TransportError("BLE 未连接")
        if not self._write_char:
            raise TransportError("未找到写入特征值")
        
        try:
            # BLE 通常有 MTU 限制，需要分片发送
            mtu = self._client.mtu_size or 20
            total_written = 0
            
            for i in range(0, len(data), mtu - 3):
                chunk = data[i:i + mtu - 3]
                await self._client.write_gatt_char(self._write_char.uuid, chunk, response=True)
                total_written += len(chunk)
                await asyncio.sleep(0.01)  # 避免发送过快
            
            return total_written
        except Exception as e:
            raise TransportError(f"BLE 写入失败：{e}")
    
    async def read(self, size: int = 1024) -> bytes:
        """从 BLE 设备读取数据"""
        if not self._client or not self._client.is_connected:
            raise TransportError("BLE 未连接")
        
        try:
            # 等待数据到达
            try:
                await asyncio.wait_for(self._read_event.wait(), timeout=self.timeout)
            except asyncio.TimeoutError:
                return b""
            
            # 返回缓冲区数据
            result = bytes(self._read_buffer[:size])
            self._read_buffer = self._read_buffer[size:]
            return result
        except Exception as e:
            raise TransportError(f"BLE 读取失败：{e}")
    
    def _notification_handler(self, sender, data: bytearray):
        """BLE 通知回调"""
        self._read_buffer.extend(data)
        self._read_event.set()
    
    def is_connected(self) -> bool:
        """检查 BLE 连接状态"""
        return self._connected and self._client is not None and self._client.is_connected
    
    @staticmethod
    async def scan_devices(timeout: int = 5) -> List[Dict]:
        """
        扫描附近的 BLE 设备
        
        Args:
            timeout: 扫描超时时间（秒）
            
        Returns:
            List[Dict]: 设备列表，包含 address 和 name
        """
        try:
            from bleak import BleakScanner
            
            devices = await BleakScanner.discover(timeout=timeout)
            return [
                {"address": d.address, "name": d.name or "Unknown"}
                for d in devices
            ]
        except Exception as e:
            raise TransportError(f"BLE 扫描失败：{e}")
    
    def connect_sync(self) -> bool:
        """同步方式连接（用于非异步环境）"""
        return asyncio.run(self.connect())
    
    def disconnect_sync(self):
        """同步方式断开连接"""
        asyncio.run(self.disconnect())
    
    def write_sync(self, data: bytes) -> int:
        """同步方式写入"""
        return asyncio.run(self.write(data))
    
    def read_sync(self, size: int = 1024) -> bytes:
        """同步方式读取"""
        return asyncio.run(self.read(size))


class TransportError(Exception):
    """通信层异常"""
    pass
