"""模板测试"""

import pytest
import sys
import os
import json
import tempfile

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from service.template import Template, TemplateManager


class TestTemplate:
    """模板测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.template = Template("test_template", 50, 30)
    
    def test_create_template(self):
        """测试创建模板"""
        assert self.template.name == "test_template"
        assert self.template.width == 50
        assert self.template.height == 30
        assert len(self.template.fields) == 0
    
    def test_add_field(self):
        """测试添加字段"""
        self.template.add_field("name", "text", 10, 10, font="1")
        
        assert len(self.template.fields) == 1
        assert self.template.fields[0]["name"] == "name"
        assert self.template.fields[0]["type"] == "text"
        assert self.template.fields[0]["x"] == 10
    
    def test_add_text_field(self):
        """测试添加文本字段"""
        self.template.add_text_field(
            "device_name",
            10, 10,
            font="1",
            size=2,
            default="设备名称"
        )
        
        field = self.template.fields[0]
        assert field["name"] == "device_name"
        assert field["type"] == "text"
        assert field["params"]["default"] == "设备名称"
    
    def test_add_barcode_field(self):
        """测试添加条形码字段"""
        self.template.add_barcode_field(
            "serial",
            10, 20,
            barcode_type="39",
            default="SN123"
        )
        
        field = self.template.fields[0]
        assert field["type"] == "barcode"
        assert field["params"]["barcode_type"] == "39"
    
    def test_add_qrcode_field(self):
        """测试添加二维码字段"""
        self.template.add_qrcode_field(
            "url",
            10, 20,
            ecc="H",
            size=5
        )
        
        field = self.template.fields[0]
        assert field["type"] == "qrcode"
        assert field["params"]["ecc"] == "H"
    
    def test_render_template(self):
        """测试渲染模板"""
        self.template.add_text_field("name", 10, 10, default="Default")
        self.template.add_qrcode_field("code", 10, 20)
        
        data = {
            "name": "Test Device",
            "code": "ABC123"
        }
        
        job = self.template.render(data)
        
        assert job.width == 50
        assert job.height == 30
        assert len(job.elements) == 2
    
    def test_render_with_missing_data(self):
        """测试渲染时数据缺失"""
        self.template.add_text_field("name", 10, 10, default="Default")
        self.template.add_text_field("model", 10, 20, default="Model")
        
        # 只提供部分数据
        data = {"name": "Test"}
        
        job = self.template.render(data)
        
        # 应该使用默认值
        assert len(job.elements) == 2
    
    def test_to_dict(self):
        """测试转换为字典"""
        self.template.add_text_field("name", 10, 10)
        self.template.description = "测试模板"
        
        data = self.template.to_dict()
        
        assert data["name"] == "test_template"
        assert data["width"] == 50
        assert data["description"] == "测试模板"
        assert len(data["fields"]) == 1
    
    def test_to_json(self):
        """测试转换为 JSON"""
        self.template.add_text_field("name", 10, 10)
        
        json_str = self.template.to_json()
        
        data = json.loads(json_str)
        assert data["name"] == "test_template"
    
    def test_save_and_load(self):
        """测试保存和加载"""
        self.template.add_text_field("name", 10, 10)
        self.template.add_qrcode_field("code", 10, 20)
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tpl.json', delete=False) as f:
            filepath = f.name
            f.write(self.template.to_json())
        
        try:
            # 加载
            loaded = Template.load(filepath)
            
            assert loaded.name == self.template.name
            assert len(loaded.fields) == 2
        finally:
            os.unlink(filepath)
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "name": "loaded_template",
            "width": 60,
            "height": 40,
            "gap": 3,
            "description": "加载的模板",
            "fields": [
                {
                    "name": "field1",
                    "type": "text",
                    "x": 10,
                    "y": 10,
                    "params": {}
                }
            ]
        }
        
        template = Template.from_dict(data)
        
        assert template.name == "loaded_template"
        assert template.width == 60
        assert len(template.fields) == 1


class TestTemplateManager:
    """模板管理器测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = TemplateManager(self.temp_dir)
    
    def teardown_method(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_manager(self):
        """测试创建管理器"""
        assert self.manager.template_dir == self.temp_dir
        assert len(self.manager.templates) == 0
    
    def test_register_template(self):
        """测试注册模板"""
        template = Template("test", 50, 30)
        self.manager.register(template)
        
        assert "test" in self.manager.templates
        assert self.manager.get("test") == template
    
    def test_get_template(self):
        """测试获取模板"""
        template = Template("test", 50, 30)
        self.manager.register(template)
        
        retrieved = self.manager.get("test")
        assert retrieved == template
        
        not_found = self.manager.get("nonexistent")
        assert not_found is None
    
    def test_list_templates(self):
        """测试列出模板"""
        t1 = Template("template1", 50, 30)
        t2 = Template("template2", 60, 40)
        
        self.manager.register(t1)
        self.manager.register(t2)
        
        names = self.manager.list_templates()
        
        assert "template1" in names
        assert "template2" in names
        assert len(names) == 2
    
    def test_create_device_label_template(self):
        """测试创建设备标签模板"""
        template = self.manager.create_device_label_template()
        
        assert template.name == "device_label"
        assert template.width == 50
        assert template.height == 30
        assert len(template.fields) > 0
    
    def test_create_cable_label_template(self):
        """测试创建线缆标签模板"""
        template = self.manager.create_cable_label_template()
        
        assert template.name == "cable_label"
        assert template.width == 40
        assert template.height == 20
        
        # 检查字段类型
        field_types = [f["type"] for f in template.fields]
        assert "text" in field_types
        assert "barcode" in field_types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
