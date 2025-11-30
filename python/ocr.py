import pytesseract
from PIL import Image

# 打开图像文件
image = Image.open('images/test.jpg')

# 使用pytesseract进行文本识别
text = pytesseract.image_to_string(image)

# 打印识别结果
print(text)
