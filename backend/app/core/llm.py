from functools import lru_cache
from typing import Any

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import AIMessage
from langchain_deepseek import ChatDeepSeek

from app.config import get_settings

DEEPSEEK_V4_PRO = "deepseek-v4-pro"


class DeepSeekThinkingChat(ChatDeepSeek):
    """DeepSeek thinking 模型在 Agent 多轮 tool calling 时需回传 reasoning_content。"""

    def _get_request_payload(
        self,
        input_: LanguageModelInput,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> dict:
        source_messages = self._convert_input(input_).to_messages()
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        for src_msg, msg_dict in zip(source_messages, payload.get("messages", [])):
            if isinstance(src_msg, AIMessage) and msg_dict.get("role") == "assistant":
                reasoning = src_msg.additional_kwargs.get("reasoning_content")
                if reasoning is not None:
                    msg_dict["reasoning_content"] = reasoning
        return payload


@lru_cache
def get_llm(*, streaming: bool = False) -> DeepSeekThinkingChat:
    settings = get_settings()
    if not settings.deepseek_api_key:
        raise ValueError("DEEPSEEK_API_KEY 未配置，请在 backend/.env 中设置")

    return DeepSeekThinkingChat(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        streaming=streaming,
        temperature=0,
        max_retries=2,
    )
