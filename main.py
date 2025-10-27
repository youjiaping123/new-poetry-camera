#!/usr/bin/env python3
"""
诗歌相机 - 主程序

将所见之物转化为诗歌
"""
import sys
import logging
from logging.handlers import RotatingFileHandler
import signal
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.camera import Camera
from src.printer import ThermalPrinter
from src.ai_service import AIService
from src.gpio_controller import GPIOController
from src.archive import PoemArchive


class PoetryCamera:
    """诗歌相机主类"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 组件
        self.camera = Camera()
        self.printer = ThermalPrinter()
        self.ai_service = AIService()
        self.gpio = GPIOController(enable_led=False)  # 禁用LED
        self.archive = PoemArchive()
        
        # 运行标志
        self.running = True
        
        # 注册信号处理
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def setup_logging(self):
        """配置日志"""
        log_level = getattr(logging, config.log_level, logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        config.log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            config.log_path,
            maxBytes=1_048_576,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)

        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(log_level)
        root.addHandler(file_handler)
        root.addHandler(stream_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"收到信号 {signum}，准备退出...")
        self.running = False
    
    def initialize(self) -> bool:
        """
        初始化所有组件
        
        Returns:
            是否全部初始化成功
        """
        self.logger.info("=" * 50)
        self.logger.info("诗歌相机启动中...")
        self.logger.info("=" * 50)
        
        # 验证配置
        is_valid, errors = config.validate()
        if not is_valid:
            self.logger.error("配置验证失败:")
            for error in errors:
                self.logger.error(f"  - {error}")
            return False
        
        # 初始化GPIO
        if not self.gpio.initialize():
            self.logger.error("GPIO初始化失败")
            return False
        
        # 初始化打印机
        if not self.printer.initialize():
            self.logger.error("打印机初始化失败")
            return False
        
        # 初始化相机
        if not self.camera.initialize():
            self.logger.error("相机初始化失败")
            return False
        
        self.logger.info("所有组件初始化成功")
        self.logger.info("日志输出到: %s", config.log_path)
        self.logger.info("诗歌归档目录: %s", config.poems_dir)
        
        return True
    
    def capture_and_print(self):
        """执行拍照和打印流程"""
        try:
            self.logger.info("=" * 50)
            self.logger.info("开始拍照...")
            
            # 拍照
            image_path = self.camera.capture()
            if not image_path:
                self.logger.error("❌ 拍照失败")
                return
            
            self.logger.info("✓ 拍照成功")
            self.logger.info("正在处理图像...")
            
            # 生成诗歌
            result = self.ai_service.process_image_to_poem(image_path)
            if not result:
                self.logger.error("❌ 诗歌生成失败")
                return
            
            self.logger.info("✓ 诗歌生成成功")
            self.logger.info("图像描述: %s", result.caption)
            self.logger.info("生成的诗歌:\n%s", result.poem)
            
            # 打印诗歌
            self.logger.info("开始打印...")
            self.printer.print_poem(result.poem)

            archived = self.archive.save(
                poem=result.poem,
                caption=result.caption,
                image_path=image_path
            )
            if archived:
                self.logger.info(
                    "记录已归档 -> poem: %s, image: %s",
                    archived.poem_path.name,
                    archived.image_path.name
                )
            
            self.logger.info("✓ 流程完成")
            self.logger.info("=" * 50)
            
        except Exception as e:
            self.logger.error(f"❌ 执行流程时出错: {e}", exc_info=True)
    
    def run(self):
        """主运行循环"""
        if not self.initialize():
            self.logger.error("初始化失败，退出")
            return
        
        try:
            self.logger.info("=" * 50)
            self.logger.info("诗歌相机就绪!")
            self.logger.info("=" * 50)
            self.logger.info("操作说明:")
            self.logger.info("  - 短按按钮: 拍照并打印诗歌")
            self.logger.info("  - 长按按钮(2秒): 退出程序")
            self.logger.info("  - Ctrl+C: 强制退出")
            self.logger.info("=" * 50)
            
            wait_count = 0
            
            while self.running:
                # 等待按钮按下（带超时，以便可以响应 Ctrl+C）
                press_type = self.gpio.wait_for_button_press(
                    long_press_duration=2.0,
                    timeout=2.0  # 2秒超时
                )
                
                if press_type == "TIMEOUT":
                    # 超时，继续循环
                    wait_count += 1
                    if wait_count % 5 == 0:  # 每10秒提示一次
                        self.logger.info(f"等待按钮... ({wait_count * 2}秒)")
                    continue
                
                elif press_type == "LONG":
                    # 长按 - 退出程序
                    self.logger.info("检测到长按，准备退出...")
                    break
                
                elif press_type == "SHORT":
                    # 短按 - 拍照并打印
                    wait_count = 0  # 重置计数
                    self.logger.info("检测到短按，开始拍照...")
                    self.capture_and_print()
                
                # 短暂延迟，防止重复触发
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            self.logger.info("\n收到键盘中断")
        
        except Exception as e:
            self.logger.error(f"运行时错误: {e}", exc_info=True)
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """清理资源"""
        self.logger.info("正在关闭诗歌相机...")
        
        try:
            # 关闭各组件
            self.camera.close()
            self.printer.close()
            self.gpio.cleanup()
            
            self.logger.info("诗歌相机已关闭")
            
        except Exception as e:
            self.logger.error(f"关闭时出错: {e}", exc_info=True)


def main():
    """主函数"""
    camera = PoetryCamera()
    camera.run()


if __name__ == "__main__":
    main()
