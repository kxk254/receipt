import pyocr
import pyocr.builders
import re
import time
from datetime import datetime
from PIL import Image

class OcrReceipt:
    date_regex = (
        r"(([0-9]|[a-z]|[A-Z]){4,})(/|-|年)*"
        r"(([0-9]|[a-z]|[A-Z]){1,2})(/|-|月)*"
        r"(([0-9]|[a-z]|[A-Z]){1,2})日*"
        r"(\(.+\))*"  # 曜日
        r"([0-9]{1,2}:[0-9]{1,2})*|"  # 時刻
        r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})"  #add
    )  # 英字は数字が読み取れていない場合用
    # total_regex = r"(合計|小計|言十|消費税|対象計|釣り*|預か*り|外税|現金|paypay).*[0-9]*"
    total_regex = r"(合計|小計|言十|対象計|釣り|預かり|現金|paypay|支払|請求).*?[\d,]+"
    item_price_regex = (
        r"([0-9]|[a-z]|[A-Z]).{0,2}\Z"  # 末尾が数字か軽減税率の記号か英字（英字は数字が読み取れていない場合用）
    )
    top_num_regex = r"^[0-9]{3,}"
    tax_ex_regex = r"外税"
    tax_in_regex = r"(内税|内消費税等)"
    separator = r"区切位置"
    discount_regex = r"(割り*引|値引|まとめ買い*)"
    conversion_to_numeric = {
        "O": "0",
        "U": "0",
        "b": "6",
        "Z": "2",
        "<": "2",
        "i": "1",
    }
    #addition
    constax_regex = r"[TIL]?\d{12,13}\b"
    reduced_tax_regex = r"(\*|＊|※|W|w)"

    def __init__(self, text):
        self.payment_date = self.get_payment_date(text)
        self.main_contents = self.get_main_contents(text)
        self.constax = self.get_constax_matches(text)
        self.output = self.payment_date + self.main_contents + self.constax
        self.sort_process()
        # for i in sorted_output:
        #     print("result:", i)
        # return sorted_output

    def sort_process(self):
        sorted_output = sorted(self.output, key=lambda x: x["index"])
        return sorted_output
    
    def get_payment_date(self, content):
        # print("content", content)
        candidate_of_payment_date = [
            match.group()
            for s in content
            if (match := re.search(self.date_regex, s))
        ]
        # print("candidate_of_payment_date", candidate_of_payment_date)
        # 一番日付らしい行を購入日として扱う
        points = []
        for value in candidate_of_payment_date:
            # print("candidate value", value)  #debug
            point = value.count("/")
            point += value.count("年")
            point += value.count("月")
            point += value.count(":")  # 購入時刻も併記されていることが多い
            point += value.count("(")  # 購入曜日もかっこ書きで併記されていることが多い
            points.append(point)
        payment_dates_with_points_dict = [
            # candidate_of_payment_date[i] for i, point in enumerate(points) if point >= 1
            {"value": candidate_of_payment_date[i], "index": i} for i, point in enumerate(points) if point >= 1
        ]

        for entry in payment_dates_with_points_dict:
            date = entry["value"] 
            # print("date in the loop", date)
            date = re.sub(r"(\(.\).*$|[0-9]{1,2}\:[0-9]{1,2}$)", "", date)
            date  = re.sub(r"(年|月|-)", r"/", date)
            date = re.sub(r"[^0-9|^/]", r"", date)

        # 年月日の区切りがない場合や他の数値が結合している場合にある程度整形する
            try:
                split_date = date.split("/")
                if len(split_date) == 3:
                    year, month, day = split_date
                elif len(split_date) == 2:
                    # Handle cases where year is not split
                    day, month = split_date
                    year = "20" + day[:2]  # Example: handle two-digit year
                else:
                    # Fallback or error handling
                    year = month = day = "01"  # Default to first day of month

                formatted_date = f"{year}/{month}/{day}"
                entry["date"] = datetime.strptime(formatted_date, "%Y/%m/%d").strftime("%Y/%m/%d")
                # print("formatted date", entry["value"])
            except (ValueError, TypeError) as e:
                # print("value error", e)
                pass
        return payment_dates_with_points_dict
    
    
    def get_main_contents(self, content):
        new_content = []
        for ctt in content:
            ctt = ctt.replace(" ", "").lower()
            new_content.append(ctt)
        main_contents = [{"value":s, "index":new_content.index(s)} for s in new_content if re.search(self.total_regex, s)]
        for con in main_contents:
            item, price = separate_first_numeric(con["value"])
            con["item"] = item
            con["price"] = price
        main_contents = [con for con in main_contents if int(con["price"]) > 9]
        for i in main_contents:   #debug  --------
            print("main contents ", i)   #debug  --------
        return main_contents
    
    def get_constax_matches(self, text):
        # print("text", text)
        constax_matches = [
            {"value": s, "index": text.index(s)} for s in text if re.search(self.constax_regex, s)
        ]
        for con in constax_matches:
            t_num = re.search(r'\d{12,13}', con["value"])
            con["t_num"] = t_num.group() if t_num else None
        # for match in constax_matches:   # debug  --------
        #     print("constax_match: ", match)   # debug  --------
        return constax_matches
    
def separate_first_numeric(string):
    # Regular expression to find the first occurrence of numeric characters
    match = re.search(r'\d', string)
    
    if match:
        # Find the index of the first numeric character
        index = match.start()
        
        # Split the string into item and price
        item = string[:index].strip()  # Everything before the first number
        price = string[index:].strip()  # Everything from the first number onward
        price = re.sub(r'[^\d]', '', price)  # clean the price
        
        return item, price
    else:
        # No numeric characters found, return the original string as the item
        return string, ""