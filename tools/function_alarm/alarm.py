# -*- coding:utf-8 -*-

import threading
import schedule # pip install schedule
import time

class function_alarm:
    def __alarm_del(self, name):
        job = self.__alarm_list[name][0]
        schedule.cancel_job(job)
        del self.__alarm_list[name]
        print('删除闹钟:', name)

    def __alarm_callback(self, name):
        if self.__callback:
             self.__callback(f"这是一个system消息注入: 现在名为'{name}'、id为'{self.__alarm_list[name][2]}'的闹钟到期了, "
                              "你应该仔细检查闹钟名字和id, 确保和设置的闹钟匹配, 之后根据需要你可以提示user或者调用tool",
                              self.__args)
        if  self.__alarm_list[name][1] == '一次':
            self.__alarm_del(name)

    def function_call(self, arguments):
        """
        设置闹钟
        """
        if arguments['op'] == 'add':        # 添加一个闹钟
            type = arguments['type'] # 每次/一次
            unit = arguments['unit'] # 秒/分钟/小时/天/周一/周二/周三/周四/周五/周六/周日
            value = arguments['value']
            if unit in '秒/分钟/小时':
                alarm_name = f'{value}{unit}'
            elif unit in '天/周一/周二/周三/周四/周五/周六/周日':
                alarm_name = f'{unit}{value}'
            else:
                return '出错: 非法的unit参数取值'
            if type == '每次':
                alarm_name = f'每{alarm_name}响一次'
            elif type == '一次':
                if unit in '秒/分钟/小时':
                    alarm_name = f'{alarm_name}后响一次'
                elif unit == '天':
                    alarm_name = f'今{alarm_name}响一次'
                else:
                    alarm_name = f'这{alarm_name}响一次'
            else:
                return '出错: 非法的type参数取值'
            # 设置
            try:
                if unit == '秒':
                    job = schedule.every(int(value)).seconds.do(self.__alarm_callback, alarm_name)
                elif unit == '分钟':
                    job = schedule.every(int(value)).minutes.do(self.__alarm_callback, alarm_name)
                elif unit == '小时':
                    job = schedule.every(int(value)).hour.do(self.__alarm_callback, alarm_name)
                elif unit == '天':
                    job = schedule.every().day.at(value).do(self.__alarm_callback, alarm_name)
                elif unit == '周一':
                    job = schedule.every().monday.at(value).do(self.__alarm_callback, alarm_name)
                elif unit == '周二':
                    job = schedule.every().tuesday.at(value).do(self.__alarm_callback, alarm_name)
                elif unit == '周三':
                    job = schedule.every().wednesday.at(value).do(self.__alarm_callback, alarm_name)
                elif unit == '周四':
                    job = schedule.every().thursday.at(value).do(self.__alarm_callback, alarm_name)
                elif unit == '周五':
                    job = schedule.every().friday.at(value).do(self.__alarm_callback, alarm_name)
                elif unit == '周六':
                    job = schedule.every().saturday.at(value).do(self.__alarm_callback, alarm_name)
                elif unit == '周日':
                    job = schedule.every().sunday.at(value).do(self.__alarm_callback, alarm_name)
                else:
                    return '出错: 非法的unit参数取值'
            except Exception:
                return '出错: 已提供的参数无法设置'
            # 添加
            print('添加闹钟:', alarm_name)
            self.__alarm_list[alarm_name] = [job, type, self.__id]
            retval = f'设置成功, 闹钟名字为: {alarm_name}、id为{self.__id}'
            self.__id += 1
            return retval
        elif arguments['op'] == 'rm':       # 删除指定闹钟
            alarm_name = arguments['name']
            if alarm_name not in self.__alarm_list:
                return '出错: 要删除的闹钟不存在'
            self.__alarm_del(alarm_name)
            return f'删除成功, 删除的闹钟名字为: {alarm_name}'
        elif arguments['op'] == 'list':     # 列出当前存在的闹钟
            retval = '当前正在运行的闹钟(名字列表):\n'
            for alarm_name, _ in self.__alarm_list.items():
                retval += f'{alarm_name}\n'
            # print(f'当前闹钟: \n{retval}')
            return retval

    def function_init(self, callback, args):
        self.__callback = callback
        self.__args = args
        self.__id = 0
        def run_scheduler(stop_event):
            print("闹钟调度线程启动")
            while not stop_event.is_set():
                schedule.run_pending()
                time.sleep(1)
            print("闹钟调度线程退出")
        self.__thread = threading.Thread(target=run_scheduler, args=(self.__stop_event,))
        self.__thread.start()

    def function_deinit(self):
        # 设置停止信号
        self.__stop_event.set()
        self.__thread.join()
        # 删掉所有
        for _, job in self.__alarm_list.items():
            schedule.cancel_job(job)
        self.__alarm_list.clear()
        self.__callback = None
        self.__args = None

    def __init__(self):
        self.__alarm_list = { }
        self.__callback = None
        self.__args = None
        self.__id = 0
        self.__stop_event = threading.Event()
        self.function_desc = {
            "desc": {
                "type": "function",  # 工具类型，目前主要是 "function"
                "function": {
                    "name": "alarm_clock",  # 函数名
                    "description": "闹钟功能, 设定的闹钟到期后会使用system消息注入, 只有单system消息注入了才能提示user闹钟到期",  # 功能描述
                    "parameters": {  # 参数定义，遵循 JSON Schema
                        "type": "object",
                        "properties": {
                            "op": {
                                "type": "string",
                                "description": "操作类型, add:添加一个闹钟; rm:删除一个闹钟; list:列出当前正在运行的闹钟",
                                "enum": ["add", "rm", "list"]
                            },
                            "type": {
                                "type": "string",
                                "description": "闹钟类型, 是响一次还是每次都响; 响一次的闹钟在到期后会自动删除;"
                                            "op为list和rm时, 这个参数应该设置为空",
                                "enum": ["每次", "一次", ""]
                            },
                            "unit": {
                                "type": "string",
                                "description": "时间单位;"
                                            "op为list和rm时, 这个参数应该设置为空",
                                "enum": ["秒", "分钟", "小时", "天", "周一", "周二", "周三", "周四", "周五", "周六", "周日", ""]
                            },
                            "value": {
                                "type": "string",
                                "description": "时间值;"
                                            "unit为 秒/分钟/小时 时, 这个值应该是个整数;"
                                            "除此之外这个值应该是个时间, 例如 12:30:01;"
                                            "op为list和rm时, 这个参数应该设置为空",
                            },
                            "name": {
                                "type": "string",
                                "description": "闹钟名字;"
                                            "仅当op为rm时需要这个参数, 其它的op取值都应该设置为空",
                            },
                        },
                        "required": ["op"]  # 指定必填参数
                    }
                }
            },
            "call": self.function_call,
            "init": self.function_init,
            "deinit": self.function_deinit
        }

def __test(f):
    # 添加闹钟
    f.function_call({'op': 'add', 'type': '每次', 'unit': '天', 'value': '12:30:00', 'name': ''})
    f.function_call({'op': 'add', 'type': '每次', 'unit': '秒', 'value': '10', 'name': ''})
    f.function_call({'op': 'add', 'type': '每次', 'unit': '周四', 'value': '12:30:00', 'name': ''})
    f.function_call({'op': 'add', 'type': '一次', 'unit': '天', 'value': '12:30:00', 'name': ''})
    f.function_call({'op': 'add', 'type': '一次', 'unit': '周五', 'value': '12:30:00', 'name': ''})
    # 列出闹钟
    f.function_call({'op': 'list', 'type': '', 'unit': '', 'value': '', 'name': ''})
    # 删除闹钟
    f.function_call({'op': 'rm', 'type': '', 'unit': '', 'value': '', 'name': '每天12:30:00响一次'})
    # 列出闹钟
    f.function_call({'op': 'list', 'type': '', 'unit': '', 'value': '', 'name': ''})

if __name__ == "__main__":
    f = function_alarm()
    f.function_init(lambda x,_: print(x), None)
    __test(f)
    time.sleep(22)
    f.function_deinit()
    time.sleep(1)
