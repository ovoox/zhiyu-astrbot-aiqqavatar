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
        
    def _get_api_key(self):
        encrypted_key = "YzYwYjVmZmEzZDZiNjMwNTZjNzcyNTg0Y2ExYzhhY2I1MzY5ZDc1YTk2N2YxNGI5ZjcyZTAzZmFiYzk3Y2I3Mg=="
        return base64.b64decode(encrypted_key).decode('utf-8')
    
    def _get_avatar_url(self, sender_id):
        encrypted_base = "aHR0cDovL2FwaS5vY29hLmNuL2FwaS9xcXR4LnBocA=="
        base_url = base64.b64decode(encrypted_base).decode('utf-8')
        return f"{base_url}?qq={sender_id}"
    
    def _get_api_base_url(self):
        encrypted_base = "aHR0cHM6Ly9taXNzcWl1LmljdS9BUEkvYWl0bC5waHA="
        return base64.b64decode(encrypted_base).decode('utf-8')

    @filter.regex(r"^(?:/)?解读头像$")
    async def interpret_avatar(self, event: AstrMessageEvent):
        sender_id = event.get_sender_id()
        if not sender_id:
            yield event.plain_result("无法获取您的QQ号")
            return

        yield event.plain_result("头像解读中...\n请耐心等待几秒")

        avatar_url = self._get_avatar_url(sender_id)
        api_base_url = self._get_api_base_url()
        api_key = self._get_api_key()

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
                        yield event.plain_result("解读头像失败 请重试")
                        return

                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    if content.strip():
                        yield event.plain_result(content.strip())
                    else:
                        yield event.plain_result("解读头像失败 请重试")

        except (aiohttp.ClientError, ValueError, KeyError, IndexError) as e:
            logger.error(f"处理AI响应时出错: {str(e)}")
            yield event.plain_result("解读头像失败 请重试")