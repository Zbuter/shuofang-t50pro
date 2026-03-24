#!/usr/bin/env python3
"""
设备扫描脚本

扫描可用的打印机设备（USB/蓝牙/网络）
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from service.device import DeviceManager


def scan_usb():
    """扫描 USB 设备"""
    print("\n" + "=" * 50)
    print("扫描 USB 设备")
    print("=" * 50)
    
    devices = DeviceManager.scan_usb()
    
    if not devices:
        print("未找到 USB 设备")
        return
    
    for i, device in enumerate(devices, 1):
        print(f"\n[{i}] {device['port']}")
        print(f"    描述：{device['description']}")
        print(f"    硬件 ID: {device['hwid']}")
        print(f"    类型：{device['type']}")


def scan_ble():
    """扫描 BLE 设备"""
    print("\n" + "=" * 50)
    print("扫描 BLE 设备")
    print("正在搜索... (可能需要几秒)")
    print("=" * 50)
    
    devices = DeviceManager.scan_ble(timeout=5)
    
    if not devices:
        print("未找到 BLE 设备")
        return
    
    for i, device in enumerate(devices, 1):
        print(f"\n[{i}] {device['address']}")
        print(f"    名称：{device['name']}")
        print(f"    类型：{device['type']}")


def scan_network():
    """扫描网络打印机"""
    print("\n" + "=" * 50)
    print("扫描网络打印机")
    print("=" * 50)
    
    host = input("请输入主机地址 (或按回车跳过): ").strip()
    
    if not host:
        print("跳过")
        return
    
    device = DeviceManager.scan_network(host)
    
    if device:
        print(f"\n找到打印机:")
        print(f"    地址：{device['host']}")
        print(f"    端口：{device['port']}")
        print(f"    类型：{device['type']}")
    else:
        print("未找到网络打印机")


def auto_detect():
    """自动检测"""
    print("\n" + "=" * 50)
    print("自动检测打印机")
    print("=" * 50)
    
    device = DeviceManager.auto_detect()
    
    if device:
        print("\n找到打印机:")
        for key, value in device.items():
            print(f"    {key}: {value}")
    else:
        print("未自动检测到打印机")


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║     硕方 T50Pro - 设备扫描工具                 ║")
    print("╚" + "=" * 48 + "╝")
    
    while True:
        print("\n请选择操作:")
        print("  1. 扫描 USB 设备")
        print("  2. 扫描 BLE 设备")
        print("  3. 扫描网络打印机")
        print("  4. 自动检测")
        print("  0. 退出")
        
        try:
            choice = input("\n请输入选项 (0-4): ").strip()
            
            if choice == "0":
                print("退出")
                break
            elif choice == "1":
                scan_usb()
            elif choice == "2":
                scan_ble()
            elif choice == "3":
                scan_network()
            elif choice == "4":
                auto_detect()
            else:
                print("无效选项")
        
        except KeyboardInterrupt:
            print("\n中断")
            break
        except Exception as e:
            print(f"错误：{e}")


if __name__ == "__main__":
    main()
