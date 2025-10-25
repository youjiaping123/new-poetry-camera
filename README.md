# 诗歌相机 (Poetry Camera)

一台能看懂世界并为所见之物创作诗歌的智能相机。

## 📸 项目简介

这是一个基于树莓派的智能相机项目，它能够：
- 📷 拍摄照片
- 🤖 使用 AI (BLIP-2 + DeepSeek) 理解图像内容
- ✍️ 根据图像生成优美的中文诗歌
- 🖨️ 用热敏打印机打印诗歌

![Poetry Camera Demo](https://via.placeholder.com/800x400?text=Poetry+Camera+Demo)

## 🛠️ 硬件要求

- **Raspberry Pi Zero 2W** (或其他树莓派型号)
- **Raspberry Pi Camera Module 3** (或兼容相机)
- **热敏打印机** (TTL串口，如 Adafruit Mini Thermal Printer)
- **按钮模块** (3引脚：VCC、OUT、GND)
- **连接线** 若干
- **电源** (5V 2A，推荐使用移动电源)

### 硬件连接

```
按钮模块:
  VCC → 树莓派 3.3V (引脚1)
  OUT → 树莓派 GPIO 17 (引脚11)
  GND → 树莓派 GND (引脚14)

热敏打印机:
  TX → 树莓派 RX (GPIO 15, 引脚10)
  RX → 树莓派 TX (GPIO 14, 引脚8)
  GND → 树莓派 GND
  VCC → 外部5V电源 (2A+)
```

## 📦 安装步骤

### 1. 系统准备

```bash
# 更新系统
sudo apt-get update
sudo apt-get upgrade -y

# 安装系统依赖
sudo apt-get install -y python3-pip python3-venv python3-picamera2 git

# 启用相机和串口
sudo raspi-config
# Interface Options -> Camera -> Enable
# Interface Options -> Serial Port -> Login shell: No, Serial hardware: Yes
```

### 2. 克隆项目

```bash
cd ~
git clone https://github.com/yourusername/poetry-camera.git
cd poetry-camera
```

### 3. 安装依赖

```bash
# 创建虚拟环境（使用系统的 picamera2）
python3 -m venv --system-site-packages venv

# 激活虚拟环境
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

填入你的API密钥：
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
REPLICATE_API_TOKEN=your_replicate_api_token_here
```

**获取API密钥：**
- DeepSeek: https://platform.deepseek.com/
- Replicate: https://replicate.com/

### 5. 测试各个模块

```bash
# 激活虚拟环境
source venv/bin/activate

# 测试相机
python tests/test_camera.py

# 测试打印机
python tests/test_printer.py

# 测试按钮
python tests/test_button_simple.py

# 测试完整流程
python tests/test_complete_flow.py
```

## 🚀 运行

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行主程序
python main.py
```

### 操作说明

- **短按按钮**：拍照并打印诗歌
- **长按按钮(2秒)**：安全退出程序
- **Ctrl+C**：强制退出

## 📁 项目结构

```
poetry-camera/
├── src/
│   ├── config.py          # 配置管理
│   ├── camera.py          # 相机控制 (Picamera2)
│   ├── printer.py         # 打印机控制 (ESC/POS)
│   ├── ai_service.py      # AI服务 (BLIP-2 + DeepSeek)
│   ├── gpio_controller.py # GPIO控制 (按钮)
│   └── utils.py           # 工具函数 (文本格式化)
├── tests/
│   ├── test_camera.py         # 相机测试
│   ├── test_printer.py        # 打印机测试
│   ├── test_button_simple.py  # 按钮测试
│   └── test_complete_flow.py  # 完整流程测试
├── scripts/
│   └── shutdown_printer.py    # 打印机关闭脚本
├── main.py                # 主程序
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量模板
└── README.md
```

## ⚙️ 配置说明

所有配置在 `.env` 文件中：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 必填 |
| `REPLICATE_API_TOKEN` | Replicate API令牌 | 必填 |
| `SERIAL_PORT` | 打印机串口 | `/dev/serial0` |
| `PRINTER_BAUD` | 打印机波特率 | `9600` |
| `BUTTON_PIN` | 按钮GPIO引脚(BCM编号) | `17` |
| `CAMERA_WIDTH` | 相机分辨率宽度 | `1920` |
| `CAMERA_HEIGHT` | 相机分辨率高度 | `1080` |

## 🐛 故障排除

<details>
<summary><b>相机无法工作</b></summary>

```bash
# 检查相机是否被识别
libcamera-hello --list-cameras

# 测试相机拍照
libcamera-jpeg -o test.jpg

# 确保相机已启用
sudo raspi-config
# Interface Options -> Camera -> Enable
```
</details>

<details>
<summary><b>打印机无法工作</b></summary>

```bash
# 检查串口
ls -l /dev/serial*

# 检查串口权限
sudo usermod -a -G dialout $USER
# 需要重启生效

# 手动测试打印机
python tests/test_printer.py
```
</details>

<details>
<summary><b>按钮无法检测</b></summary>

```bash
# 测试按钮硬件
python tests/test_button_simple.py

# 检查GPIO配置
# 确保 .env 中的 BUTTON_PIN 与实际连接一致
```
</details>

<details>
<summary><b>权限问题</b></summary>

```bash
# 添加用户到必要的组
sudo usermod -a -G dialout $USER  # 串口访问
sudo usermod -a -G video $USER    # 相机访问
sudo usermod -a -G gpio $USER     # GPIO访问

# 重启后生效
sudo reboot
```
</details>

## � 自动启动

如果希望开机自动运行：

```bash
# 编辑 crontab
crontab -e

# 添加以下行
@reboot sleep 30 && cd /home/pi/poetry-camera && /home/pi/poetry-camera/venv/bin/python /home/pi/poetry-camera/main.py >> /home/pi/poetry-camera/poetry-camera.log 2>&1
```

## 🎨 打印样例

```
2025年10月25日
14:30
`'. .'`'. .'`'. .'`'. .'`
   `     `     `     `     `

灰白的月光洒在按键上，
指尖轻触，诗意流淌。
科技与人文交织，
在这方寸之间绽放。

   .     .     .     .     .   
_.` `._.` `._.` `._.` `._.` `._
这首诗由AI创作。
在以下网址探索档案
roefruit.com
```

## �📝 许可证

MIT License

## 🙏 致谢

- [Adafruit Thermal Printer Library](https://github.com/adafruit/Python-Thermal-Printer)
- [Picamera2 Documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Replicate BLIP-2](https://replicate.com/salesforce/blip-2)
- [DeepSeek AI](https://www.deepseek.com/)

## 💡 灵感来源

本项目受 [Poetry Camera](https://poetry.camera/) 启发
