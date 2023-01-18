from __future__ import annotations
from typing import List
import time
from driver import Driver

class ProductAddressCrawler:
    def __init__(self, keyword: str, number_of_page_collected: None | int = None):
        self.keyword = keyword
        self.number_of_page_collected = number_of_page_collected
        self.product_list_url = f"https://shopee.tw/search?keyword={keyword}"
        self.driver = Driver(is_headless= False)
        
        self.total_number_of_pages:int = 0
        self.query_urls = []
        
        
    def _go_to_query_url(self) -> ProductAddressCrawler:
        self.driver.open_firefox_browser().open_url(self.product_list_url).wait_n_seconds(5)
        
        
            
        return self
    
   
    def _scroll_to_button(self) -> None:
        for scroll in range(6):
            self.driver.execute_script('window.scrollBy(0,1000)')
            time.sleep(3)
        print("Till Button")
            
    def get_all_product_urls(self) -> List[str]:
        print("Scraping...")
        if not self.driver.is_element_exists_by("class name", "shopee-search-item-result__items"):
            return []
        
        all_anchor_tags = self.driver.find_element_by("class name", "shopee-search-item-result__items").searched_element.find_elements("tag name", "a")
        print("collected.")
        all_urls = [tag.get_attribute("href") for tag in all_anchor_tags]
        return all_urls
    
    def _get_total_number_of_pages(self) -> int:
        self.driver.wait_until(5,"class name", "shopee-mini-page-controller__total")
        
        return int(self.driver.find_element_by("class name", "shopee-mini-page-controller__total").searched_element.text)
    
    def _is_in_search_page(self) -> bool:
        return "shopee.tw/search?keyword" in self.driver.get_current_url()
    
    def _is_in_verification_page(self) -> bool:
        return "verify" in self.driver.get_current_url()
    
    def collect_product_urls(self) -> List[str]:
        
        self._go_to_query_url()
        while (True):
            if self._is_in_search_page():
                break
            time.sleep(1.0)
        
        self.total_number_of_pages = self._get_total_number_of_pages()
        
        all_product_urls = []
        all_urls = [ f"https://shopee.tw/search?keyword={self.keyword}&page={page_num}" 
        for page_num in range(self.number_of_page_collected or self.total_number_of_pages) ]
        
        while (True):    
            if not self._is_in_search_page():
                time.sleep(1.0)
                continue
            for query_url in all_urls:
                self.driver.open_url(query_url)
                self._scroll_to_button()
                current_page_product_urls = self.get_all_product_urls()
                all_product_urls.append(current_page_product_urls)
            break
            
        
        
        self.driver.close_browser()
        
        return sum(all_product_urls, [])
    