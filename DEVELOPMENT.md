# 诗歌相机项目 - 开发文档

## 📋 项目概述

这是一个全新重构的诗歌相机项目，采用模块化设计，易于维护和扩展。

## 🏗️ 项目架构

### 核心设计理念

1. **模块化** - 每个功能独立封装为模块
2. **可测试** - 每个模块都有对应的测试脚本
3. **容错性** - 完善的错误处理和日志记录
4. **可配置** - 所有配置通过环境变量管理

### 目录结构

```
new-poetry-camera/
├── src/                      # 源代码目录
│   ├── __init__.py          # 包初始化
│   ├── config.py            # 配置管理（单例模式）
│   ├── camera.py            # 相机控制
│   ├── printer.py           # 打印机控制
│   ├── ai_service.py        # AI服务（图像识别+诗歌生成)
│   ├── gpio_controller.py   # GPIO控制（按钮+LED）
│   └── utils.py             # 工具函数
├── tests/                    # 测试脚本目录
│   ├── __init__.py
│   ├── test_camera.py       # 相机测试
│   ├── test_printer.py      # 打印机测试
│   ├── test_button.py       # 按钮测试
│   └── test_full.py         # 完整流程测试
├── data/                     # 数据目录（运行时创建）
│   ├── images/              # 拍摄的照片
│   ├── uploads/             # 上传的图片
│   └── processed/           # 已处理的图片
├── main.py                   # 主程序入口
├── requirements.txt          # Python依赖
├── .env.example             # 环境变量模板
├── .gitignore               # Git忽略规则
├── install.sh               # 自动安装脚本
├── README.md                # 完整文档
├── QUICKSTART.md            # 快速开始指南
└── LICENSE                  # 许可证
```

## 🔧 模块说明

### 1. config.py - 配置管理

**功能:**
- 从 `.env` 文件加载配置
- 验证必需的配置项
- 提供全局配置访问
- 自动创建必需的目录

**设计模式:** 单例模式

**使用示例:**
```python
from src.config import config

# 访问配置
print(config.serial_port)
print(config.camera_width)

# 验证配置
is_valid, errors = config.validate()
```

### 2. camera.py - 相机控制

**功能:**
- 初始化 Picamera2
- 拍摄照片
- 自动生成时间戳文件名

**设计模式:** 上下文管理器

**使用示例:**
```python
from src.camera import Camera

with Camera() as camera:
    image_path = camera.capture()
```

### 3. printer.py - 打印机控制

**功能:**
- 串口通信初始化
- ESC/POS 命令封装
- 自动文本换行
- 打印诗歌（带头部和脚注）

**使用示例:**
```python
from src.printer import ThermalPrinter

with ThermalPrinter() as printer:
    printer.print_poem("这是一首诗")
```

### 4. ai_service.py - AI服务

**功能:**
- 图像识别（Replicate BLIP-2）
- 诗歌生成（DeepSeek API）
- 自动重试机制

**使用示例:**
```python
from src.ai_service import AIService

ai = AIService()
poem = ai.process_image_to_poem(image_path)
```

### 5. gpio_controller.py - GPIO控制

**功能:**
- 按钮状态检测
- 短按/长按识别
- LED控制（开/关/闪烁）

**使用示例:**
```python
from src.gpio_controller import GPIOController

with GPIOController() as gpio:
    gpio.led_on()
    press_type = gpio.wait_for_button_press()
```

### 6. utils.py - 工具函数

**功能:**
- 文本换行（支持中文）
- 格式化头部和脚注
- 文本居中

## 🔄 主流程

```
启动程序
   ↓
初始化配置
   ↓
初始化GPIO → LED亮起（就绪）
   ↓
初始化打印机
   ↓
初始化相机
   ↓
等待按钮 ←─────────┐
   ↓                  │
短按检测             │
   ↓                  │
LED闪烁（开始）      │
   ↓                  │
拍摄照片             │
   ↓                  │
LED关闭（处理中）    │
   ↓                  │
图像识别             │
   ↓                  │
生成诗歌             │
   ↓                  │
LED亮起（打印中）    │
   ↓                  │
打印诗歌             │
   ↓                  │
LED闪烁（完成）      │
   ↓                  │
LED亮起（就绪）─────┘
   ↓
长按检测
   ↓
关闭所有组件
   ↓
退出程序
```

## 🎯 核心改进

### 相比旧版本的优势

1. **模块化设计**
   - 旧版: 所有代码混在一个文件
   - 新版: 每个功能独立模块，职责清晰

2. **错误处理**
   - 旧版: 错误处理不完整
   - 新版: 每个操作都有异常捕获和日志

3. **可测试性**
   - 旧版: 难以单独测试各组件
   - 新版: 每个模块都有独立测试脚本

4. **配置管理**
   - 旧版: 配置分散在代码中
   - 新版: 集中式配置管理，易于修改

5. **代码质量**
   - 旧版: 缺少文档和注释
   - 新版: 完整的文档字符串和类型提示

6. **资源管理**
   - 旧版: 资源清理不完整
   - 新版: 使用上下文管理器，自动清理资源

## 🚀 部署步骤

### 1. 准备工作

```bash
# 在树莓派上克隆项目
cd ~
git clone <your-repo-url> poetry-camera
cd poetry-camera
```

### 2. 安装

```bash
# 运行安装脚本
chmod +x install.sh
./install.sh
```

### 3. 配置

```bash
# 编辑环境变量
nano .env

# 填入API密钥
DEEPSEEK_API_KEY=your_key_here
REPLICATE_API_TOKEN=your_token_here
```

### 4. 测试

```bash
# 测试各个组件
python3 tests/test_printer.py
python3 tests/test_camera.py
python3 tests/test_button.py

# 完整测试
python3 tests/test_full.py
```

### 5. 运行

```bash
# 手动运行
python3 main.py

# 或重启（如果配置了自动启动）
sudo reboot
```

## 🐛 调试技巧

### 查看日志

```bash
# 实时查看日志
tail -f poetry-camera.log

# 查看错误
cat errors.txt
```

### 串口调试

```bash
# 列出可用串口
ls -l /dev/serial*
ls -l /dev/ttyAMA*

# 检查串口权限
groups  # 应该包含 dialout 组
```

### 相机调试

```bash
# 测试相机
libcamera-hello --list-cameras
libcamera-jpeg -o test.jpg
```

## 📝 开发指南

### 添加新功能

1. 在 `src/` 目录创建新模块
2. 实现功能类
3. 在 `tests/` 创建测试脚本
4. 在 `main.py` 中集成
5. 更新文档

### 修改配置

1. 在 `.env.example` 添加新配置项
2. 在 `src/config.py` 中读取配置
3. 更新文档说明配置用途

### 提交代码

```bash
# 添加文件
git add .

# 提交
git commit -m "描述你的修改"

# 推送
git push
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🙏 致谢

- 原始项目: [poetry-camera-rpi](https://github.com/carolynz/poetry-camera-rpi)
- Adafruit Thermal Printer Library
- Raspberry Pi Foundation

---

**项目版本:** 2.0.0  
**最后更新:** 2025-10-25
