import os
from dotenv import load_dotenv
from pprint import pprint
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langchain.chat_models import init_chat_model

load_dotenv()

# After a model makes a tool call
# (Here, we demonstrate manually creating the messages for brevity)
ai_message = AIMessage(
  content=[],
  tool_calls=[{
    "name": "get_weather",
    "args": {"location": "San Francisco"},
    "id": "call_123"
  }]
)

# Execute tool and create result message
weather_result = "Sunny, 72°F"
tool_message = ToolMessage(
  content=weather_result,
  tool_call_id="call_123"  # Must match the call ID
)

# Continue conversation
messages = [
  HumanMessage("What's the weather in San Francisco?"),
  ai_message,  # Model's tool call
  tool_message,  # Tool execution result
]

model = init_chat_model(
  model="gpt-5-nano",
  api_key=os.getenv('CLOSEAI_API_KEY'),
  base_url=os.getenv('CLOSEAI_BASE_URL'),
  temperature=0.0)

response = model.invoke(messages)  # Model processes the result
pprint(response)
