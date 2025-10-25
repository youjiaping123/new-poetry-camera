"""
AI服务模块

封装图像识别和诗歌生成API调用
"""
import logging
from pathlib import Path
from typing import Optional
import httpx
import replicate
from tenacity import retry, stop_after_attempt, wait_fixed

from .config import config


class AIService:
    """AI服务类"""
    
    # 诗歌生成提示词
    SYSTEM_PROMPT = """你是一位诗人。你擅长优雅且情感丰富的诗歌。
你善于使用微妙的表达,并以现代口语风格写作。
使用高中水平的中文,但研究生水平的技巧。
你的诗更具文学性,但易于理解和产生共鸣。
你专注于亲密和个人的真实,不能使用诸如真理、时间、沉默、生命、爱、和平、战争、仇恨、幸福等宏大词语,
而必须使用具体和具象的语言来展示,而非直接告诉这些想法。
仔细思考如何创作一首能满足这些要求的诗。
这非常重要,过于生硬或俗气的诗会造成巨大伤害。"""
    
    PROMPT_TEMPLATE = """根据我下面描述的细节写一首诗。
使用指定的诗歌格式。对源材料的引用必须微妙但清晰。
专注于独特和优雅的诗,使用具体的想法和细节。
你必须保持词汇简单,并使用低调的视角。这一点非常重要。

诗歌格式: {format}

场景描述: {description}
"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 设置Replicate API Token
        if config.replicate_api_token:
            import os
            os.environ['REPLICATE_API_TOKEN'] = config.replicate_api_token
    
    def generate_image_caption(self, image_path: Path) -> Optional[str]:
        """
        使用BLIP-2生成图像描述
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            图像描述文本，失败返回None
        """
        try:
            self.logger.info(f"正在分析图像: {image_path}")
            
            with open(image_path, "rb") as f:
                output = replicate.run(
                    "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608",
                    input={
                        "image": f,
                        "caption": True,
                    }
                )
            
            caption = str(output).strip()
            self.logger.info(f"图像描述: {caption}")
            return caption
            
        except Exception as e:
            self.logger.error(f"图像识别失败: {e}", exc_info=True)
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _call_deepseek_api(self, messages: list) -> dict:
        """
        调用DeepSeek API（带重试机制）
        
        Args:
            messages: 消息列表
            
        Returns:
            API响应
        """
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": False
        }
        
        with httpx.Client(timeout=config.http_timeout) as client:
            response = client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
    
    def generate_poem(self, image_description: str, poem_format: str = "8行自由诗") -> Optional[str]:
        """
        根据图像描述生成诗歌
        
        Args:
            image_description: 图像描述
            poem_format: 诗歌格式
            
        Returns:
            生成的诗歌，失败返回None
        """
        try:
            self.logger.info("正在生成诗歌...")
            
            # 构建提示词
            user_prompt = self.PROMPT_TEMPLATE.format(
                format=poem_format,
                description=image_description
            )
            
            # 清理特殊字符
            user_prompt = user_prompt.replace("[", "").replace("]", "")
            user_prompt = user_prompt.replace("{", "").replace("}", "")
            
            # 调用API
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
            
            result = self._call_deepseek_api(messages)
            poem = result['choices'][0]['message']['content'].strip()
            
            self.logger.info("诗歌生成成功")
            self.logger.info(f"生成的诗歌:\n{poem}")
            
            return poem
            
        except Exception as e:
            self.logger.error(f"诗歌生成失败: {e}", exc_info=True)
            return None
    
    def process_image_to_poem(self, image_path: Path) -> Optional[str]:
        """
        完整流程：图像 -> 描述 -> 诗歌
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            生成的诗歌，失败返回None
        """
        # 生成图像描述
        caption = self.generate_image_caption(image_path)
        if not caption:
            self.logger.error("无法生成图像描述")
            return None
        
        # 生成诗歌
        poem = self.generate_poem(caption)
        if not poem:
            self.logger.error("无法生成诗歌")
            return None
        
        return poem
