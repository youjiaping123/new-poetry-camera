"""
GPIO控制模块

封装按钮和LED控制
"""
import logging
import time
from typing import Callable, Optional

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO 未安装，GPIO功能将不可用")

from .config import config


class GPIOController:
    """GPIO控制类"""
    
    def __init__(self, enable_led: bool = True):
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self.button_pressed = False
        self.button_press_time: Optional[float] = None
        self.enable_led = enable_led  # 是否启用LED
    
    def initialize(self) -> bool:
        """
        初始化GPIO
        
        Returns:
            是否成功初始化
        """
        if not GPIO_AVAILABLE:
            self.logger.error("RPi.GPIO 未安装")
            return False
        
        try:
            self.logger.info("正在初始化GPIO...")
            
            # 设置GPIO模式
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # 设置按钮引脚（使用下拉电阻）
            # 按钮模块：未按下=LOW，按下=HIGH（需要下拉电阻）
            GPIO.setup(config.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            
            # 设置LED引脚（可选）
            if self.enable_led:
                GPIO.setup(config.led_pin, GPIO.OUT)
                GPIO.output(config.led_pin, GPIO.LOW)
                self.logger.info("LED已启用")
            else:
                self.logger.info("LED已禁用")
            
            self._initialized = True
            self.logger.info("GPIO初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"GPIO初始化失败: {e}", exc_info=True)
            return False
    
    def is_button_pressed(self) -> bool:
        """
        检查按钮是否被按下
        
        Returns:
            按钮是否被按下
        """
        if not self._initialized:
            print("[错误] is_button_pressed: GPIO未初始化")
            return False
        
        try:
            # 按钮按下时为HIGH（使用下拉电阻，按下时输出3.3V）
            return GPIO.input(config.button_pin) == GPIO.HIGH
        except Exception as e:
            self.logger.error(f"读取按钮状态失败: {e}", exc_info=True)
            return False
    
    def wait_for_button_press(self, long_press_duration: float = 2.0, timeout: float = None) -> str:
        """
        等待按钮按下
        
        Args:
            long_press_duration: 长按时间阈值（秒）
            timeout: 超时时间（秒），None表示无限等待
            
        Returns:
            "SHORT" 表示短按, "LONG" 表示长按, "TIMEOUT" 表示超时
        """
        if not self._initialized:
            return "TIMEOUT"
        
        button_press_time = None
        start_time = time.time()
        
        while True:
            # 检查超时
            if timeout and (time.time() - start_time) >= timeout:
                return "TIMEOUT"
            
            is_pressed = self.is_button_pressed()
            
            if is_pressed:
                # 按钮被按下
                if button_press_time is None:
                    button_press_time = time.time()
                    
                # 检查是否长按
                press_duration = time.time() - button_press_time
                if press_duration >= long_press_duration:
                    # 长按
                    self.logger.info("检测到长按")
                    # 等待按钮释放
                    while self.is_button_pressed():
                        time.sleep(0.05)
                    return "LONG"
            else:
                # 按钮释放
                if button_press_time is not None:
                    press_duration = time.time() - button_press_time
                    
                    if press_duration >= 0.05:  # 至少按下50ms才算有效
                        if press_duration < long_press_duration:
                            # 短按
                            self.logger.info("检测到短按")
                            return "SHORT"
                        else:
                            self.logger.info("检测到长按")
                            return "LONG"
                    
                    button_press_time = None
            
            time.sleep(0.02)  # 20ms 轮询间隔
    
    def led_on(self):
        """打开LED"""
        if self._initialized and self.enable_led:
            GPIO.output(config.led_pin, GPIO.HIGH)
    
    def led_off(self):
        """关闭LED"""
        if self._initialized and self.enable_led:
            GPIO.output(config.led_pin, GPIO.LOW)
    
    def led_blink(self, times: int = 1, interval: float = 0.5):
        """
        LED闪烁
        
        Args:
            times: 闪烁次数
            interval: 闪烁间隔（秒）
        """
        if not self.enable_led:
            return
        for _ in range(times):
            self.led_on()
            time.sleep(interval)
            self.led_off()
            time.sleep(interval)
    
    def led_pulse(self, duration: float = 1.0):
        """
        LED呼吸灯效果（模拟）
        
        Args:
            duration: 持续时间（秒）
        """
        if not self.enable_led:
            return
        steps = 20
        step_time = duration / (steps * 2)
        
        # 淡入
        for _ in range(steps):
            self.led_on()
            time.sleep(step_time * 0.9)
            self.led_off()
            time.sleep(step_time * 0.1)
        
        # 淡出
        for _ in range(steps):
            self.led_on()
            time.sleep(step_time * 0.1)
            self.led_off()
            time.sleep(step_time * 0.9)
    
    def cleanup(self):
        """清理GPIO"""
        if GPIO_AVAILABLE:
            try:
                self.logger.info("正在清理GPIO...")
                GPIO.cleanup()
                self.logger.info("GPIO已清理")
            except Exception as e:
                self.logger.error(f"清理GPIO时出错: {e}", exc_info=True)
            finally:
                self._initialized = False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()
