"""
热敏打印机控制模块
支持通用热敏打印机（ESC/POS 协议）
"""
import logging
import serial
import time
from typing import Optional
from .config import config
from .utils import wrap_text, format_header, format_footer


class ThermalPrinter:
    """热敏打印机控制类"""
    
    # ESC/POS 命令
    ESC = b'\x1b'
    GS = b'\x1d'
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.serial: Optional[serial.Serial] = None
        self.initialized = False
    
    def initialize(self) -> bool:
        """初始化打印机"""
        try:
            self.logger.info("尝试连接串口: %s", config.serial_port)
            self.logger.info("波特率: %s", config.printer_baud)
            
            self.serial = serial.Serial(
                port=config.serial_port,
                baudrate=config.printer_baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=3,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            time.sleep(0.5)  # 等待串口稳定
            
            self.logger.debug("发送初始化命令")
            
            # 清空缓冲区
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            
            # ESC @ - 初始化打印机
            self._write(self.ESC + b'@')
            time.sleep(0.1)
            
            # 设置打印密度和加热时间（可选，根据打印机调整）
            # ESC 7 n1 n2 n3
            self._write(self.ESC + b'\x37')
            self._write(bytes([11, 200, 50]))  # 加热时间、加热间隔、加热密度
            time.sleep(0.1)
            
            # 设置字符间距
            self._write(self.ESC + b'\x20' + bytes([0]))
            
            # 设置行间距
            self._write(self.ESC + b'\x33' + bytes([50]))

            self.initialized = True

            # 确保清除任何待打印的数据
            self.cancel_print()
            
            self.logger.info("打印机初始化完成")
            return True
            
        except Exception as e:
            self.logger.exception("打印机初始化失败: %s", e)
            return False
    
    def _write(self, data: bytes):
        """写入数据到串口"""
        if self.serial and self.serial.is_open:
            self.serial.write(data)
            self.serial.flush()
            # 添加小延迟确保数据发送完成
            time.sleep(0.01)
    
    def print_text(self, text: str, font_size: int = 1, align: str = 'left'):
        """
        打印文本
        
        Args:
            text: 要打印的文本
            font_size: 字体大小 (1-3)
            align: 对齐方式 ('left', 'center', 'right')
        """
        if not self.initialized or not self.serial:
            self.logger.error("打印机未初始化")
            return
        
        try:
            self.logger.debug("准备打印文本，长度 %s", len(text))
            
            # 设置对齐方式
            align_commands = {
                'left': b'\x00',
                'center': b'\x01',
                'right': b'\x02'
            }
            self._write(self.ESC + b'a' + align_commands.get(align, b'\x00'))
            
            # 设置字体大小
            if font_size > 1:
                # GS ! n - 设置字符大小
                size = min(font_size - 1, 7)  # 0-7
                width = size & 0x0F
                height = (size & 0x0F) << 4
                self._write(self.GS + b'!' + bytes([width | height]))
            else:
                self._write(self.GS + b'!' + bytes([0]))
            
            # 打印文本（按行发送）
            if not text:
                return

            lines = text.split('\n')
            for i, line in enumerate(lines):
                self.logger.debug("发送第 %s/%s 行", i + 1, len(lines))
                # 编码为 GB18030（支持中文）或 UTF-8
                try:
                    encoded = line.encode('gb18030')
                except:
                    encoded = line.encode('utf-8', errors='replace')
                
                self._write(encoded)
                self._write(b'\n')  # 换行
                time.sleep(0.05)  # 给打印机处理时间
            
            # 走纸1行留空隙
            self.logger.debug("发送走纸命令")
            self.feed(1)
            
            self.logger.debug("文本发送完成")
            
        except Exception as e:
            self.logger.exception("打印失败: %s", e)
    
    def feed(self, lines: int = 1):
        """走纸"""
        if not self.initialized or not self.serial:
            return
        
        # ESC d n - 走纸 n 行
        self._write(self.ESC + b'd' + bytes([lines]))
        time.sleep(0.1 * lines)  # 等待走纸完成
    
    def cut_paper(self):
        """切纸（如果打印机支持）"""
        if not self.initialized or not self.serial:
            return
        
        try:
            # 走一些纸再切
            self.feed(5)
            # GS V m - 切纸命令
            self._write(self.GS + b'V' + bytes([66, 0]))  # 全切
            time.sleep(0.5)
        except Exception:
            self.logger.exception("切纸失败（打印机可能不支持）")

    def cancel_print(self):
        """发送取消打印命令并清空缓冲"""
        if not self.serial:
            return

        try:
            # CAN - 取消打印
            self._write(b'\x18')
            time.sleep(0.1)
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            self.logger.debug("打印缓冲区已清空")
        except Exception:
            self.logger.exception("清空打印缓冲失败")

    def enter_sleep_mode(self):
        """让打印机进入休眠，防止关机时串口噪声触发"""
        if not self.serial:
            return

        try:
            # ESC 8 - 进入休眠（大部分ESC/POS兼容）
            self._write(self.ESC + b'8')
            time.sleep(0.1)
            self.logger.debug("打印机进入休眠模式")
        except Exception:
            self.logger.exception("打印机休眠命令发送失败")
    
    def set_chinese_mode(self):
        """设置中文模式"""
        if not self.initialized or not self.serial:
            return
        
        # FS & - 选择中文模式
        self._write(b'\x1c\x26')
    
    def test_print(self):
        """打印测试页"""
        if not self.initialized:
            self.logger.error("打印机未初始化")
            return
        
        self.logger.info("开始打印测试页")
        
        # 打印标题
        self.print_text("=== 打印机测试 ===", font_size=2, align='center')
        self.feed(1)
        
        # 打印信息
        self.print_text("诗歌相机 Poetry Camera", align='center')
        self.feed(1)
        
        self.print_text("如果你能看到这些文字，")
        self.print_text("说明打印机工作正常。")
        self.feed(1)
        
        self.print_text("ASCII Test: !@#$%^&*()")
        self.print_text("Numbers: 0123456789")
        self.feed(2)
        
        # 走纸
        self.feed(5)
        
        self.logger.info("测试页打印完成")
    
    def print_poem(self, poem: str):
        """打印诗歌（带头部和脚注）"""
        if not self.initialized:
            self.logger.error("打印机未初始化")
            return

        try:
            self.logger.info("开始打印诗歌")
            header = format_header()
            self.print_text(header, align='left')

            wrapped_poem = wrap_text(poem)
            self.print_text(wrapped_poem, align='left')

            footer = format_footer()
            self.print_text(footer, align='left')

            self.feed(2)
            self.logger.info("诗歌打印完成")
        except Exception as exc:
            self.logger.exception("打印诗歌失败: %s", exc)

    def close(self):
        """关闭打印机连接"""
        if self.serial and self.serial.is_open:
            try:
                # 进入休眠，避免关机/开机串口噪声导致乱码
                self.enter_sleep_mode()
                # 确保无待处理数据
                self.cancel_print()
                time.sleep(0.3)
                self.serial.close()
                self.logger.info("串口已关闭")
            except Exception:
                self.logger.exception("关闭串口时出错")

        self.initialized = False
