"""
配置管理模块

负责从环境变量和配置文件中加载和验证配置
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """配置类 - 单例模式"""
    
    _instance: Optional['Config'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 加载.env文件
        project_root = Path(__file__).parent.parent
        env_path = project_root / '.env'
        load_dotenv(dotenv_path=env_path)
        
        # 项目路径
        self.project_root = project_root
        
        # API配置
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.replicate_api_token = os.getenv('REPLICATE_API_TOKEN', '')
        
        # 串口配置
        self.serial_port = os.getenv('SERIAL_PORT', '/dev/serial0')
        self.printer_baud = int(os.getenv('PRINTER_BAUD', '9600'))
        self.printer_encoding = os.getenv('PRINTER_ENCODING', 'gbk')
        
        # GPIO配置（避免与串口冲突）
        self.button_pin = int(os.getenv('BUTTON_PIN', '17'))  # GPIO 17 (引脚11)
        self.led_pin = int(os.getenv('LED_PIN', '27'))  # GPIO 27 (引脚13)
        
        # HTTP配置
        self.http_timeout = float(os.getenv('HTTP_TIMEOUT', '30'))
        
        # 日志和数据目录
        self.log_file = os.getenv('LOG_FILE', 'poetry-camera.log')
        self.data_dir = os.getenv('DATA_DIR', 'data')
        
        # 相机配置
        self.camera_width = int(os.getenv('CAMERA_WIDTH', '1920'))
        self.camera_height = int(os.getenv('CAMERA_HEIGHT', '1080'))
        
        # 创建必要的目录
        self._setup_directories()
        
        self._initialized = True
    
    def _setup_directories(self):
        """创建必要的目录"""
        data_path = self.project_root / self.data_dir
        data_path.mkdir(exist_ok=True)
        
        # 创建子目录
        (data_path / 'images').mkdir(exist_ok=True)
        (data_path / 'uploads').mkdir(exist_ok=True)
        (data_path / 'processed').mkdir(exist_ok=True)
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        验证配置
        
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        if not self.deepseek_api_key:
            errors.append("未设置 DEEPSEEK_API_KEY")
        
        if not self.replicate_api_token:
            errors.append("未设置 REPLICATE_API_TOKEN")
        
        return len(errors) == 0, errors
    
    @property
    def images_dir(self) -> Path:
        """图像保存目录"""
        return self.project_root / self.data_dir / 'images'
    
    @property
    def uploads_dir(self) -> Path:
        """上传目录"""
        return self.project_root / self.data_dir / 'uploads'
    
    @property
    def processed_dir(self) -> Path:
        """已处理目录"""
        return self.project_root / self.data_dir / 'uploads' / 'processed'
    
    @property
    def log_path(self) -> Path:
        """日志文件路径"""
        return self.project_root / self.log_file
    
    def __repr__(self):
        return f"<Config project_root={self.project_root}>"


# 全局配置实例
config = Config()
