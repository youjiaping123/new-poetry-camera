"""
工具函数模块
"""
import textwrap
from datetime import datetime


def wrap_text(text: str, width: int = 32) -> str:
    """
    按指定宽度换行文本
    
    Args:
        text: 要换行的文本
        width: 每行的最大字符数
        
    Returns:
        换行后的文本
    """
    lines = text.split('\n')
    wrapped_lines = []
    
    for line in lines:
        if not line:
            wrapped_lines.append('')
            continue
        
        # 中文字符计算为2个宽度
        wrapped = []
        current_line = ""
        current_width = 0
        
        for char in line:
            char_width = 2 if ord(char) > 127 else 1
            
            if current_width + char_width > width:
                wrapped.append(current_line)
                current_line = char
                current_width = char_width
            else:
                current_line += char
                current_width += char_width
        
        if current_line:
            wrapped.append(current_line)
        
        wrapped_lines.extend(wrapped)
    
    return '\n'.join(wrapped_lines)


def format_header() -> str:
    """
    生成打印头部（日期和装饰线）
    
    Returns:
        格式化的头部文本
    """
    now = datetime.now()
    # 中文日期格式
    date_string = now.strftime('%Y年%m月%d日')
    time_string = now.strftime('%H:%M')
    
    header = f"{date_string}\n{time_string}\n"
    header += "`'. .'`'. .'`'. .'`'. .'`\n"
    header += "   `     `     `     `     `"
    
    return header


def format_footer() -> str:
    """
    生成打印脚注
    
    Returns:
        格式化的脚注文本
    """
    footer = "   .     .     .     .     .   \n"
    footer += "_.` `._.` `._.` `._.` `._.` `._\n"
    footer += "这首诗由AI创作。\n"
    footer += "在以下网址探索档案\n"
    footer += "roefruit.com"
    
    return footer


def center_text(text: str, width: int = 32) -> str:
    """
    居中对齐文本
    
    Args:
        text: 要居中的文本
        width: 总宽度
        
    Returns:
        居中后的文本
    """
    lines = text.split('\n')
    centered_lines = []
    
    for line in lines:
        # 计算实际宽度（中文算2个字符）
        line_width = sum(2 if ord(c) > 127 else 1 for c in line)
        padding = (width - line_width) // 2
        centered_lines.append(' ' * padding + line)
    
    return '\n'.join(centered_lines)
