#!/bin/bash
# Sealos 启动脚本 - 网易新闻API
set -e

echo "=== 安装依赖 ==="
pip install flask requests beautifulsoup4 lxml python-dateutil -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "=== 下载代码 ==="
wget -q https://raw.githubusercontent.com/ljx19900710/news-api/main/app.py -O /app/app.py

echo "=== 启动服务 ==="
cd /app && python app.py
