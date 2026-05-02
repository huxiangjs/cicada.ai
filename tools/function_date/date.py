# -*- coding:utf-8 -*-

from datetime import datetime

class function_date:
    def function_call(self, arguments):
        """
        获取当前的时间
        返回值: 年月日时分秒
        """
        # 获取当前日期和时间
        now = datetime.now()
        # 格式化为 "年-月-日 时:分:秒" 的字符串并打印
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        # print(formatted_time)
        return formatted_time

    def __init__(self):
        self.function_desc = {
            "desc": {
                "type": "function",  # 工具类型，目前主要是 "function"
                "function": {
                    "name": "get_current_date",  # 函数名
                    "description": function_date.function_call.__doc__.strip(),  # 功能描述
                }
            },
            "call": self.function_call
        }

if __name__ == "__main__":
    print(function_date().function_call(None))
