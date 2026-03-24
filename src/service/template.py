"""模板管理服务"""

import json
import os
from typing import Dict, List, Any, Optional
from .job import PrintJob


class Template:
    """打印模板 - 可复用的标签设计"""
    
    def __init__(self, name: str, width: int, height: int):
        """
        初始化模板
        
        Args:
            name: 模板名称
            width: 标签宽度（mm）
            height: 标签高度（mm）
        """
        self.name = name
        self.width = width
        self.height = height
        self.fields: List[Dict[str, Any]] = []
        self.gap: int = 2
        self.description: str = ""
    
    def add_field(self, name: str, field_type: str,
                  x: int, y: int, **kwargs) -> 'Template':
        """
        添加字段
        
        Args:
            name: 字段名称
            field_type: 字段类型（text/barcode/qrcode/image）
            x: X 坐标
            y: Y 坐标
            **kwargs: 字段特定参数
            
        Returns:
            self: 链式调用
        """
        field = {
            "name": name,
            "type": field_type,
            "x": x,
            "y": y,
            "params": kwargs
        }
        self.fields.append(field)
        return self
    
    def add_text_field(self, name: str, x: int, y: int,
                       font: str = "1", size: int = 1,
                       default: str = "") -> 'Template':
        """添加文本字段"""
        return self.add_field(
            name=name,
            field_type="text",
            x=x,
            y=y,
            font=font,
            size=size,
            default=default
        )
    
    def add_barcode_field(self, name: str, x: int, y: int,
                          barcode_type: str = "128",
                          height: int = 40,
                          default: str = "") -> 'Template':
        """添加条形码字段"""
        return self.add_field(
            name=name,
            field_type="barcode",
            x=x,
            y=y,
            barcode_type=barcode_type,
            height=height,
            readable=True,
            default=default
        )
    
    def add_qrcode_field(self, name: str, x: int, y: int,
                         ecc: str = "M", size: int = 4,
                         default: str = "") -> 'Template':
        """添加二维码字段"""
        return self.add_field(
            name=name,
            field_type="qrcode",
            x=x,
            y=y,
            ecc=ecc,
            size=size,
            default=default
        )
    
    def render(self, data: Dict[str, Any]) -> PrintJob:
        """
        使用数据渲染模板
        
        Args:
            data: 字段数据字典
            
        Returns:
            PrintJob: 渲染后的打印任务
        """
        job = PrintJob(self.width, self.height, self.gap)
        
        for field in self.fields:
            field_name = field["name"]
            field_type = field["type"]
            params = field.get("params", {})
            
            # 获取字段值
            value = data.get(field_name, params.get("default", ""))
            
            if not value and value != 0:
                continue  # 跳过空值
            
            if field_type == "text":
                job.add_text(
                    content=str(value),
                    x=field["x"],
                    y=field["y"],
                    font=params.get("font", "1"),
                    size=params.get("size", 1),
                    rotation=params.get("rotation", 0)
                )
            
            elif field_type == "barcode":
                job.add_barcode(
                    content=str(value),
                    x=field["x"],
                    y=field["y"],
                    type=params.get("barcode_type", "128"),
                    height=params.get("height", 40),
                    readable=params.get("readable", True)
                )
            
            elif field_type == "qrcode":
                job.add_qrcode(
                    content=str(value),
                    x=field["x"],
                    y=field["y"],
                    ecc=params.get("ecc", "M"),
                    size=params.get("size", 4)
                )
            
            elif field_type == "image" and isinstance(value, str):
                job.add_image(
                    image=value,
                    x=field["x"],
                    y=field["y"],
                    max_width=params.get("max_width"),
                    max_height=params.get("max_height")
                )
        
        return job
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "gap": self.gap,
            "description": self.description,
            "fields": self.fields
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save(self, filepath: str = None) -> str:
        """
        保存模板到文件
        
        Args:
            filepath: 文件路径，默认使用模板名称
            
        Returns:
            str: 保存的文件路径
        """
        if filepath is None:
            filepath = f"{self.name}.tpl.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        
        return filepath
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Template':
        """从字典创建模板"""
        template = cls(
            name=data["name"],
            width=data["width"],
            height=data["height"]
        )
        template.gap = data.get("gap", 2)
        template.description = data.get("description", "")
        template.fields = data.get("fields", [])
        return template
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Template':
        """从 JSON 字符串创建模板"""
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def load(cls, filepath: str) -> 'Template':
        """从文件加载模板"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, template_dir: str = None):
        """
        初始化模板管理器
        
        Args:
            template_dir: 模板目录
        """
        self.template_dir = template_dir or "./templates"
        self.templates: Dict[str, Template] = {}
        
        # 创建模板目录
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
    
    def register(self, template: Template) -> None:
        """注册模板"""
        self.templates[template.name] = template
    
    def get(self, name: str) -> Optional[Template]:
        """获取模板"""
        return self.templates.get(name)
    
    def load_from_dir(self) -> List[str]:
        """
        从目录加载所有模板
        
        Returns:
            List[str]: 加载的模板名称列表
        """
        loaded = []
        
        if not os.path.exists(self.template_dir):
            return loaded
        
        for filename in os.listdir(self.template_dir):
            if filename.endswith('.tpl.json'):
                filepath = os.path.join(self.template_dir, filename)
                try:
                    template = Template.load(filepath)
                    self.register(template)
                    loaded.append(template.name)
                except Exception as e:
                    print(f"加载模板失败 {filename}: {e}")
        
        return loaded
    
    def list_templates(self) -> List[str]:
        """列出所有模板名称"""
        return list(self.templates.keys())
    
    def create_device_label_template(self) -> Template:
        """创建设备标签模板"""
        template = Template("device_label", 50, 30)
        template.description = "设备标签模板"
        
        template.add_text_field(
            name="device_name",
            x=5, y=3,
            font="1", size=2,
            default="设备名称"
        )
        
        template.add_text_field(
            name="device_model",
            x=5, y=10,
            font="1", size=1,
            default="型号"
        )
        
        template.add_qrcode_field(
            name="serial_number",
            x=30, y=5,
            size=4,
            default="SN:XXXX"
        )
        
        template.add_text_field(
            name="install_date",
            x=5, y=17,
            font="1", size=1,
            default="安装日期"
        )
        
        return template
    
    def create_cable_label_template(self) -> Template:
        """创建线缆标签模板"""
        template = Template("cable_label", 40, 20)
        template.description = "线缆标签模板"
        
        template.add_text_field(
            name="cable_from",
            x=2, y=2,
            font="1", size=1,
            default="From"
        )
        
        template.add_text_field(
            name="cable_to",
            x=2, y=10,
            font="1", size=1,
            default="To"
        )
        
        template.add_barcode_field(
            name="cable_id",
            x=25, y=5,
            barcode_type="39",
            height=30,
            default="C001"
        )
        
        return template
