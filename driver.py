from __future__ import annotations
import platform
from typing import List,Dict
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, UnexpectedAlertPresentException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys # for pressing command button
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions # for wait
from selenium.webdriver.support.ui import Select # for dropdown menu selection
from selenium.webdriver import FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager



import time

WebElement = webdriver.remote.webelement.WebElement
Cookies = List[Dict[str, str]]

class Driver:
    def __init__(self, is_headless:bool = False, is_full_size_screen:bool = False) -> None:
        self.driver = None
        self.searched_element = None
        self.select = None

        self.is_headless = is_headless
        self.is_full_size_screen = is_full_size_screen
        

    def get_current_url(self) -> str:
        return self.driver.current_url
    
    def get_current_page_title(self) -> str:
        return self.driver.title
    
    def maximize_window(self) -> Driver:
        self.driver.maximize_window()
        return self

    def open_firefox_browser(self) -> Driver:
        opts = FirefoxOptions()
        if self.is_headless:
            opts.add_argument("--headless")
        
        opts.set_preference("general.useragent.override", 
        "userAgent=Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0")
        opts.set_preference("dom.webdriver.enabled", False)
        opts.set_preference("browser.cache.disk.enable", False)
        opts.set_preference("browser.cache.memory.enable", False)
        opts.set_preference("browser.cache.offline.enable", False)
        opts.set_preference("network.http.use-cache", False) 

        platform_name = platform.system().lower()
        if "mac" in platform_name:
            self.driver = webdriver.Firefox(options=opts, executable_path=GeckoDriverManager().install())
        elif "linux" in platform_name:
            self.driver = webdriver.Firefox(options=opts)
        self.driver.delete_all_cookies()
        
        return self

    def open_url(self, url:str) -> Driver:
        print(f"Open Url: {url}")
        self.driver.get(url)
        return self

    def get_cookies(self) -> Cookies:
        return self.driver.get_cookies()
    
    def set_cookie(self,new_cookie:List[Dict[str,str]], target_domain_name:str) -> Driver:
        self.driver.delete_all_cookies()
        
        for cookie_dict in new_cookie:
            if not isinstance(cookie_dict, dict):
                continue
            if target_domain_name not in cookie_dict["domain"]:
                continue

            self.driver.add_cookie(cookie_dict)    
        return self
    
    def find_element_by(self, by:By,searched_element:str) -> Driver:
        self.searched_element = self.driver.find_element(by, searched_element)
        return self
    
    def find_multiple_elements_by(self, by:By,searched_element:str) -> List[WebElement]:
        return self.driver.find_elements(by, searched_element)
    
    def enter_input(self, _input:str) -> Driver:
        self.searched_element.send_keys(_input)
        return self
    
    def clear_input_field(self) -> Driver:
        self.searched_element.clear()
        return self
    
    def click_n_times(self, n:int = 1) -> Driver:
        for current_n in range(n):
            self.searched_element.click()
        return self
        
    def select_by_visible_text(self, text:str) -> Driver:
        Select(self.searched_element).select_by_visible_text(text)
        return self

    def select_by_value(self, value:str) -> Driver:
        Select(self.searched_element).select_by_value(value)
        return self
    
    def press_enter(self) -> Driver:
        self.searched_element.send_keys(Keys.RETURN)
        return self

    def press(self, key:Keys) -> Driver:
        self.searched_element.send_keys(key)
        return self
    
    def wait_n_seconds(self, n:float) -> Driver:
        time.sleep(n)
        return self
    
    def wait_until(self, max_wait_n_seconds:float, by:By,element_name_presented:str) -> Driver:
        self.searched_element =  (
            WebDriverWait(self.driver, max_wait_n_seconds).until(
            expected_conditions.presence_of_element_located(
                                                             (by, element_name_presented)
                                                            )
                        )
        )
        return self
    
    def wait_until_clickable(self, max_wait_n_seconds:float, by:By,element_name_clicked:str) -> Driver:
        self.searched_element =  (
            WebDriverWait(self.driver, max_wait_n_seconds).until(
            expected_conditions.element_to_be_clickable(
                                                            (by, element_name_clicked)
                                                        )
                        )
        )
        return self
    
    def refresh(self) -> Driver:
        self.driver.refresh()
        return self

    def is_alert_present(self) -> bool:
        try:
            alert_obj = self.driver.switch_to.alert
            print(f"Alert: {alert_obj.text}")
            return True
        except UnexpectedAlertPresentException:
            return True
        except NoAlertPresentException:
            return False
        
    def is_alert_contains_text(self, text:str) -> bool:
        if not self.is_alert_present():
            return False

        alert_obj = self.driver.switch_to.alert
        return text in alert_obj.text

    def accept_alert(self) -> None:
        if not self.is_alert_present():
            return

        alert_obj = self.driver.switch_to.alert
        print(f"Alert: {alert_obj.text} is accepted")
        alert_obj.accept()
    
    def get_alert_text(self) -> str:
        alert_obj = self.driver.switch_to.alert
        alert_text = alert_obj.text
        return alert_text
       
    
    def screenshot_element(self, by:By, searched_element:str, file_name: str = None) -> bytes:
        binary_img = self.driver.find_element(by, searched_element).screenshot_as_png
        if file_name is None:
            return binary_img
        with open(file_name, "wb") as file:
            file.write(binary_img)
        
        
    def is_element_exists_by(self, by:By, searched_element:str) -> bool:
        try:
            self.driver.find_element(by, searched_element)
        except NoSuchElementException:
            return False
        return True
    
    def execute_script(self, script: str) -> Driver:
        self.driver.execute_script(script)

        return self
    
    def close_browser(self) -> None:
        if self.driver is None:
            return

        print("Closing Browser..")
        self.driver.quit()
        self._destrctor()
        print("Browser is closed")
        
    def _destrctor(self) -> None:
        self.driver = None
        self.searched_element = None
        self.select = None

    def __repr__(self):
        return f"At {self.driver.current_url}, in {self.driver.current_window_handle} Window"