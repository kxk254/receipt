from PIL import Image
import pytesseract
import pyocr
import pyocr.builders
import cv2
import numpy as np
from .ocr_text import OcrReceipt
import os
from datetime import datetime
from receipts.models import 項目リスト, PDF番号

# pip install prepro
# If you're on Windows, you'll need to specify the path to the Tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# pyocr.tesseract.TESSERACT_CMD = r'C:\\Users\\konno\\OneDrive - SCM\\Dev\\sapps\\Tesseract-OCR\\tesseract.exe'
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\konno\\OneDrive - SCM\\Dev\\sapps\\Tesseract-OCR\\tesseract.exe'

pyocr.tesseract.TESSERACT_CMD = '/usr/bin/tesseract'
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# img_cv = cv2.imread(image_path)
# img_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
text_dic = {}

def gray1(img_path):
    img = cv2.imread(str(img_path))
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised_img = cv2.bilateralFilter(gray_img, 9, 75, 75)
    return denoised_img

"""
OCRのデータをViewで表示できるように整列させる
"""
def ocr_get(image_path):
    print("ocr_get passing point 1", image_path)
    img= gray1(image_path)
    text_gray_pyt = pytesseract.image_to_string(img, lang='jpn')
    print("ocr_get text_gray_pyt point 4", text_gray_pyt)
    text_dic["gray_pyt"] = text_gray_pyt
    print("OCR raw output repr:", repr(text_gray_pyt))
    print("gray1 debug", type(img), img.shape)
    print("text_dic", text_dic)


    for k, text in text_dic.items():
        text = text.splitlines()
        print("inside text_dic.items loop text===>", text)
        ocr = OcrReceipt(text)
        ocrs = ocr.sort_process()
        for o in ocrs:
            print("ocr_get: ocr result", o)

    print("ocr_get passing point 2")
    fin_results = []
    # Variable to keep track of the last non-empty value
    date_index_value = [ocr.get('index') for ocr in ocrs if "date" in ocr]
    t_num_index_value = [ocr.get('index') for ocr in ocrs if "t_num" in ocr]
    price_index_value = [ocr.get('index') for ocr in ocrs if "price" in ocr]

    for ocr in ocrs:
        index = ocr["index"]
        
        if ocr.get("date", '') == '':
            closest_date_index = min((date_index for date_index in date_index_value if date_index != index), key=lambda x: abs(x-index), default=None)
            if closest_date_index is not None:
                closest_date_ocr = next((entry for entry in ocrs if entry["index"] == closest_date_index), None)
                if closest_date_ocr and "date" in closest_date_ocr:
                    ocr["date"] = closest_date_ocr["date"]
        
        if ocr.get("t_num", '') == '':
            closest_t_num_index = min((t_num_index for t_num_index in t_num_index_value if t_num_index != index), key=lambda x: abs(x-index), default=None)
            if closest_t_num_index is not None:
                closest_t_num_ocr = next((entry for entry in ocrs if entry["index"] == closest_t_num_index), None)
                if closest_t_num_ocr and "t_num" in closest_t_num_ocr:
                    ocr["t_num"] = closest_t_num_ocr["t_num"]
        
        if ocr.get("price", '') == '':
            closest_price_index = min((price_index for price_index in price_index_value if price_index != index), key=lambda x: abs(x-index), default=None)
            if closest_price_index is not None:
                closest_price_ocr = next((entry for entry in ocrs if entry["index"] == closest_price_index), None)
                if closest_price_ocr and "price" in closest_price_ocr:
                    ocr["price"] = closest_price_ocr["price"]

    if price_index_value in ocrs:
        ocrs.remove(price_index_value)
        
    # for o in ocrs:
    #         print("result", o)
    
    return ocrs

"""
データをReceiptモデルに合うように標準化させる
"""
def get_initial_data(ocrs, id):

    instance = PDF番号.objects.filter(id=id).first()
    print("ocr_main.py.get_initial_data #1 and ocrs ==", ocrs)
    for o in ocrs:
            try:
                if isinstance(o["date"], str):
                    try:
                        date_obj = datetime.strptime(o["date"], "%Y/%m/%d")  # Adjust the format if necessary
                    except ValueError:
                        date_obj = datetime.now()  # Or set a default value

                    o["date"] = date_obj.strftime("%Y-%m-%d")
                else:
                    o["date"] = o["date"].strftime("%Y-%m-%d")
            except:
                o["date"] = datetime.today().strftime('%Y-%m-%d')
        
    for o in ocrs:
        if "date" in o:
            o["日付"] = o.pop("date")
        else:
            o["日付"] = datetime.today().strftime('%Y-%m-%d')
        if "t_num" in o:
            o["登録番号"] = o.pop("t_num")
        else:
            o["登録番号"] = 0
        if "price" in o:
            o["価格"] = o.pop("price")
        else:
            o["価格"] = 0
        o["備考"] = ''
        o['項目コード'] = 項目リスト.objects.get(項目コード="001")
        o['PDF番号'] = instance
        o['DELETE'] = True
        o.pop("value")
        o.pop("index")

    print("get_initial_data ocrs ===", ocrs)
    initial_data = [ocrs[i] for i in range(len(ocrs))]

    return initial_data
