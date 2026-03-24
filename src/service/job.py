"""打印任务服务"""

from typing import List, Dict, Any, Optional, Union
from PIL import Image
import json


class PrintJob:
    """打印任务 - 构建和管理打印内容"""
    
    def __init__(self, width: int, height: int, gap: int = 2):
        """
        初始化打印任务
        
        Args:
            width: 标签宽度（mm）
            height: 标签高度（mm）
            gap: 标签间隙（mm）
        """
        self.width = width
        self.height = height
        self.gap = gap
        self.elements: List[Dict[str, Any]] = []
        self.speed: int = 2
        self.density: int = 8
        self.direction: int = 0
        self.reference_x: int = 0
        self.reference_y: int = 0
    
    def add_text(self, content: str, x: int, y: int,
                 font: str = "1", size: int = 1,
                 rotation: int = 0) -> 'PrintJob':
        """
        添加文本元素
        
        Args:
            content: 文本内容
            x: X 坐标（mm）
            y: Y 坐标（mm）
            font: 字体
            size: 字体大小倍数
            rotation: 旋转角度
            
        Returns:
            self: 链式调用
        """
        self.elements.append({
            "type": "text",
            "content": content,
            "x": x,
            "y": y,
            "font": font,
            "size": size,
            "rotation": rotation
        })
        return self
    
    def add_barcode(self, content: str, x: int, y: int,
                    type: str = "128", height: int = 40,
                    readable: bool = True) -> 'PrintJob':
        """
        添加条形码元素
        
        Args:
            content: 条形码内容
            x: X 坐标（mm）
            y: Y 坐标（mm）
            type: 条形码类型（39/128/EAN13 等）
            height: 条形码高度
            readable: 是否显示可读文本
            
        Returns:
            self: 链式调用
        """
        self.elements.append({
            "type": "barcode",
            "content": content,
            "x": x,
            "y": y,
            "barcode_type": type,
            "height": height,
            "readable": 1 if readable else 0
        })
        return self
    
    def add_qrcode(self, content: str, x: int, y: int,
                   ecc: str = "M", size: int = 4) -> 'PrintJob':
        """
        添加二维码元素
        
        Args:
            content: 二维码内容
            x: X 坐标（mm）
            y: Y 坐标（mm）
            ecc: 纠错级别（L/M/Q/H）
            size: 模块大小
            
        Returns:
            self: 链式调用
        """
        self.elements.append({
            "type": "qrcode",
            "content": content,
            "x": x,
            "y": y,
            "ecc": ecc,
            "size": size
        })
        return self
    
    def add_image(self, image: Union[Image, str],
                  x: int, y: int,
                  max_width: int = None,
                  max_height: int = None) -> 'PrintJob':
        """
        添加图像元素
        
        Args:
            image: PIL Image 对象或文件路径
            x: X 坐标（mm）
            y: Y 坐标（mm）
            max_width: 最大宽度（mm）
            max_height: 最大高度（mm）
            
        Returns:
            self: 链式调用
        """
        # 如果是文件路径，加载图像
        if isinstance(image, str):
            from .driver.image import ImageConverter
            image = ImageConverter.from_file(image, max_width, max_height)
        
        self.elements.append({
            "type": "image",
            "image": image,
            "x": x,
            "y": y,
            "max_width": max_width,
            "max_height": max_height
        })
        return self
    
    def add_box(self, x: int, y: int, width: int, height: int,
                thickness: int = 1) -> 'PrintJob':
        """
        添加矩形框
        
        Args:
            x: X 坐标
            y: Y 坐标
            width: 宽度
            height: 高度
            thickness: 线宽
            
        Returns:
            self: 链式调用
        """
        self.elements.append({
            "type": "box",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "thickness": thickness
        })
        return self
    
    def add_line(self, x1: int, y1: int, x2: int, y2: int,
                 thickness: int = 1) -> 'PrintJob':
        """
        添加直线
        
        Args:
            x1: 起点 X
            y1: 起点 Y
            x2: 终点 X
            y2: 终点 Y
            thickness: 线宽
            
        Returns:
            self: 链式调用
        """
        self.elements.append({
            "type": "line",
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "thickness": thickness
        })
        return self
    
    def set_speed(self, speed: int) -> 'PrintJob':
        """设置打印速度"""
        self.speed = max(1, min(5, speed))
        return self
    
    def set_density(self, density: int) -> 'PrintJob':
        """设置打印浓度"""
        self.density = max(1, min(15, density))
        return self
    
    def set_direction(self, direction: int) -> 'PrintJob':
        """设置打印方向（0=正常，1=旋转 180 度）"""
        self.direction = direction
        return self
    
    def set_reference(self, x: int, y: int) -> 'PrintJob':
        """设置参考坐标"""
        self.reference_x = x
        self.reference_y = y
        return self
    
    def clear(self) -> 'PrintJob':
        """清空所有元素"""
        self.elements = []
        return self
    
    def render(self) -> str:
        """
        渲染为 TSPL 指令
        
        Returns:
            str: TSPL 指令序列
        """
        from ..driver.tspl import TSPLCommand
        
        tspl = TSPLCommand()
        commands = []
        
        # 基础设置
        commands.append(tspl.setup(self.width, self.height, self.gap))
        commands.append(tspl.speed(self.speed))
        commands.append(tspl.density(self.density))
        commands.append(tspl.direction(self.direction))
        commands.append(tspl.reference(self.reference_x, self.reference_y))
        
        # 渲染每个元素
        for elem in self.elements:
            cmd = self._render_element(elem, tspl)
            if cmd:
                commands.append(cmd)
        
        return "".join(commands)
    
    def _render_element(self, elem: Dict, tspl: TSPLCommand) -> Optional[str]:
        """渲染单个元素"""
        elem_type = elem.get("type")
        
        if elem_type == "text":
            return tspl.text(
                x=elem["x"],
                y=elem["y"],
                font=elem.get("font", "1"),
                rotation=elem.get("rotation", 0),
                x_mul=elem.get("size", 1),
                y_mul=elem.get("size", 1),
                content=elem["content"]
            )
        
        elif elem_type == "barcode":
            return tspl.barcode(
                x=elem["x"],
                y=elem["y"],
                type=elem.get("barcode_type", "128"),
                height=elem.get("height", 40),
                readable=elem.get("readable", 1),
                content=elem["content"]
            )
        
        elif elem_type == "qrcode":
            return tspl.qrcode(
                x=elem["x"],
                y=elem["y"],
                ecc=elem.get("ecc", "M"),
                size=elem.get("size", 4),
                content=elem["content"]
            )
        
        elif elem_type == "image":
            return tspl.bitmap(
                x=elem["x"],
                y=elem["y"],
                image=elem["image"]
            )
        
        elif elem_type == "box":
            return tspl.box(
                x=elem["x"],
                y=elem["y"],
                width=elem["width"],
                height=elem["height"],
                thickness=elem.get("thickness", 1)
            )
        
        elif elem_type == "line":
            return tspl.line(
                x1=elem["x1"],
                y1=elem["y1"],
                x2=elem["x2"],
                y2=elem["y2"],
                thickness=elem.get("thickness", 1)
            )
        
        return None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "width": self.width,
            "height": self.height,
            "gap": self.gap,
            "speed": self.speed,
            "density": self.density,
            "direction": self.direction,
            "reference": [self.reference_x, self.reference_y],
            "elements": [
                {k: v for k, v in elem.items() if k != "image"}
                for elem in self.elements
            ]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PrintJob':
        """从字典创建"""
        job = cls(
            width=data["width"],
            height=data["height"],
            gap=data.get("gap", 2)
        )
        job.speed = data.get("speed", 2)
        job.density = data.get("density", 8)
        job.direction = data.get("direction", 0)
        ref = data.get("reference", [0, 0])
        job.reference_x = ref[0]
        job.reference_y = ref[1]
        
        # 注意：从字典恢复时，图像元素需要重新加载
        job.elements = data.get("elements", [])
        
        return job
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PrintJob':
        """从 JSON 字符串创建"""
        return cls.from_dict(json.loads(json_str))
