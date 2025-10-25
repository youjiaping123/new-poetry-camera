#!/usr/bin/env python3
"""
最简单的按钮测试 - 直接读取GPIO状态
"""
import time

try:
    import RPi.GPIO as GPIO
    print("✅ RPi.GPIO 已导入")
except ImportError:
    print("❌ 无法导入 RPi.GPIO")
    exit(1)

# 配置
BUTTON_PIN = 17  # GPIO 17 (物理引脚11)

print("=" * 60)
print("最简单的按钮测试")
print("=" * 60)
print(f"\n按钮连接：GPIO {BUTTON_PIN} (物理引脚11)")
print("接线: VCC → 3.3V, OUT → GPIO17, GND → GND")
print("\n按 Ctrl+C 退出\n")

try:
    # 初始化GPIO
    print("1. 初始化GPIO...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print("✅ GPIO初始化成功\n")
    
    # 读取初始状态
    initial_state = GPIO.input(BUTTON_PIN)
    print(f"2. 当前按钮初始状态: {'HIGH (按下)' if initial_state else 'LOW (未按下)'}")
    print()
    
    # 实时监控
    print("3. 开始实时监控...")
    print("   请尝试按下和释放按钮")
    print("   （等待状态变化...）\n")
    
    last_state = initial_state
    count = 0
    wait_time = 0
    
    while True:
        current_state = GPIO.input(BUTTON_PIN)
        
        # 状态改变时输出
        if current_state != last_state:
            count += 1
            wait_time = 0
            
            if current_state == 1:  # 变成 HIGH
                print(f"[{count}] 按钮状态: 未按下 → 按下 ▼▼▼")
            else:  # 变成 LOW
                print(f"[{count}] 按钮状态: 按下 → 未按下 ○○○")
            
            last_state = current_state
        else:
            wait_time += 0.1
            if wait_time >= 5.0:
                print(f"   [等待中] 当前状态: {'HIGH (按下)' if current_state else 'LOW (未按下)'}")
                wait_time = 0
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\n测试被中断")

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n4. 清理GPIO...")
    GPIO.cleanup()
    print("✅ 完成\n")
    print("=" * 60)
