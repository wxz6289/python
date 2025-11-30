from PIL import Image
import pytesseract
from pytesseract import Output
import numpy as np

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"


def clean_file(file_path, threshold):
    image = Image.open(file_path)
    image = image.point(lambda x: 0 if x < threshold else 255)
    # image.save(new_file_path)
    return image


def get_confidence(image):
    data = pytesseract.image_to_data(image, output_type=Output.DICT)
    text = data["text"]
    confidences = []
    num_chars = []

    for i in range(len(text)):
        if data["conf"][i] > -1:
            confidences.append(data["conf"][i])
            num_chars.append(len(text[i]))
    return np.average(confidences, weights=num_chars), sum(num_chars)


file_path = "./imgs/test31.png"
start = 80
step = 5
end = 200

for threshold in range(start, end, step):
    image = clean_file(file_path, threshold)
    scores = get_confidence(image)
    print(f"threshold: {threshold}, confidence: {scores[0]}, num_chars: {scores[1]}")
# print(pytesseract.image_to_string(image))
