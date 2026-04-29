# -*- coding:utf-8 -*-

from datetime import datetime

def __function_call(arguments):
    # 获取当前日期和时间
    now = datetime.now()
    # 格式化为 "年-月-日 时:分:秒" 的字符串并打印
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    # print(formatted_time)
    return formatted_time

function_desc_get_current_date = {
    "desc": {
        "type": "function",  # 工具类型，目前主要是 "function"
        "function": {
            "name": "get_current_date",  # 函数名
            "description": "获取当前的时间，年月日时分秒",  # 功能描述
        }
    },
    "call": __function_call
}
