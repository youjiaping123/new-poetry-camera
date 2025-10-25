#!/bin/bash
# 诗歌相机安装脚本

set -e

echo "======================================"
echo "诗歌相机 - 安装脚本"
echo "======================================"

# 检查是否在树莓派上运行
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "警告: 此脚本设计用于树莓派"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 更新系统
echo ""
echo "1. 更新系统"
read -p "是否更新系统? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt-get update
    sudo apt-get upgrade -y
    echo "✓ 系统更新完成"
else
    echo "⏭️  跳过系统更新"
fi

# 安装系统依赖
echo ""
echo "2. 安装系统依赖"
read -p "是否安装系统依赖? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt-get install -y \
        python3-pip \
        python3-picamera2 \
        python3-venv \
        python3-full \
        git \
        build-essential
    echo "✓ 系统依赖安装完成"
else
    echo "⏭️  跳过系统依赖安装"
fi

# 创建虚拟环境
echo ""
echo "3. 创建虚拟环境"
if [ ! -d "venv" ]; then
    read -p "是否创建虚拟环境? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -m venv venv --system-site-packages
        echo "✓ 虚拟环境已创建"
    else
        echo "⏭️  跳过虚拟环境创建"
    fi
else
    echo "✓ 虚拟环境已存在，跳过"
fi

# 激活虚拟环境并安装Python依赖
echo ""
echo "4. 安装Python依赖"
read -p "是否安装Python依赖? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 激活虚拟环境
    if [ -d "venv" ]; then
        source venv/bin/activate
        
        # 确认虚拟环境已激活
        echo "当前Python路径: $(which python3)"
        echo "当前pip路径: $(which pip)"
        
        # 升级pip
        pip install --upgrade pip
        
        # 安装依赖
        echo "正在安装项目依赖..."
        pip install -r requirements.txt
        
        echo "✓ Python依赖安装完成"
    else
        echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    fi
else
    echo "⏭️  跳过Python依赖安装"
fi

# 配置环境变量
echo ""
echo "5. 配置环境变量"
if [ ! -f .env ]; then
    read -p "是否创建并编辑 .env 文件? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "已创建 .env 文件，请编辑并填入您的API密钥"
        echo ""
        read -p "按Enter键继续编辑 .env 文件..." 
        nano .env
        echo "✓ .env 文件配置完成"
    else
        cp .env.example .env
        echo "⏭️  已创建 .env 文件，但跳过编辑（请稍后手动编辑）"
    fi
else
    echo "✓ .env 文件已存在，跳过"
fi

# 配置树莓派硬件
echo ""
echo "6. 配置树莓派硬件..."
echo "需要启用以下功能:"
echo "  - 相机 (Camera)"
echo "  - 串口 (Serial Port)"
echo ""
read -p "是否打开 raspi-config 进行配置? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo raspi-config
fi

# 添加用户到必要的组
echo ""
echo "7. 配置用户权限"
read -p "是否配置用户权限（添加到 dialout 和 video 组）? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo usermod -a -G dialout $USER
    sudo usermod -a -G video $USER
    echo "✓ 用户已添加到 dialout 和 video 组"
else
    echo "⏭️  跳过用户权限配置"
fi

# 测试安装
echo ""
echo "8. 测试安装..."
echo "运行测试脚本以验证安装:"
echo "  - source venv/bin/activate"
echo "  - python3 tests/test_camera.py   # 测试相机"
echo "  - python3 tests/test_printer.py  # 测试打印机"
echo "  - python3 tests/test_button.py   # 测试按钮"
echo "  - python3 tests/test_full.py     # 完整测试"
echo ""
read -p "是否现在运行打印机测试? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 确保虚拟环境已激活
    source venv/bin/activate
    python3 tests/test_printer.py
fi

# 配置自动启动
echo ""
echo "9. 配置自动启动 (可选)"
read -p "是否配置开机自动运行? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    PROJECT_DIR=$(pwd)
    CRON_CMD="@reboot sleep 30 && cd $PROJECT_DIR && $PROJECT_DIR/venv/bin/python $PROJECT_DIR/main.py >> $PROJECT_DIR/errors.txt 2>&1"
    
    # 检查是否已经存在
    if crontab -l 2>/dev/null | grep -q "poetry-camera"; then
        echo "✓ cron任务已存在"
    else
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        echo "✓ 已添加cron任务"
    fi
fi

# 退出虚拟环境
deactivate

echo ""
echo "======================================"
echo "✓ 安装完成!"
echo "======================================"
echo ""
echo "下一步:"
echo "1. 重启树莓派使权限生效: sudo reboot"
echo "2. 重启后激活虚拟环境: source ~/poetry-camera/venv/bin/activate"
echo "3. 运行测试脚本验证功能"
echo "4. 运行主程序: python3 main.py"
echo ""
echo "快速启动命令:"
echo "  cd ~/poetry-camera && ./start.sh"
echo ""
echo "如有问题，请查看 README.md"
echo ""