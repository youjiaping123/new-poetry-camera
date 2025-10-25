#!/usr/bin/env python3
"""
优雅关闭打印机 - 在树莓派关机前运行
"""
import serial
import time
import os

PORT = '/dev/serial0'
BAUD = 9600

try:
    print("连接打印机...")
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(0.3)
    
    print("取消待打印内容...")
    ser.write(b'\x18')  # CAN
    time.sleep(0.1)
    
    print("重置打印机...")
    ser.write(b'\x1b@')  # ESC @
    time.sleep(0.2)
    
    print("发送休眠命令...")
    ser.write(b'\x1b\x38')  # ESC 8 - 进入休眠模式（部分打印机支持）
    time.sleep(0.1)
    
    print("清空缓冲区...")
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.flush()
    time.sleep(0.3)
    
    print("关闭串口...")
    ser.close()
    time.sleep(0.2)
    
    # 尝试禁用串口硬件（需要root权限）
    print("尝试禁用串口硬件...")
    os.system("sudo stty -F /dev/serial0 0 2>/dev/null")
    
    print("✓ 打印机已安全关闭")
    
except Exception as e:
    print(f"错误: {e}")
    # 即使出错也尝试禁用串口
    try:
        os.system("sudo stty -F /dev/serial0 0 2>/dev/null")
    except:
        pass
