# 测试目录说明

**任务 ID**: JJC-20260324-001  
**负责部门**: 刑部

---

## 目录结构

```
tests/
├── README.md           # 本文件
├── run_tests.sh        # 测试运行脚本
├── test_printer.py     # 主测试套件
└── fixtures/           # 测试数据（待创建）
    ├── sample_text.txt
    ├── sample_image.png
    └── sample_barcode.png
```

---

## 快速开始

### 安装依赖

```bash
pip3 install pytest pytest-html -U
```

### 运行测试

```bash
# 方式 1: 使用运行脚本
./run_tests.sh

# 方式 2: 直接使用 pytest
pytest test_printer.py -v

# 方式 3: 运行特定测试类
pytest test_printer.py::TestBasicFunctionality -v

# 方式 4: 运行单个测试用例
pytest test_printer.py::TestBasicFunctionality::test_tc_basic_001_printer_connect -v
```

### 生成报告

测试完成后，HTML 报告将生成在 `../reports/test_report.html`

---

## 测试用例说明

详见 `../docs/02-测试用例集.md`

---

## 添加新测试

1. 在 `test_printer.py` 中添加新的测试方法
2. 在 `../docs/02-测试用例集.md` 中更新测试用例文档
3. 运行测试验证

---

## 测试数据

待工部代码提交后，根据需要创建测试数据文件。

---

**刑部 谨呈**
