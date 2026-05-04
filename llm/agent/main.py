from openai import OpenAI
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from dotenv import load_dotenv
import os

load_dotenv()

client = wrap_openai(OpenAI(
  api_key=os.environ["OPENAI_API_KEY"],
  base_url=os.environ["OPENAI_BASE_URL"],
))

@traceable
def get_context(question: str) -> str:
    """Get context for given question"""
    # query from a knowledge or vector store
    return f"The answer to {question} is always 42."

@traceable
def assistant(question: str) -> str:
    context = get_context(question)
    respone = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {
              "role": "system",
              "content": f"Answer using the context below. \n\n context: {context}"},
            {
              "role": "user",
              "content": f"{question}"
            },
        ],
    )
    return respone.choices[0].message.content

def main():
    result  = assistant("你是谁?")
    print(result)


if __name__ == "__main__":
    main()
