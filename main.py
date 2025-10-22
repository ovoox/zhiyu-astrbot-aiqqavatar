from astrbot.api.all import *
from astrbot.api.event import filter, AstrMessageEvent
import aiohttp
import re
import base64
from typing import Optional


@register("avatar_interpreter", "解读头像", "AI解读用户头像", "1.0")
class AvatarInterpreterPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        
    def _decrypt_api_key(self) -> str:
        """解密API密钥"""
        # Base64编码的API密钥
        encrypted_key = "YzYwYjVmZmEzZDZiNjMwNTZjNzcyNTg0Y2ExYzhhY2I1MzY5ZDc1YTk2N2YxNGI5ZjcyZTAzZmFiYzk3Y2I3Mg=="
        return base64.b64decode(encrypted_key).decode('utf-8')
    
    def _decrypt_avatar_url(self, sender_id: str) -> str:
        """解密头像URL"""
        # 加密的头像URL基础部分
        encrypted_base = "aHR0cDovL2FwaS5vY29hLmNuL2FwaS9xcXR4LnBocA=="
        base_url = base64.b64decode(encrypted_base).decode('utf-8')
        return f"{base_url}?qq={sender_id}"
    
    def _decrypt_api_url(self) -> str:
        """解密API URL基础部分"""
        # 加密的API URL基础部分
        encrypted_base = "aHR0cHM6Ly9taXNzcWl1LmljdS9BUEkvYWl0bC5waHA="
        return base64.b64decode(encrypted_base).decode('utf-8')

    @filter.regex(r"^(?:/)?解读头像$")
    async def interpret_avatar(self, event: AstrMessageEvent):
        sender_id = event.get_sender_id()
        if not sender_id:
            yield event.plain_result("无法获取您的QQ号")
            return

        yield event.plain_result("头像解读中...\n请耐心等待几秒")

        # 使用解密方法获取URL和密钥
        avatar_url = self._decrypt_avatar_url(sender_id)
        api_base_url = self._decrypt_api_url()
        api_key = self._decrypt_api_key()

        # 构建完整的API URL
        api_url = (
            f"{api_base_url}"
            f"?apikey={api_key}"
            "&text=解读一下这个头像，不要输出markdown格式，要纯文本返回"
            f"&url={avatar_url}"
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status != 200:
                        logger.error(f"AI接口HTTP状态码: {response.status}")
                        yield event.plain_result("头像解读失败 请稍后再试")
                        return

                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    if content.strip():
                        yield event.plain_result(content.strip())
                    else:
                        yield event.plain_result("AI返回内容为空")

        except (aiohttp.ClientError, ValueError, KeyError, IndexError) as e:
            logger.error(f"处理AI响应时出错: {str(e)}")
            yield event.plain_result("解析结果失败 请稍后再试")