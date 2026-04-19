import os

from langchain.agents import create_agent
from chat2 import AuthenticationError, RateLimitError


def get_weather(city: str) -> str:
    """Get weather for given city"""
    return f"It's always sunny in {city}."


def print_agent_result(result: dict) -> None:
    messages = result.get("messages", [])
    if not messages:
        print(result)
        return

    last = messages[-1]
    content = getattr(last, "content", None)
    print(content if content else result)


def main() -> None:
    # DeepSeek uses an OpenAI-compatible API.
    # Always prefer DEEPSEEK_API_KEY and map it to OPENAI_API_KEY for LangChain/OpenAI clients.
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_api_key:
        os.environ["OPENAI_API_KEY"] = deepseek_api_key

    # Default DeepSeek base URL (can be overridden by OPENAI_BASE_URL).
    os.environ.setdefault("OPENAI_BASE_URL", "https://api.deepseek.com/v1")

    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError(
            "Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY) before running."
        )

    agent = create_agent(
        model="openai:deepseek-chat",
        tools=[get_weather],
        system_prompt="You are a helpful assistant.",
    )

    city = "San Francisco"
    user_message = f"What is the weather in {city}?"

    try:
        result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
        print_agent_result(result)
    except AuthenticationError as e:
        print("Authentication failed (401).")
        print("Please verify your DEEPSEEK_API_KEY is valid.")
        print("Fallback result:", get_weather(city))
        print("Raw error:", e)
    except RateLimitError as e:
        print("DeepSeek/OpenAI-compatible API quota exceeded (429).")
        print("Fallback result:", get_weather(city))
        print("Raw error:", e)


if __name__ == "__main__":
    main()
