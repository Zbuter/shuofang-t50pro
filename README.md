# 硕方 T50Pro 标签打印机控制程序

硕方 T50Pro 标签打印机的 Python 控制库，支持 USB/蓝牙/网络通信，提供完整的 TSPL 指令集封装。

## 功能特性

- ✅ **多通信方式**: USB 串口、蓝牙 BLE、TCP 网络
- ✅ **完整 TSPL 支持**: 文本、条形码、二维码、图像、图形
- ✅ **打印任务管理**: 链式 API、模板系统
- ✅ **状态查询**: 打印机状态实时监控
- ✅ **跨平台**: Windows/Linux/macOS

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础示例

```python
from printer_t50pro import Printer, PrintJob

# 创建打印机实例（USB 连接）
printer = Printer.usb("/dev/ttyUSB0")

# 连接
printer.connect()

# 创建打印任务
job = PrintJob(50, 30)  # 50mm x 30mm 标签
job.add_text("设备标签", 15, 5, size=2)
job.add_text("名称：交换机 A", 5, 15)
job.add_qrcode("SN:SW2024001", 35, 12)

# 打印
printer.print_job(job, count=1)

# 断开
printer.disconnect()
```

### 快捷打印

```python
# 文本打印
printer.print_text("Hello World", x=10, y=10, size=2)

# 条形码打印
printer.print_barcode("1234567890", type="128", x=10, y=30)

# 二维码打印
printer.print_qrcode("https://example.com", x=10, y=50)
```

### 模板系统

```python
from printer_t50pro import Template

# 创建模板
template = Template("device_label", 50, 30)
template.add_text_field("name", 5, 5, size=2)
template.add_qrcode_field("sn", 30, 10)

# 使用模板
job = template.render({
    "name": "核心交换机",
    "sn": "SN:H3C2024001"
})

printer.print_job(job)
```

## 通信方式

### USB 连接

```python
printer = Printer.usb("/dev/ttyUSB0")  # Linux/macOS
printer = Printer.usb("COM3")          # Windows
```

### 蓝牙连接

```python
printer = Printer.ble("AA:BB:CC:DD:EE:FF")
```

### 网络连接

```python
printer = Printer.tcp("192.168.1.100", port=9100)
```

## API 参考

### Printer 类

| 方法 | 说明 |
|------|------|
| `Printer.usb(port, baudrate)` | 创建 USB 打印机实例 |
| `Printer.ble(address)` | 创建蓝牙打印机实例 |
| `Printer.tcp(host, port)` | 创建网络打印机实例 |
| `connect()` | 连接打印机 |
| `disconnect()` | 断开连接 |
| `print_job(job, count)` | 打印任务 |
| `print_text(...)` | 快捷打印文本 |
| `print_barcode(...)` | 快捷打印条形码 |
| `print_qrcode(...)` | 快捷打印二维码 |
| `print_image(...)` | 快捷打印图片 |
| `get_status()` | 获取打印机状态 |
| `calibrate()` | 校准标签纸 |
| `reset()` | 重置打印机 |

### PrintJob 类

| 方法 | 说明 |
|------|------|
| `PrintJob(width, height, gap)` | 创建打印任务 |
| `add_text(content, x, y, ...)` | 添加文本 |
| `add_barcode(content, x, y, ...)` | 添加条形码 |
| `add_qrcode(content, x, y, ...)` | 添加二维码 |
| `add_image(image, x, y, ...)` | 添加图片 |
| `add_box(x, y, width, height)` | 添加矩形框 |
| `add_line(x1, y1, x2, y2)` | 添加直线 |
| `set_speed(speed)` | 设置打印速度 |
| `set_density(density)` | 设置打印浓度 |
| `render()` | 渲染为 TSPL 指令 |

### TSPLCommand 类

支持所有标准 TSPL 指令：
- `size()`, `gap()`, `speed()`, `density()`
- `direction()`, `reference()`, `cls()`
- `text()`, `barcode()`, `qrcode()`, `bitmap()`
- `box()`, `line()`, `reverse()`
- `print()`, `query_status()`, `calibrate()`

## 运行示例

```bash
# 运行打印示例
python scripts/demo_print.py

# 扫描设备
python scripts/device_scan.py
```

## 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_tspl.py -v
```

## 项目结构

```
printer-t50pro/
├── docs/                    # 文档
│   ├── 技术调研报告.md
│   └── 程序架构设计.md
├── src/                     # 源代码
│   ├── printer.py           # 主打印机类
│   ├── transport/           # 通信层
│   │   ├── base.py
│   │   ├── usb_transport.py
│   │   ├── ble_transport.py
│   │   └── tcp_transport.py
│   ├── driver/              # 驱动层
│   │   ├── tspl.py
│   │   ├── image.py
│   │   └── status.py
│   └── service/             # 服务层
│       ├── job.py
│       ├── template.py
│       └── device.py
├── tests/                   # 单元测试
│   ├── test_tspl.py
│   ├── test_image.py
│   ├── test_status.py
│   ├── test_job.py
│   └── test_template.py
├── scripts/                 # 示例脚本
│   ├── demo_print.py
│   └── device_scan.py
├── requirements.txt
└── README.md
```

## 支持的条形码类型

- CODE39
- CODE128
- EAN13 / EAN8
- UPCA / UPCE
- ITF (Interleaved 2 of 5)
- CODABAR
- CODE93

## 二维码纠错级别

- L (7%)
- M (15%) - 默认
- Q (25%)
- H (30%)

## 故障排查

### 无法连接 USB 设备

1. 检查设备是否已连接
2. 确认端口号正确（`/dev/ttyUSB0` 或 `COM3`）
3. 检查权限（Linux 需要添加到 dialout 组）

```bash
# Linux 添加用户到 dialout 组
sudo usermod -a -G dialout $USER
```

### 蓝牙连接失败

1. 确认打印机处于配对模式
2. 检查蓝牙地址是否正确
3. 确保系统蓝牙已启用

### 打印内容不清晰

调整打印浓度：
```python
job.set_density(10)  # 1-15，越大越深
```

### 中文乱码

确保使用正确的字体和编码：
```python
job.add_text("中文", x, y, font="SIMSUN.TTF")
```

## 技术栈

- Python 3.8+
- pyserial (串口通信)
- bleak (蓝牙 BLE)
- Pillow (图像处理)
- python-barcode (条形码)
- qrcode (二维码)

## 许可证

MIT License

## 作者

工部·开发组  
尚书省·JJC-20260324-001

## 版本

v1.0.0 - 2026-03-24
