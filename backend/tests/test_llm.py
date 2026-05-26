import pytest

from app.config import get_settings
from app.core.llm import DEEPSEEK_V4_PRO, get_llm


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    get_llm.cache_clear()
    yield
    get_settings.cache_clear()
    get_llm.cache_clear()


def test_deepseek_v4_pro_responds() -> None:
    settings = get_settings()
    if not settings.deepseek_api_key:
        pytest.skip("DEEPSEEK_API_KEY 未配置")

    assert settings.deepseek_model == DEEPSEEK_V4_PRO

    llm = get_llm(streaming=False)
    response = llm.invoke("用一句话介绍你自己，并说明当前模型名称。")
    content = response.content if hasattr(response, "content") else str(response)

    assert content
    assert len(content.strip()) > 0
    print(f"\n[DeepSeek {settings.deepseek_model}] 回复: {content[:200]}")
