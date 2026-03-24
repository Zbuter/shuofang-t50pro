#!/usr/bin/env python3
"""
硕方 T50Pro 打印示例脚本

演示如何使用 printer-t50pro 库进行基本打印操作
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from printer import Printer
from service.job import PrintJob
from service.template import Template


def demo_usb_print():
    """USB 打印示例"""
    print("=" * 50)
    print("USB 打印示例")
    print("=" * 50)
    
    try:
        # 创建打印机实例（根据实际情况修改端口）
        printer = Printer.usb("/dev/ttyUSB0")
        
        # 连接
        print("正在连接打印机...")
        printer.connect()
        print("连接成功!")
        
        # 创建打印任务
        job = PrintJob(50, 30)
        
        # 添加文本
        job.add_text("设备标签", 15, 5, font="1", size=2)
        job.add_text("名称：交换机 A", 5, 15, font="1", size=1)
        job.add_text("型号：SW-2024", 5, 22, font="1", size=1)
        
        # 添加二维码
        job.add_qrcode("SN:SW2024001", 35, 12, size=4)
        
        # 打印
        print("正在打印...")
        printer.print_job(job, count=1)
        print("打印完成!")
        
        # 断开
        printer.disconnect()
        
    except Exception as e:
        print(f"打印失败：{e}")


def demo_ble_print():
    """蓝牙打印示例"""
    print("=" * 50)
    print("蓝牙打印示例")
    print("=" * 50)
    
    try:
        # 创建蓝牙打印机实例（替换为实际地址）
        printer = Printer.ble("AA:BB:CC:DD:EE:FF")
        
        # 连接
        print("正在连接打印机...")
        printer.connect()
        print("连接成功!")
        
        # 快速打印文本
        printer.print_text(
            "蓝牙测试",
            x=15, y=10,
            size=2,
            width=50, height=30
        )
        
        # 断开
        printer.disconnect()
        print("打印完成!")
        
    except Exception as e:
        print(f"打印失败：{e}")


def demo_qrcode_print():
    """二维码打印示例"""
    print("=" * 50)
    print("二维码打印示例")
    print("=" * 50)
    
    try:
        printer = Printer.usb("/dev/ttyUSB0")
        printer.connect()
        
        # 打印二维码
        printer.print_qrcode(
            "https://example.com/device/123",
            x=10, y=10,
            ecc="M",
            size=5,
            width=50, height=50
        )
        
        printer.disconnect()
        print("二维码打印完成!")
        
    except Exception as e:
        print(f"打印失败：{e}")


def demo_barcode_print():
    """条形码打印示例"""
    print("=" * 50)
    print("条形码打印示例")
    print("=" * 50)
    
    try:
        printer = Printer.usb("/dev/ttyUSB0")
        printer.connect()
        
        # 打印 CODE128 条形码
        printer.print_barcode(
            "SN20240324001",
            barcode_type="128",
            x=5, y=10,
            height=40,
            width=50, height_mm=30
        )
        
        printer.disconnect()
        print("条形码打印完成!")
        
    except Exception as e:
        print(f"打印失败：{e}")


def demo_template_print():
    """模板打印示例"""
    print("=" * 50)
    print("模板打印示例")
    print("=" * 50)
    
    try:
        # 创建设备标签模板
        template = Template("device_label", 50, 30)
        template.description = "设备标签模板"
        
        # 添加字段
        template.add_text_field(
            "device_name",
            x=5, y=3,
            font="1", size=2,
            default="设备名称"
        )
        
        template.add_text_field(
            "device_model",
            x=5, y=12,
            font="1", size=1,
            default="型号"
        )
        
        template.add_qrcode_field(
            "serial_number",
            x=30, y=5,
            size=4,
            default="SN:XXXX"
        )
        
        # 使用模板渲染
        data = {
            "device_name": "核心交换机",
            "device_model": "H3C S6850",
            "serial_number": "SN:H3C2024001"
        }
        
        job = template.render(data)
        
        # 打印
        printer = Printer.usb("/dev/ttyUSB0")
        printer.connect()
        printer.print_job(job)
        printer.disconnect()
        
        print("模板打印完成!")
        
    except Exception as e:
        print(f"打印失败：{e}")


def demo_status_query():
    """状态查询示例"""
    print("=" * 50)
    print("状态查询示例")
    print("=" * 50)
    
    try:
        printer = Printer.usb("/dev/ttyUSB0")
        printer.connect()
        
        # 查询状态
        status = printer.get_status()
        
        print(f"打印机状态：{status}")
        print(f"  - 就绪：{status.is_ready}")
        print(f"  - 纸张：{status.paper_status}")
        print(f"  - 打印头：{status.head_status}")
        if status.head_temp:
            print(f"  - 温度：{status.head_temp}°C")
        
        printer.disconnect()
        
    except Exception as e:
        print(f"查询失败：{e}")


def demo_batch_print():
    """批量打印示例"""
    print("=" * 50)
    print("批量打印示例")
    print("=" * 50)
    
    try:
        printer = Printer.usb("/dev/ttyUSB0")
        printer.connect()
        
        # 批量打印设备标签
        devices = [
            {"name": "交换机 A", "sn": "SW001"},
            {"name": "交换机 B", "sn": "SW002"},
            {"name": "路由器 A", "sn": "RT001"},
        ]
        
        for i, device in enumerate(devices, 1):
            print(f"正在打印 {i}/{len(devices)}: {device['name']}")
            
            job = PrintJob(50, 30)
            job.add_text(device["name"], 10, 10, size=2)
            job.add_qrcode(device["sn"], 10, 20, size=3)
            
            printer.print_job(job)
        
        printer.disconnect()
        print(f"批量打印完成！共 {len(devices)} 个标签")
        
    except Exception as e:
        print(f"打印失败：{e}")


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║     硕方 T50Pro 标签打印机 - 示例程序          ║")
    print("║     Supvan T50Pro Label Printer Demo          ║")
    print("╚" + "=" * 48 + "╝")
    print()
    
    # 选择示例
    examples = [
        ("USB 打印文本和二维码", demo_usb_print),
        ("蓝牙打印", demo_ble_print),
        ("打印二维码", demo_qrcode_print),
        ("打印条形码", demo_barcode_print),
        ("模板打印", demo_template_print),
        ("查询打印机状态", demo_status_query),
        ("批量打印", demo_batch_print),
    ]
    
    print("请选择示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print("  0. 退出")
    print()
    
    try:
        choice = input("请输入选项 (0-7): ").strip()
        
        if choice == "0":
            print("退出")
            return
        
        idx = int(choice) - 1
        if 0 <= idx < len(examples):
            examples[idx][1]()
        else:
            print("无效选项")
    
    except KeyboardInterrupt:
        print("\n中断")
    except Exception as e:
        print(f"错误：{e}")


if __name__ == "__main__":
    main()
