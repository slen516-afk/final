import pytesseract
from PIL import Image

# 簡單測試
print("Tesseract Version:", pytesseract.get_tesseract_version())

# 如果要讀圖片 (假設你有放一張 test.png)
# image = Image.open('test.png')
# text = pytesseract.image_to_string(image, lang='chi_tra') # 指定繁體中文
# print(text)