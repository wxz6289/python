import anthropic
import os

client = anthropic.Anthropic(
    base_url="https://api.mcxhm.cn",
    api_key="sk-cf1wIjsmF8Hkuk2lCX3I9Nl6WuDMDk1iKrU7jq205jlyZwDx",
)

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "你好，请介绍一下anthropic",
        }
    ],
)
print(message.content)
