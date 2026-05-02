# -*- coding:utf-8 -*-

if __name__ == "__main__":
    import sys as s
    import os as o
    project_root = o.path.dirname(o.path.dirname(o.path.abspath(__file__)))
    print(project_root)
    if project_root not in s.path:
        s.path.insert(0, project_root)

import tools.function_date.date
import tools.function_weather.weather
import tools.function_alarm.alarm

class functions:
    def __init__(self):
        self.__all_function = [
            tools.function_date.date.function_date(),
            tools.function_weather.weather.function_weather(),
            tools.function_alarm.alarm.function_alarm(),
        ]

    def get_function_desc(self):
        functions_desc = [_.function_desc['desc'] for _ in self.__all_function]
        # print(functions_desc)
        return functions_desc

    def call_function(self, func, arguments):
        for item in self.__all_function:
            desc = item.function_desc
            if desc['desc']['function']['name'] == func:
                return desc['call'](arguments)
        return 'ERROR'

    def init_function(self, callback, args=None):
        for item in self.__all_function:
            desc = item.function_desc
            if 'init' not in desc:
                    continue
            desc['init'](callback, args)

    def deinit_function(self):
        for item in self.__all_function:
            desc = item.function_desc
            if 'deinit' not in desc:
                    continue
            desc['deinit']()

if __name__ == "__main__":
    import json as j
    result_list = functions().get_function_desc()
    result_json_str = j.dumps(result_list, indent=4, ensure_ascii=False)
    print(result_json_str)
