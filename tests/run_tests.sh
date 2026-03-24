#!/bin/bash
# 硕方 T50Pro 标签打印机控制程序 - 测试运行脚本
# 任务 ID: JJC-20260324-001
# 负责部门：刑部

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="$PROJECT_DIR/reports"

echo "=========================================="
echo "  硕方 T50Pro 打印机控制程序 - 测试套件"
echo "  任务 ID: JJC-20260324-001"
echo "  负责部门：刑部"
echo "=========================================="
echo ""

# 创建报告目录
mkdir -p "$REPORTS_DIR"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 python3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"
echo ""

# 检查 pytest
if ! python3 -m pytest --version &> /dev/null; then
    echo "⚠️  未安装 pytest，正在安装..."
    pip3 install pytest pytest-html --user
fi

# 切换到项目目录
cd "$PROJECT_DIR"

echo "📁 项目目录：$PROJECT_DIR"
echo ""

# 运行测试
echo "🚀 开始执行测试..."
echo ""

python3 -m pytest tests/test_printer.py \
    -v \
    --tb=short \
    --html="$REPORTS_DIR/test_report.html" \
    --self-contained-html \
    2>&1 | tee "$REPORTS_DIR/test_output.log"

echo ""
echo "=========================================="
echo "  测试完成"
echo "=========================================="
echo ""
echo "📊 测试报告：$REPORTS_DIR/test_report.html"
echo "📝 测试日志：$REPORTS_DIR/test_output.log"
echo ""

# 显示测试摘要
echo "📈 测试摘要:"
grep -E "(PASSED|FAILED|SKIPPED|ERROR)" "$REPORTS_DIR/test_output.log" | tail -20 || true

echo ""
echo "✅ 刑部测试完成"
