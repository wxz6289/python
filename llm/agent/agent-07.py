import os
from dotenv import load_dotenv
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

OUTPUT_DIR = os.path.join(BASE_DIR, "resources")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "elevenlabs-text-to-speech.mp3")
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


def get_elevenlabs_config() -> tuple[str, str]:
  api_key = os.getenv("ELEVENLABS_API_KEY")
  if not api_key:
    raise EnvironmentError("请先设置 ELEVENLABS_API_KEY")

  voice_id = os.getenv("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
  return api_key, voice_id


def generate_speech(api_key: str, voice_id: str, text: str, output_file: str) -> None:
  os.makedirs(os.path.dirname(output_file), exist_ok=True)

  response = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    headers={
      "xi-api-key": api_key,
      "Accept": "audio/mpeg",
      "Content-Type": "application/json",
    },
    json={
      "text": text,
      "model_id": "eleven_multilingual_v2",
      "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
      },
    },
    timeout=60,
  )
  response.raise_for_status()

  with open(output_file, "wb") as f:
    f.write(response.content)


if __name__ == "__main__":
  api_key, voice_id = get_elevenlabs_config()
  text = (
    "你好，请声情并茂地朗诵以下这首古诗:"
    "远上寒山石径斜，白云生处有人家。"
    "停车坐爱枫林晚，霜叶红于二月花。"
  )

  generate_speech(api_key, voice_id, text, OUTPUT_FILE)
  print(f"音频已保存到: {OUTPUT_FILE}")
