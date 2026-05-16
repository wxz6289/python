"""
LLM 模型统一调用封装
支持: DeepSeek, Qwen, GPT, Claude 等模型
"""

import os
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import SecretStr
from dotenv import load_dotenv

load_dotenv()


class ModelConfig:
    """模型配置类"""
    
    # DeepSeek 配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # Qwen (通义千问) 配置 - 通过 OpenAI 兼容接口
    QWEN_API_KEY = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
    
    # GPT (OpenAI) 配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("CLOSEAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL") or os.getenv("CLOSEAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Claude (Anthropic) 配置
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    CLAUDE_BASE_URL = os.getenv("CLAUDE_BASE_URL") or os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest")


def create_deepseek_model(
    model: Optional[str] = None,
    temperature: float = 0,
    timeout: int = 30,
    **kwargs
) -> ChatOpenAI:
    """
    创建 DeepSeek 模型实例
    
    Args:
        model: 模型名称,默认使用环境变量 DEEPSEEK_MODEL
        temperature: 温度参数,控制随机性 (0-1)
        timeout: 超时时间(秒)
        **kwargs: 其他传递给 ChatOpenAI 的参数
        
    Returns:
        ChatOpenAI 实例
        
    Example:
        >>> model = create_deepseek_model()
        >>> result = model.invoke("你好")
        >>> print(result.content)
    """
    api_key = ModelConfig.DEEPSEEK_API_KEY
    if not api_key:
        raise EnvironmentError(
            "Please set DEEPSEEK_API_KEY environment variable"
        )
    
    return ChatOpenAI(
        model=model or ModelConfig.DEEPSEEK_MODEL,
        temperature=temperature,
        api_key=SecretStr(api_key),
        base_url=ModelConfig.DEEPSEEK_BASE_URL,
        timeout=timeout,
        **kwargs
    )


def create_qwen_model(
    model: Optional[str] = None,
    temperature: float = 0,
    timeout: int = 30,
    **kwargs
) -> ChatOpenAI:
    """
    创建 Qwen (通义千问) 模型实例
    
    Args:
        model: 模型名称,默认使用环境变量 QWEN_MODEL
        temperature: 温度参数,控制随机性 (0-1)
        timeout: 超时时间(秒)
        **kwargs: 其他传递给 ChatOpenAI 的参数
        
    Returns:
        ChatOpenAI 实例
        
    Example:
        >>> model = create_qwen_model()
        >>> result = model.invoke("你好")
        >>> print(result.content)
    """
    api_key = ModelConfig.QWEN_API_KEY
    if not api_key:
        raise EnvironmentError(
            "Please set QWEN_API_KEY or DASHSCOPE_API_KEY environment variable"
        )
    
    return ChatOpenAI(
        model=model or ModelConfig.QWEN_MODEL,
        temperature=temperature,
        api_key=SecretStr(api_key),
        base_url=ModelConfig.QWEN_BASE_URL,
        timeout=timeout,
        **kwargs
    )


def create_gpt_model(
    model: Optional[str] = None,
    temperature: float = 0,
    timeout: int = 30,
    **kwargs
) -> ChatOpenAI:
    """
    创建 GPT (OpenAI) 模型实例
    
    Args:
        model: 模型名称,默认使用环境变量 OPENAI_MODEL
        temperature: 温度参数,控制随机性 (0-1)
        timeout: 超时时间(秒)
        **kwargs: 其他传递给 ChatOpenAI 的参数
        
    Returns:
        ChatOpenAI 实例
        
    Example:
        >>> model = create_gpt_model()
        >>> result = model.invoke("你好")
        >>> print(result.content)
    """
    api_key = ModelConfig.OPENAI_API_KEY
    if not api_key:
        raise EnvironmentError(
            "Please set OPENAI_API_KEY or CLOSEAI_API_KEY environment variable"
        )
    
    return ChatOpenAI(
        model=model or ModelConfig.OPENAI_MODEL,
        temperature=temperature,
        api_key=SecretStr(api_key),
        base_url=ModelConfig.OPENAI_BASE_URL,
        timeout=timeout,
        **kwargs
    )


def create_claude_model(
    model: Optional[str] = None,
    temperature: float = 0,
    timeout: int = 30,
    **kwargs
) -> ChatAnthropic:
    """
    创建 Claude (Anthropic) 模型实例
    
    Args:
        model: 模型名称,默认使用环境变量 CLAUDE_MODEL
        temperature: 温度参数,控制随机性 (0-1)
        timeout: 超时时间(秒)
        **kwargs: 其他传递给 ChatAnthropic 的参数
        
    Returns:
        ChatAnthropic 实例
        
    Example:
        >>> model = create_claude_model()
        >>> result = model.invoke("你好")
        >>> print(result.content)
    """
    api_key = ModelConfig.CLAUDE_API_KEY
    if not api_key:
        raise EnvironmentError(
            "Please set CLAUDE_API_KEY or ANTHROPIC_API_KEY environment variable"
        )
    
    return ChatAnthropic(
        model=model or ModelConfig.CLAUDE_MODEL,
        temperature=temperature,
        api_key=SecretStr(api_key),
        base_url=ModelConfig.CLAUDE_BASE_URL,
        timeout=timeout,
        **kwargs
    )


# 模型类型映射
MODEL_CREATORS = {
    "deepseek": create_deepseek_model,
    "qwen": create_qwen_model,
    "gpt": create_gpt_model,
    "openai": create_gpt_model,
    "claude": create_claude_model,
}


def create_model(
    model_type: str,
    model_name: Optional[str] = None,
    temperature: float = 0,
    timeout: int = 30,
    **kwargs
):
    """
    通用模型创建工厂函数
    
    Args:
        model_type: 模型类型 ('deepseek', 'qwen', 'gpt', 'claude')
        model_name: 具体模型名称
        temperature: 温度参数
        timeout: 超时时间
        **kwargs: 其他参数
        
    Returns:
        模型实例 (ChatOpenAI 或 ChatAnthropic)
        
    Example:
        >>> model = create_model("deepseek")
        >>> model = create_model("gpt", model_name="gpt-4")
        >>> result = model.invoke("你好")
    """
    model_type = model_type.lower()
    
    if model_type not in MODEL_CREATORS:
        raise ValueError(
            f"Unsupported model type: {model_type}. "
            f"Supported types: {list(MODEL_CREATORS.keys())}"
        )
    
    creator = MODEL_CREATORS[model_type]
    return creator(
        model=model_name,
        temperature=temperature,
        timeout=timeout,
        **kwargs
    )


# 便捷函数:快速调用
def chat(
    message: str,
    model_type: str = "deepseek",
    model_name: Optional[str] = None,
    temperature: float = 0,
    **kwargs
) -> str:
    """
    快速对话函数
    
    Args:
        message: 用户消息
        model_type: 模型类型
        model_name: 具体模型名称
        temperature: 温度参数
        **kwargs: 其他参数
        
    Returns:
        模型回复内容字符串
        
    Example:
        >>> response = chat("你好,请介绍一下自己")
        >>> print(response)
    """
    model = create_model(
        model_type=model_type,
        model_name=model_name,
        temperature=temperature,
        **kwargs
    )
    result = model.invoke(message)
    return result.content


if __name__ == "__main__":
    # 测试示例
    print("=" * 60)
    print("模型调用封装测试")
    print("=" * 60)
    
    # 测试 DeepSeek
    try:
        print("\n1. 测试 DeepSeek:")
        ds_model = create_deepseek_model()
        result = ds_model.invoke("你好,请用一句话介绍自己")
        print(f"DeepSeek: {result.content}")
    except Exception as e:
        print(f"DeepSeek 测试失败: {e}")
    
    # 测试 Qwen
    try:
        print("\n2. 测试 Qwen:")
        qwen_model = create_qwen_model()
        result = qwen_model.invoke("你好,请用一句话介绍自己")
        print(f"Qwen: {result.content}")
    except Exception as e:
        print(f"Qwen 测试失败: {e}")
    
    # 测试 GPT
    try:
        print("\n3. 测试 GPT:")
        gpt_model = create_gpt_model()
        result = gpt_model.invoke("你好,请用一句话介绍自己")
        print(f"GPT: {result.content}")
    except Exception as e:
        print(f"GPT 测试失败: {e}")
    
    # 测试 Claude
    try:
        print("\n4. 测试 Claude:")
        claude_model = create_claude_model()
        result = claude_model.invoke("你好,请用一句话介绍自己")
        print(f"Claude: {result.content}")
    except Exception as e:
        print(f"Claude 测试失败: {e}")
    
    # 测试工厂函数
    try:
        print("\n5. 测试工厂函数:")
        model = create_model("deepseek")
        result = model.invoke("Python 的优点是什么?")
        print(f"Factory: {result.content[:100]}...")
    except Exception as e:
        print(f"工厂函数测试失败: {e}")
    
    # 测试便捷函数
    try:
        print("\n6. 测试便捷函数:")
        response = chat("今天天气怎么样?", model_type="deepseek")
        print(f"Chat: {response[:100]}...")
    except Exception as e:
        print(f"便捷函数测试失败: {e}")
