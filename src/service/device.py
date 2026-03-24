"""设备管理服务"""

from typing import List, Dict, Optional, Union
from ..transport import USBTransport, BLETransport, TCPTransport, Transport


class DeviceManager:
    """打印机设备管理器"""
    
    @staticmethod
    def scan_usb() -> List[Dict]:
        """
        扫描 USB 串口设备
        
        Returns:
            List[Dict]: 设备列表，包含 port 和 description
        """
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            
            devices = []
            for port in ports:
                device = {
                    "port": port.device,
                    "description": port.description,
                    "hwid": port.hwid,
                    "type": "usb"
                }
                devices.append(device)
            
            return devices
        except Exception as e:
            print(f"扫描 USB 设备失败：{e}")
            return []
    
    @staticmethod
    def scan_ble(timeout: int = 5) -> List[Dict]:
        """
        扫描 BLE 设备
        
        Args:
            timeout: 扫描超时时间（秒）
            
        Returns:
            List[Dict]: 设备列表，包含 address 和 name
        """
        try:
            import asyncio
            from ..transport.ble_transport import BLETransport
            
            async def scan():
                return await BLETransport.scan_devices(timeout)
            
            devices = asyncio.run(scan())
            
            # 标记为 BLE 类型
            for device in devices:
                device["type"] = "ble"
            
            return devices
        except Exception as e:
            print(f"扫描 BLE 设备失败：{e}")
            return []
    
    @staticmethod
    def scan_network(host: str) -> Optional[Dict]:
        """
        扫描网络打印机
        
        Args:
            host: 主机地址或主机名
            
        Returns:
            Optional[Dict]: 设备信息或 None
        """
        try:
            from ..transport.tcp_transport import TCPTransport
            
            result = TCPTransport.scan_printer(host)
            
            if result:
                return {
                    "host": result[0],
                    "port": result[1],
                    "type": "tcp"
                }
            return None
        except Exception as e:
            print(f"扫描网络打印机失败：{e}")
            return None
    
    @staticmethod
    def connect(port_or_address: str,
                transport_type: str = "usb",
                **kwargs) -> Transport:
        """
        连接打印机
        
        Args:
            port_or_address: 端口或地址
            transport_type: 传输类型（usb/ble/tcp）
            **kwargs: 其他参数
            
        Returns:
            Transport: 通信传输实例
            
        Examples:
            # USB 连接
            DeviceManager.connect("/dev/ttyUSB0", "usb")
            
            # BLE 连接
            DeviceManager.connect("AA:BB:CC:DD:EE:FF", "ble")
            
            # TCP 连接
            DeviceManager.connect("192.168.1.100", "tcp", port=9100)
        """
        if transport_type == "usb":
            baudrate = kwargs.get("baudrate", 115200)
            return USBTransport(port_or_address, baudrate)
        
        elif transport_type == "ble":
            return BLETransport(port_or_address)
        
        elif transport_type == "tcp":
            host = port_or_address
            port = kwargs.get("port", 9100)
            return TCPTransport(host, port)
        
        else:
            raise ValueError(f"未知的传输类型：{transport_type}")
    
    @staticmethod
    def auto_detect() -> Optional[Dict]:
        """
        自动检测打印机
        
        Returns:
            Optional[Dict]: 检测到的设备信息或 None
        """
        # 优先扫描 USB
        usb_devices = DeviceManager.scan_usb()
        if usb_devices:
            # 返回第一个 USB 设备
            return usb_devices[0]
        
        # 扫描 BLE
        ble_devices = DeviceManager.scan_ble(timeout=3)
        if ble_devices:
            # 尝试找到硕方设备（名称中包含 Supvan 或 T50）
            for device in ble_devices:
                name = device.get("name", "").lower()
                if "supvan" in name or "t50" in name or "label" in name:
                    return device
            
            # 返回第一个 BLE 设备
            return ble_devices[0]
        
        return None
    
    @staticmethod
    def get_printer_info(transport: Transport) -> Dict:
        """
        获取打印机信息
        
        Args:
            transport: 通信传输实例
            
        Returns:
            Dict: 打印机信息
        """
        from ..driver.tspl import TSPLCommand
        from ..driver.status import StatusParser
        
        info = {
            "connected": False,
            "model": "T50Pro",
            "status": "unknown"
        }
        
        try:
            # 连接并查询状态
            if transport.connect():
                info["connected"] = True
                
                # 发送状态查询
                tspl = TSPLCommand()
                transport.write(tspl.query_status().encode('gbk'))
                
                # 读取响应
                response = transport.read(256)
                
                if response:
                    status = StatusParser.parse(response)
                    info["status"] = str(status)
                    info["status_detail"] = {
                        "is_ready": status.is_ready,
                        "paper_status": status.paper_status,
                        "head_status": status.head_status
                    }
                
                transport.disconnect()
        except Exception as e:
            info["error"] = str(e)
        
        return info
