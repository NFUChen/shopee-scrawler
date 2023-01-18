

from typing import Callable
import traceback
import sys

def print_error_message(func:Callable) -> Callable:
    def _get_error_detail(error:Exception) -> str:
        error_class_name = error.__class__.__name__ # 引發錯誤的 class 名稱
        error_detail = error.args[0] # 得到詳細的訊息
        _, _, trace_back = sys.exc_info() # 得到錯誤的完整資訊 Call Stack
        last_call_stack = traceback.extract_tb(trace_back)[-1] # 取得最後一行的錯誤訊息
        file_name_error_occurred, error_line_number, func_name, _ = last_call_stack # 錯誤的檔案位置名稱
        # 產生錯誤訊息
        error_msg = f"Exception raise in file: {file_name_error_occurred}, line {error_line_number}, in {func_name}: [{error_class_name}] {error_detail}."
        return error_msg

    def wrapper(*args, **kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as error:
            error_msg = _get_error_detail(error)
            print(error_msg)
    return wrapper