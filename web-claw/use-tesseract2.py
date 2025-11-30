from PIL import Image
import pytesseract
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

def clean_file(file_path, new_file_path):
  image = Image.open(file_path)
  image = image.point(lambda x: 0 if x < 130 else 255)
  image.save(new_file_path)
  return image

image = clean_file('./imgs/test31.png', './imgs/cleaned.png')
print(pytesseract.image_to_string(image))
