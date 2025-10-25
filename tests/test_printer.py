#!/usr/bin/env python3
"""
测试打印机功能
"""
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.printer import ThermalPrinter


def main():
    print("=" * 50)
    print("打印机测试")
    print("=" * 50)
    
    printer = ThermalPrinter()
    
    # 初始化
    print("\n1. 初始化打印机...")
    if not printer.initialize():
        print("❌ 初始化失败")
        print("\n提示:")
        print("  - 检查串口连接")
        print("  - 确认波特率设置")
        print("  - 运行 'ls -l /dev/serial*' 查看可用串口")
        return
    print("✅ 初始化成功")
    
    # 等待一下
    time.sleep(1)
    
    # 使用 test_print 方法
    print("\n2. 打印测试页...")
    printer.test_print()
    
    # 等待打印完成
    print("\n等待打印完成...")
    time.sleep(3)
    
    # 关闭
    print("\n3. 关闭打印机...")
    printer.close()
    print("✅ 打印机已关闭")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
    print("\n如果打印机仍然没有反应，请检查:")
    print("  1. 打印机电源是否充足（需要 5V 2A）")
    print("  2. 接线是否正确（TX-RX 交叉连接）")
    print("  3. 打印纸是否装好")
    print("  4. 尝试不同的波特率（修改 .env 文件）:")
    print("     PRINTER_BAUD=9600   # 或 19200, 115200")


if __name__ == "__main__":
    main()
