from __future__ import annotations
from typing import List ,Dict, Tuple, Union
from threading import Thread
import time
from product_info import ProductInfo
from driver import Driver
from exception_decor import print_error_message


def extract_number(number_string: str) -> float:
    try:
        chinese_unit = {
            "百": 100, "千": 1000, "萬": 10000
        }
        temp_numbers = []
        unit = None
        for word in number_string:
            if word.isdigit() or word == ".":
                temp_numbers.append(word)
            if word in chinese_unit:
                unit = chinese_unit[word]
        number = float("".join(temp_numbers))
        if unit is None:
            return number

        return number * unit
    except Exception as error:
        return number_string

def conver_dates(date_string: str) -> int:
    chinese_date_unit = {
        "月": 30, "年": 365
    }
    temp_numbers = []
    unit = None
    for word in date_string:
        if word.isdigit():
            temp_numbers.append(word)
        if word in chinese_date_unit:
            unit = chinese_date_unit[word]
    number = int("".join(temp_numbers))
    
    return number * unit


class ProductInfoListener:
    SHOPEE_URL = "https://shopee.tw/"
    def __init__(self) -> None:
        self.driver = Driver(is_headless= False)
        self.info_scraped:List[ProductInfo] = []
    
        self.item_with_element_type_and_element_name: Dict[str, Tuple(str, str)] = {
            "product_name": ("css selector","._44qnta"),
            "number_of_stars": ("css selector", '._046PXf'),
            "number_of_comments": ("css selector", 'div.IZIVH\+:nth-child(2)'),
            "quantity_sold": ("css selector", ".jgUbWJ"),
            "quantity_remaining": ("css selector", "._6lioXX"),
            "price_range": ("css selector", ".pqTWkA"),
            "free_shipment_fee_threshold": ("css selector", "._7K5or9"),
            "number_of_likes": ("css selector", "div.Ne7dEf:nth-child(2)"),
            "number_of_market_comments": ("css selector", "div.Odudp\+:nth-child(1) > div:nth-child(1) > span:nth-child(2)"),
            "number_of_market_product": ("css selector", ".vUG3KX"),
            "chat_response_speed": ("css selector", "div.Odudp\+:nth-child(2) > div:nth-child(2) > span:nth-child(2)"),
            "chat_response_rate": ("css selector", "div.Odudp\+:nth-child(2) > div:nth-child(1) > span:nth-child(2)"),
            "join_time": ("css selector", "div.Odudp\+:nth-child(3) > div:nth-child(1)"),
            "number_of_fans": ("css selector", "div.Odudp\+:nth-child(3) > div:nth-child(2)")
            
        }
            
        self.number_attrs = [
            "number_of_stars", 
            "number_of_comments", 
            "quantity_sold", 
            "quantity_remaining", 
            "free_shipment_fee_threshold", 
            "number_of_likes", 
            "number_of_market_comments", 
            "number_of_market_product", 
            "chat_response_rate", 
            "number_of_fans"
        ]
        
        self.date_attrs = [
            "join_time"
        ]
    
    def _is_in_product_page(self) -> bool:
        current_url = self.driver.get_current_url()
        
        return "sp_atk" in current_url
    
    def is_in_login_page(self) -> bool:
        return "login" in self.driver.get_current_url()
    
    def is_in_verification_page(self) -> bool:
        return "verify" in self.driver.get_current_url()
        
    def _go_to_shopee_official_website(self) -> ProductInfoListener:
        self.driver.open_firefox_browser().open_url(self.SHOPEE_URL).wait_n_seconds(3)
        
        return self

    @print_error_message
    def _get_product_info_dict(self) -> Union[None, Dict[str, str]]:
        if not self._is_in_product_page():
            return

        try:
            info_dict = {}
            for item_name, element_type_and_element_name in self.item_with_element_type_and_element_name.items():
                element_type, element_name = element_type_and_element_name
                if not self.driver.is_element_exists_by(element_type, element_name):
                    print(f"[{element_type}] {element_name} for {item_name} is not exists.")
                    info_dict[item_name] = None
                    continue
                text = self.driver.find_element_by(element_type, element_name).searched_element.text
                if item_name in self.number_attrs:
                    info_dict[item_name] = extract_number(text)
                elif item_name in self.date_attrs:
                    info_dict[item_name] = conver_dates(text)
                else:
                    info_dict[item_name] = text

            info_dict["is_preferred_seller"] = True if "優選" in info_dict["product_name"] else False
            info_dict["product_url"] = self.driver.get_current_url()
        
            return info_dict
        except Exception as error:
            print(error)
            return
        
    def go_to_product_url(self, url: str) -> None:
        self.driver.open_url(url)

    
    def listen(self) -> Dict[str, str]:
        try:
            self._go_to_shopee_official_website()
            while (True):
                if not self._is_in_product_page():
                    time.sleep(0.5)
                    continue

                info_dict = self._get_product_info_dict()
                if info_dict is None:
                    continue
                
                product_info = ProductInfo(info_dict)
                if product_info not in self.info_scraped:
                    print(product_info)
                    self.info_scraped.append(product_info)
        except KeyboardInterrupt:
            self.driver.close_browser()
            
        
    
    def run(self) -> None:
        Thread(target= self.listen).start()
        
    def close(self) -> None:
        self.driver.close_browser()