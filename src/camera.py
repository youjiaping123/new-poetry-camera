"""
相机控制模块

封装 Picamera2 相关功能
"""
import logging
from pathlib import Path
from typing import Optional

try:
    from picamera2 import Picamera2
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False
    logging.warning("Picamera2 未安装，相机功能将不可用")

from .config import config


class Camera:
    """相机控制类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.camera: Optional[Picamera2] = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        初始化相机
        
        Returns:
            是否成功初始化
        """
        if not CAMERA_AVAILABLE:
            self.logger.error("Picamera2 未安装")
            return False
        
        try:
            self.logger.info("正在初始化相机...")
            self.camera = Picamera2()
            
            # 配置相机
            camera_config = self.camera.create_still_configuration(
                main={"size": (config.camera_width, config.camera_height)}
            )
            self.camera.configure(camera_config)
            
            # 启动相机
            self.camera.start()
            
            # 等待相机稳定
            import time
            time.sleep(2)
            
            self._initialized = True
            self.logger.info("相机初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"相机初始化失败: {e}", exc_info=True)
            return False
    
    def capture(self, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        拍摄照片
        
        Args:
            output_path: 输出文件路径，如果为None则使用默认路径
            
        Returns:
            保存的文件路径，失败返回None
        """
        if not self._initialized or self.camera is None:
            self.logger.error("相机未初始化")
            return None
        
        try:
            if output_path is None:
                output_path = config.images_dir / f"image_{self._get_timestamp()}.jpg"
            
            self.logger.info(f"正在拍照，保存到: {output_path}")
            self.camera.capture_file(str(output_path))
            
            self.logger.info("拍照成功")
            return output_path
            
        except Exception as e:
            self.logger.error(f"拍照失败: {e}", exc_info=True)
            return None
    
    def _get_timestamp(self) -> str:
        """获取时间戳字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def close(self):
        """关闭相机"""
        if self.camera:
            try:
                self.logger.info("正在关闭相机...")
                self.camera.stop()
                self.camera.close()
                self.logger.info("相机已关闭")
            except Exception as e:
                self.logger.error(f"关闭相机时出错: {e}", exc_info=True)
            finally:
                self.camera = None
                self._initialized = False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
