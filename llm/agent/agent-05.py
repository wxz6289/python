import os
import base64
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

OUTPUT_DIR = os.path.join(BASE_DIR, "resources")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dalle-text-to-image.png")


def build_client() -> OpenAI:
  api_key = os.getenv("CLOSEAI_API_KEY")
  if not api_key:
    raise EnvironmentError("请先设置CLOSEAI_API_KEY")

  base_url = os.getenv("OPENAI_BASE_URL")
  if base_url:
    return OpenAI(api_key=api_key, base_url=base_url)
  return OpenAI(api_key=api_key)


def save_base64_image(image_base64: str, output_file: str) -> None:
  os.makedirs(os.path.dirname(output_file), exist_ok=True)
  with open(output_file, "wb") as f:
    f.write(base64.b64decode(image_base64))


if __name__ == "__main__":
  client = build_client()
  prompt = (
    "一只穿着宇航服的橘猫坐在月球表面，"
    "远处能看到蓝色地球，电影感灯光，细节丰富，数字插画风格。"
  )

  response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
    response_format="b64_json",
  )

  image_base64 = response.data[0].b64_json
  if not image_base64:
    raise RuntimeError("图片生成成功，但响应中没有 b64_json 数据。")

  save_base64_image(image_base64, OUTPUT_FILE)
  print(f"图片已保存到: {OUTPUT_FILE}")
