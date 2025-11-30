from PIL import Image, ImageDraw, ImageFont, ImageFilter

kitten = Image.open('./imgs/kitten.png')
women = Image.open('./imgs/women.png')
ft = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 60)

blurry_kitten = kitten.filter(ImageFilter.GaussianBlur)
draw = ImageDraw.Draw(blurry_kitten)
draw.text((30, 40), u'Dreamer', ft=ft, fill='green')
rotated_women = women.rotate(45, expand=True)
w, h = rotated_women.size
rotated_women.thumbnail((w/2, h/2))
blurry_kitten.paste(rotated_women, (200, 100))
blurry_kitten.save('./imgs/kitten_blurred.png')
blurry_kitten.show()