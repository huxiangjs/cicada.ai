# -*- coding:utf-8 -*-

from datetime import datetime, timedelta
import json

class function_date:
    def __date_info():
        now = datetime.now()
        start_of_week = now - timedelta(days=now.weekday())
        end_of_week = start_of_week + timedelta(days=6) # 0=Monday, 6=Sunday
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=999999)
        _, week_number, _ = now.isocalendar()
        return start_of_week, end_of_week, week_number

    def function_call(self, arguments):
        """
        获取当前的时间
        返回值 json格式:
            current: 当前的时间，年/月/日 时:分:秒
            start_of_week: 本周的开始时间，年/月/日 时:分:秒
            end_of_week：本周的结束时间，年/月/日 时:分:秒
            week_number：今年的第几周
        """
        # 获取当前日期和时间
        now = datetime.now()
        # 格式化为 "年-月-日 时:分:秒" 的字符串并打印
        formatted_time = now.strftime("%Y/%m/%d %H:%M:%S")
        # print(formatted_time)
        # 获取本周信息
        start_of_week, end_of_week, week_number = function_date.__date_info()
        sw_str = start_of_week.strftime('%Y/%m/%d %H:%M:%S')
        ew_str = end_of_week.strftime('%Y/%m/%d %H:%M:%S')
        wn_str = str(week_number)
        # print(sw_str, ew_str, wn_str)
        info = {
            "current": formatted_time,
            "start_of_week": sw_str,
            "end_of_week": ew_str,
            "week_number": wn_str
        }
        result_json_str = json.dumps(info, indent=4, ensure_ascii=False)
        return result_json_str

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
