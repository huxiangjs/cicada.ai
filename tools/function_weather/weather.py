import requests

def __function_call(arguments):
    """
    使用 wttr.in 获取指定城市的天气
    """
    # ?format=3 参数可以返回一行精简的天气信息
    # url = f"https://wttr.in/{city_name}?format=3&lang=zh"
    # url = f"https://wttr.in/{arguments['city_name']}?format=地点:+%l\n+天气状况(表情符号):+%c\n+天气状况(文字):+%C\n+当前温度:+%t\n+体感温度:+%f\n+风速:+%w\n+湿度:+%h\n+降水量:+%p\n&lang=zh"
    url = f"https://wttr.in/{arguments['city_name']}?format=j2&lang=zh"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # wttr.in 的 format=3 返回的是纯文本
        # print(response.text.strip())
        return response.text
    except requests.exceptions.RequestException as e:
        # print(f"❌ 请求失败: {e}")
        return "查询失败"

function_desc_get_weather = {
    "desc": {
        "type": "function",  # 工具类型，目前主要是 "function"
        "function": {
            "name": "get_weather",  # 函数名
            "description": "获取指定城市当前的天气状况和未来2天的天气状况，返回为json数据",  # 功能描述
            "parameters": {  # 参数定义，遵循 JSON Schema
                "type": "object",
                "properties": {
                    "city_name": {
                        "type": "string",
                        "description": "要查询的城市名称，例如 北京、上海"
                    },
                },
                "required": ["city_name"]  # 指定必填参数
            }
        }
    },
    "call": __function_call
}

if __name__ == "__main__":
    print(__function_call({"city_name": "上海"}))
