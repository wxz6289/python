from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
  client = Anthropic(
    # base_url='https://api.openai-proxy.org/anthropic',
    api_key= os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('ANTHROPIC_BASE_URL'),
  )

  message = client.messages.create(
    max_tokens=1024,
    messages=[
      {
        "role": "user",
        "content": "Hello, Claude",
      }
    ],
    model="claude-haiku-4-5",
  )
  print(message.content)
