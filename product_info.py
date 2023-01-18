from __future__ import annotations
from typing import Dict

class ProductInfo:
    def __init__(self, info_dict: Dict[str, str]) -> None:
        self.info_dict = info_dict
    
    def __eq__(self, __o: ProductInfo) -> bool:
        return self.info_dict["product_name"] == __o.info_dict["product_name"]
    
    def __repr__(self) -> str:
        return f"{self.info_dict}"