import os
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

OUTPUT_DIR = os.path.join(BASE_DIR, "resources")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "text-to-speech.mp3")


def build_client() -> OpenAI:
  api_key = os.getenv("CLOSEAI_API_KEY")
  if not api_key:
    raise EnvironmentError("请先设置CLOSEAI_API_KEY")

  base_url = os.getenv("OPENAI_BASE_URL")
  if base_url:
    return OpenAI(api_key=api_key, base_url=base_url)
  return OpenAI(api_key=api_key)


def generate_speech(client: OpenAI, text: str, output_file: str) -> None:
  os.makedirs(os.path.dirname(output_file), exist_ok=True)

  with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input=text,
    response_format="mp3",
  ) as response:
    response.stream_to_file(output_file)


if __name__ == "__main__":
  client = build_client()
  text = (
    "你好，这是一个 OpenAI 文本生成音频的示例。"
    "我们会把这段中文文本转换成 MP3 音频文件。"
  )

  generate_speech(client, text, OUTPUT_FILE)
  print(f"音频已保存到: {OUTPUT_FILE}")
