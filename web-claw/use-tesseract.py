from PIL import Image
import pytesseract
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

print(pytesseract.image_to_string(Image.open('./imgs/linear-gradent.png')))
# print(pytesseract.image_to_data(Image.open('./imgs/test3.png'), output_type=Output.DICT))
# print(pytesseract.image_to_data(Image.open('./imgs/test3.png'), output_type=Output.BYTES))
