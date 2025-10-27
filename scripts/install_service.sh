#!/usr/bin/env bash
set -euo pipefail

# 简单安装脚本：将本项目的 systemd 单元复制到 /etc/systemd/system 并启用
# 可选：自动创建持久化日志目录，保证重启后也能用 journalctl 查看历史日志

SERVICE_SRC="$(cd "$(dirname "$0")"/.. && pwd)/systemd/poetry-camera.service"
SERVICE_DST="/etc/systemd/system/poetry-camera.service"

if [[ $EUID -ne 0 ]]; then
  echo "请用 sudo 运行：sudo $0"
  exit 1
fi

if [[ ! -f "$SERVICE_SRC" ]]; then
  echo "未找到服务模板：$SERVICE_SRC"
  exit 1
fi

# 复制服务文件
cp "$SERVICE_SRC" "$SERVICE_DST"
chmod 644 "$SERVICE_DST"

# 可选：开启持久化 journal（保留跨重启日志）
mkdir -p /var/log/journal
systemd-tmpfiles --create --prefix /var/log/journal || true

# 载入并启用
systemctl daemon-reload
systemctl enable poetry-camera.service
systemctl restart poetry-camera.service

# 显示状态
systemctl status poetry-camera.service --no-pager -l || true

echo
echo "已安装并启动 poetry-camera.service。"
echo "查看实时日志： sudo journalctl -fu poetry-camera.service"
echo "查看上一次启动的日志： sudo journalctl -b -1 -u poetry-camera.service"
