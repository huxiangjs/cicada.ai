# -*- coding:utf-8 -*-

import tools.function_date.date
import tools.function_weather.weather

all_function = [
    tools.function_date.date.function_desc_get_current_date,
    tools.function_weather.weather.function_desc_get_weather
]

def get_function_desc():
    functions_desc = [_['desc'] for _ in all_function]
    # print(functions_desc)
    return functions_desc

def call_function(func, arguments):
    for item in all_function:
        if item['desc']['function']['name'] == func:
            return item['call'](arguments)
    return 'ERROR'

# print(get_function_desc())
