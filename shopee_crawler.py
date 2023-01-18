from typing import List, Dict
import time
import uuid
import pandas as pd
from product_address_crawler import ProductAddressCrawler
from product_info_listener import ProductInfoListener

class ShopeeCrawler:
    def __init__(self, keyword: str, number_of_pages: int | None = None) -> None:
        self.listener_browser = ProductInfoListener()
        self.address_scraper = ProductAddressCrawler(keyword, number_of_pages)
    
    def collect_info_into_df(self) -> pd.core.frame.DataFrame:
        random_file_name = uuid.uuid4()
        
        try:
            self.listener_browser.run()
            all_product_urls = self.address_scraper.collect_product_urls()
            for idx, url in enumerate(all_product_urls):
                print(f"{idx+1}/{len(all_product_urls) + 1}")
                while self.listener_browser.is_in_login_page() or self.listener_browser.is_in_verification_page():
                    time.sleep(1)
                # in product page, waiting 5 secs
                self.listener_browser.go_to_product_url(url)
                time.sleep(5)
            self.listener_browser.close()

            df = pd.DataFrame(
                [info.info_dict for info in self.listener_browser.info_scraped]
            )
            return df
        except Exception as error:
            print(error)
            df = pd.DataFrame(
                [info.info_dict for info in self.listener_browser.info_scraped]
            )
            return df
        finally:
            df.to_csv(f"{random_file_name}.csv", encoding= "utf_8_sig")