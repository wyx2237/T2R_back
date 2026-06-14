#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$ROOT_DIR/venv"

echo "=== 创建 Python 虚拟环境 ==="
python3 -m venv "$VENV_DIR"

echo "=== 激活虚拟环境 ==="
source "$VENV_DIR/bin/activate"

echo "=== 升级 pip ==="
pip install --upgrade pip -q

echo "=== 安装依赖包 ==="
pip install -r "$ROOT_DIR/requirements.txt"

echo ""
echo "虚拟环境构建完成！"
echo "激活命令: source $VENV_DIR/bin/activate"
