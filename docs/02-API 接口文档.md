# 硕方 T50 Pro - API 接口文档

**版本**: v1.0  
**更新日期**: 2026-03-24  
**语言**: Python 3.8+

---

## 目录

1. [模块概览](#模块概览)
2. [T50ProPrinter 类](#t50proprinter-类)
3. [LabelTemplate 类](#labeltemplate-类)
4. [LabelPrinter 类](#labelprinter-类)
5. [SZPL 指令集参考](#szpl-指令集参考)
6. [错误处理](#错误处理)
7. [完整示例](#完整示例)

---

## 模块概览

项目包含两个核心模块：

| 模块 | 文件 | 说明 |
|------|------|------|
| `printer` | `printer.py` | 打印机蓝牙通信核心类 |
| `label_designer` | `label_designer.py` | 标签模板设计器 |

### 导入方式

```python
# 导入打印机核心类
from printer import T50ProPrinter

# 导入标签设计器
from label_designer import LabelTemplate, LabelPrinter, TextElement, QRCodeElement, BarcodeElement
```

---

## T50ProPrinter 类

打印机蓝牙通信核心类，提供底层打印指令发送功能。

### 类属性

```python
class T50ProPrinter:
    SERVICE_UUID = "000018f0-0000-1000-8000-00805f9b34fb"  # 蓝牙服务 UUID
    WRITE_UUID = "00002af1-0000-1000-8000-00805f9b34fb"    # 写入特征 UUID
    READ_UUID = "00002af2-0000-1000-8000-00805f9b34fb"     # 读取特征 UUID
    NOTIFY_UUID = "00002af3-0000-1000-8000-00805f9b34fb"   # 通知特征 UUID
```

### 构造函数

```python
def __init__(self)
```

**说明**: 初始化打印机实例，不建立连接。

**示例**:
```python
printer = T50ProPrinter()
```

---

### 实例属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `client` | `BleakClient` | 蓝牙客户端实例 |
| `address` | `str` | 打印机 MAC 地址 |
| `connected` | `bool` | 连接状态 |

---

### 方法详解

#### scan()

扫描附近的蓝牙设备，筛选打印机。

```python
async def scan(self, timeout: int = 5) -> List[dict]
```

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `timeout` | `int` | `5` | 扫描超时时间（秒） |

**返回值**: `List[dict]` - 打印机列表，每项包含：
- `name` (str): 设备名称
- `address` (str): MAC 地址
- `rssi` (int): 信号强度 (dBm)

**示例**:
```python
printers = await printer.scan(timeout=10)
for p in printers:
    print(f"{p['name']} - {p['address']} (RSSI: {p['rssi']})")
```

---

#### connect()

连接到指定打印机。

```python
async def connect(self, address: str) -> bool
```

**参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `address` | `str` | 打印机 MAC 地址或 UUID |

**返回值**: `bool` - 连接是否成功

**示例**:
```python
success = await printer.connect("XX:XX:XX:XX:XX:XX")
if success:
    print("连接成功")
```

---

#### disconnect()

断开打印机连接。

```python
async def disconnect(self)
```

**返回值**: 无

**示例**:
```python
await printer.disconnect()
```

---

#### send_command()

发送原始打印指令。

```python
async def send_command(self, command: bytes) -> bool
```

**参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `command` | `bytes` | SZPL 指令（字节串） |

**返回值**: `bool` - 发送是否成功

**示例**:
```python
cmd = b"SZPL\nCLS\nPRINT 1,1\n"
success = await printer.send_command(cmd)
```

---

#### print_text()

打印文字内容。

```python
async def print_text(self, text: str, font_size: int = 24, 
                     align: str = "left", bold: bool = False) -> bool
```

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text` | `str` | - | 要打印的文字 |
| `font_size` | `int` | `24` | 字体大小（像素） |
| `align` | `str` | `"left"` | 对齐方式：`left`/`center`/`right` |
| `bold` | `bool` | `False` | 是否粗体 |

**返回值**: `bool` - 打印是否成功

**示例**:
```python
# 打印粗体居中文字
await printer.print_text("产品标签", font_size=28, align="center", bold=True)

# 打印多行
await printer.print_text("型号：T50-Pro", font_size=20)
await printer.print_text("批次：2026-03", font_size=16)
```

---

#### print_qrcode()

打印二维码。

```python
async def print_qrcode(self, data: str, size: int = 3) -> bool
```

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data` | `str` | - | 二维码数据 |
| `size` | `int` | `3` | 二维码尺寸（1-10） |

**返回值**: `bool` - 打印是否成功

**示例**:
```python
# 打印网址二维码
await printer.print_qrcode("https://example.com", size=4)

# 打印 JSON 数据
import json
data = json.dumps({"id": "001", "name": "产品 A"})
await printer.print_qrcode(data, size=3)
```

---

#### print_barcode()

打印条形码。

```python
async def print_barcode(self, data: str, barcode_type: str = "code128", 
                        height: int = 50, wide: int = 2) -> bool
```

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data` | `str` | - | 条形码数据 |
| `barcode_type` | `str` | `"code128"` | 条码类型（见下表） |
| `height` | `int` | `50` | 条码高度（像素） |
| `wide` | `int` | `2` | 条码宽度倍数 |

**支持的条码类型**:

| 类型 | 值 | 说明 |
|------|-----|------|
| Code 128 | `code128` | 最常用，支持全 ASCII |
| Code 39 | `code39` | 字母数字，工业常用 |
| EAN-13 | `ean13` | 商品条码（13 位） |
| EAN-8 | `ean8` | 商品条码（8 位） |
| ITF | `itf` | 交叉 25 码 |
| Codabar | `codabar` | 库伦巴码 |
| UPC-A | `upca` | 北美商品码（12 位） |
| UPC-E | `upce` | 北美商品码（压缩） |

**返回值**: `bool` - 打印是否成功

**示例**:
```python
# 打印 Code 128 条码
await printer.print_barcode("1234567890", barcode_type="code128")

# 打印 EAN-13 商品码
await printer.print_barcode("6901234567892", barcode_type="ean13", height=60)
```

---

## LabelTemplate 类

标签模板设计器，支持组合多种元素。

### 构造函数

```python
def __init__(self, width: int = 40, height: int = 30)
```

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `width` | `int` | `40` | 标签宽度（mm） |
| `height` | `int` | `30` | 标签高度（mm） |

**示例**:
```python
# 创建标准标签模板
template = LabelTemplate(width=40, height=30)

# 创建小标签模板
template = LabelTemplate(width=24, height=15)
```

---

### 方法详解

#### add_text()

添加文字元素到模板。

```python
def add_text(self, text: str, x: int = 10, y: int = 10, 
             font_size: int = 24, bold: bool = False, align: str = "left") -> self
```

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text` | `str` | - | 文字内容 |
| `x` | `int` | `10` | X 坐标（mm） |
| `y` | `int` | `10` | Y 坐标（mm） |
| `font_size` | `int` | `24` | 字体大小 |
| `bold` | `bool` | `False` | 是否粗体 |
| `align` | `str` | `"left"` | 对齐方式 |

**返回值**: `self` - 支持链式调用

**示例**:
```python
template.add_text("标题", x=10, y=10, font_size=24, bold=True)
       .add_text("副标题", x=10, y=30, font_size=16)
```

---

#### add_qrcode()

添加二维码元素到模板。

```python
def add_qrcode(self, data: str, x: int = 10, y: int = 10, size: int = 3) -> self
```

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data` | `str` | - | 二维码数据 |
| `x` | `int` | `10` | X 坐标（mm） |
| `y` | `int` | `10` | Y 坐标（mm） |
| `size` | `int` | `3` | 二维码尺寸 |

**返回值**: `self`

**示例**:
```python
template.add_qrcode("https://example.com", x=10, y=50, size=4)
```

---

#### add_barcode()

添加条形码元素到模板。

```python
def add_barcode(self, data: str, x: int = 10, y: int = 10,
                barcode_type: str = "code128", height: int = 50) -> self
```

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data` | `str` | - | 条形码数据 |
| `x` | `int` | `10` | X 坐标（mm） |
| `y` | `int` | `10` | Y 坐标（mm） |
| `barcode_type` | `str` | `"code128"` | 条码类型 |
| `height` | `int` | `50` | 条码高度 |

**返回值**: `self`

**示例**:
```python
template.add_barcode("1234567890", x=10, y=80, barcode_type="code128")
```

---

#### clear()

清空模板所有元素。

```python
def clear(self) -> self
```

**返回值**: `self`

**示例**:
```python
template.clear()  # 清空后重新设计
```

---

#### preview()

预览模板内容（控制台输出）。

```python
def preview(self)
```

**返回值**: 无（打印到控制台）

**示例**:
```python
template.preview()
# 输出:
# 标签预览 (40mm x 30mm)
# ----------------------------------------
#   📝 文字：'标题' @ (10, 10) 字体:24 粗体:True
#   🔲 二维码：'https://...' @ (10, 50) 尺寸:4
#   📊 条形码：'1234567890' @ (10, 80) 类型:code128 高度:50
# ----------------------------------------
```

---

## LabelPrinter 类

高级打印控制器，整合模板和打印功能。

### 构造函数

```python
def __init__(self)
```

**示例**:
```python
printer = LabelPrinter()
```

---

### 方法详解

#### connect()

连接打印机。

```python
async def connect(self, address: str) -> bool
```

**参数**: `address` (str) - 打印机地址  
**返回值**: `bool` - 连接状态

---

#### disconnect()

断开连接。

```python
async def disconnect(self)
```

---

#### print_template()

打印标签模板。

```python
async def print_template(self, template: LabelTemplate, copies: int = 1) -> bool
```

**参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `template` | `LabelTemplate` | - | 标签模板 |
| `copies` | `int` | `1` | 打印份数 |

**返回值**: `bool` - 打印是否成功

**示例**:
```python
await printer.print_template(template, copies=3)  # 打印 3 份
```

---

## SZPL 指令集参考

硕方自有打印指令集（SZPL = Shuofang Zebra Programming Language）。

### 基础指令

| 指令 | 格式 | 说明 |
|------|------|------|
| `SIZE` | `SIZE width,height` | 设置标签尺寸（mm） |
| `CLS` | `CLS` | 清除打印缓冲区 |
| `PRINT` | `PRINT n,m` | 打印 n 份，重复 m 次 |

### 文字指令

```
TEXT x,y,font,rotation,width,height,"content"
```

**参数**:
- `x,y`: 起始坐标
- `font`: 字体名称（SIMSUN=宋体）
- `rotation`: 旋转角度（0/90/180/270）
- `width`: 字宽倍数
- `height`: 字高倍数
- `content`: 文字内容

**示例**:
```
TEXT 50,20,"SIMSUN",0,1,2,"Hello"
```

### 二维码指令

```
QRCODE x,y,level,width,"data"
```

**参数**:
- `x,y`: 起始坐标
- `level`: 纠错级别（L/M/Q/H）
- `width`: 模块宽度
- `data`: 二维码数据

**示例**:
```
QRCODE 30,50,M,3,"https://example.com"
```

### 条形码指令

```
BARCODE x,y,type,height,human_readable,rotation,"data"
```

**参数**:
- `x,y`: 起始坐标
- `type`: 条码类型（见 API 文档）
- `height`: 条码高度
- `human_readable`: 是否显示下方文字（0/1）
- `rotation`: 旋转角度
- `data`: 条码数据

**示例**:
```
BARCODE 30,80,"128",50,1,0,"1234567890"
```

---

## 错误处理

### 异常类型

| 异常 | 触发条件 | 处理方式 |
|------|----------|----------|
| `ConnectionError` | 蓝牙连接失败 | 检查配对/重试 |
| `TimeoutError` | 操作超时 | 增加 timeout/检查设备 |
| `ValueError` | 参数错误 | 检查参数范围 |

### 推荐实践

```python
from printer import T50ProPrinter

async def safe_print():
    printer = T50ProPrinter()
    try:
        # 连接
        if not await printer.connect("XX:XX:XX:XX:XX:XX"):
            print("连接失败")
            return
        
        # 打印
        success = await printer.print_text("Hello")
        if not success:
            print("打印失败")
            
    except ConnectionError as e:
        print(f"连接错误：{e}")
    except Exception as e:
        print(f"未知错误：{e}")
    finally:
        # 确保断开连接
        await printer.disconnect()
```

---

## 完整示例

### 示例 1: 打印产品标签

```python
#!/usr/bin/env python3
"""打印产品标签示例"""
import asyncio
from label_designer import LabelTemplate, LabelPrinter

async def main():
    # 创建模板
    template = LabelTemplate(width=40, height=30)
    
    # 设计标签
    template.add_text("产品名称", x=10, y=10, font_size=18, bold=True)
    template.add_text("硕方 T50 Pro", x=10, y=30, font_size=16)
    template.add_text("型号：TS-2024", x=10, y=50, font_size=14)
    template.add_qrcode("SN:T50-2024-001", x=10, y=70, size=3)
    
    # 预览
    template.preview()
    
    # 打印
    printer = LabelPrinter()
    if await printer.connect("XX:XX:XX:XX:XX:XX"):
        await printer.print_template(template, copies=5)
        await printer.disconnect()
        print("✅ 打印完成")
    else:
        print("❌ 连接失败")

asyncio.run(main())
```

### 示例 2: 批量打印资产标签

```python
#!/usr/bin/env python3
"""批量打印资产标签"""
import asyncio
from printer import T50ProPrinter

ASSETS = [
    {"id": "ZC-001", "name": "笔记本电脑", "dept": "IT 部"},
    {"id": "ZC-002", "name": "显示器", "dept": "设计部"},
    {"id": "ZC-003", "name": "打印机", "dept": "行政部"},
]

async def print_asset_label(printer, asset):
    """打印单个资产标签"""
    # 资产编号
    await printer.print_text(f"资产编号：{asset['id']}", font_size=16, bold=True)
    # 资产名称
    await printer.print_text(asset['name'], font_size=20, align="center")
    # 使用部门
    await printer.print_text(f"使用部门：{asset['dept']}", font_size=14)
    # 二维码（包含完整信息）
    import json
    qr_data = json.dumps(asset, ensure_ascii=False)
    await printer.print_qrcode(qr_data, size=3)

async def main():
    printer = T50ProPrinter()
    
    if await printer.connect("XX:XX:XX:XX:XX:XX"):
        for asset in ASSETS:
            print(f"正在打印：{asset['id']}")
            await print_asset_label(printer, asset)
            await asyncio.sleep(0.5)  # 等待打印完成
        
        await printer.disconnect()
        print(f"✅ 完成 {len(ASSETS)} 个资产标签打印")
    else:
        print("❌ 无法连接打印机")

asyncio.run(main())
```

---

**礼部 编制** | 尚书省 审定 | 任务 ID: JJC-20260324-001
