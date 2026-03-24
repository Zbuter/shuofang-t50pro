# pytest 配置文件
# 任务 ID: JJC-20260324-001

import pytest

def pytest_configure(config):
    """配置 pytest"""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async"
    )
