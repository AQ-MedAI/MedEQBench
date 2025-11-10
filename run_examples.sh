#!/bin/bash
set -e

# 设置 Python 路径
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

# 运行评测
cd "${PROJECT_ROOT}"
opencompass configs/examples_config.py "$@"