# -*- coding:utf-8 -*-

import threading
# pip install schedule
import schedule as sd # schedule是模块级别的单一实例
import time
import json

thread = None
thread_name = 'alarm_schedule_thread'
# 创建模块级单一调度线程
for t in threading.enumerate():
    if t.name == thread_name:
        thread = t
        print('闹钟调度线程已存在')

if thread is None:
    def run_sdr():
        print("闹钟调度线程启动")
        while True:
            time.sleep(1)
            thread.lock.acquire()
            sd.run_pending()
            thread.lock.release()
        # print("闹钟调度线程退出")
    print('创建闹钟调度线程')
    t = threading.Thread(target=run_sdr, name=thread_name)
    t.lock = threading.Lock() # 创建锁
    t.start()
    thread = t

class function_alarm:
    """
    闹钟功能, 设定的闹钟到期后会使用system消息注入, 只有当system消息注入了才能提示user闹钟到期
    """
    def __is_my_job(self, job):
        # 检查是不是自己的job
        instance = job.job_func.args[4]
        return self == instance

    def __get_job(self, name):
        alarm_job = None
        # 查找job
        for job in sd.get_jobs():
            if job.job_func.args[0] == name and self.__is_my_job(job):
                alarm_job = job
                break
        return alarm_job

    def __get_desc_by_args(self, name, id, note):
        """
        返回值 json数据:
            name: 闹钟名字
            id: 闹钟的编号
            note: 闹钟的备注
        """
        data_dict = {'name': name, 'id': id, 'note': note}
        json_str = json.dumps(data_dict, indent=4, ensure_ascii=False)
        return json_str

    def __get_desc_by_job(self, job):
        name = job.job_func.args[0]
        id = job.job_func.args[1]
        note = job.job_func.args[2]
        return self.__get_desc_by_args(name, id, note)

    def list(self):
        """
        列出当前所有有效的闹钟
        返回值 json数据, list中每一项中的属性:
            name: 闹钟名字
            id: 闹钟的编号
            note: 闹钟的备注
        """
        data_list = []
        thread.lock.acquire()
        for job in sd.get_jobs():
            if not self.__is_my_job(job):
                continue
            name = job.job_func.args[0]
            id = job.job_func.args[1]
            note = job.job_func.args[2]
            data_list.append({'name': name, 'id': id, 'note': note})
        thread.lock.release()
        json_str = json.dumps(data_list, indent=4, ensure_ascii=False)
        return json_str

    def __rm_by_job(self, job):
        name = job.job_func.args[0]
        print(f'删除闹钟：{name} | {self}')
        sd.cancel_job(job)
        return 'success'

    def __rm_by_name(self, name):
        alarm_job = self.__get_job(name)
        if alarm_job is None:
            return '出错: 要删除的闹钟不存在'
        return self.__rm_by_job(alarm_job)

    def rm(self, name):
        """
        删除已存在的闹钟
        返回值: success表示成功，其它值则表示没有成功的原因
        """
        thread.lock.acquire()
        retval = self.__rm_by_name(name)
        thread.lock.release()
        return retval

    def __alarm_callback(self, name, id, note, once, instance):
        """
        这个函数是在锁里面调用的
        """
        if self.__callback:
             self.__callback(f"闹钟到期了：\n{self.__get_desc_by_args(name, id, note)}\n"
                              "请仔细检查闹钟name和id, 确保和设置的闹钟匹配, 之后根据note提示user或者调用tool",
                              self.__args)
        # 如果只要响则关掉
        if once:
            print(f'删除一次性闹钟： {name}, 结果：', self.__rm_by_name(name))

    def add(self, type, unit, value, note):
        """
        添加一个闹钟
        返回值: 返回闹钟信息表示成功，其它值则表示没有成功的原因
        """
        if unit in '秒/分钟/小时':
            alarm_name = f'{value}{unit}'
        elif unit in '天/周一/周二/周三/周四/周五/周六/周日':
            alarm_name = f'{unit}{value}'
        else:
            return '出错: 非法的unit参数取值'
        if type == '每次':
            alarm_name = f'每{alarm_name}响一次'
            once = False
        elif type == '一次':
            if unit in '秒/分钟/小时':
                alarm_name = f'{alarm_name}后响一次'
            elif unit == '天':
                alarm_name = f'今{alarm_name}响一次'
            else:
                alarm_name = f'这{alarm_name}响一次'
            once = True
        else:
            return '出错: 非法的type参数取值'
        def __sd_do(f):
            return f.do(self.__alarm_callback, alarm_name, self.__id, note, once, self)
        # 设置
        try:
            if unit == '秒':
                thread.lock.acquire()
                job = __sd_do(sd.every(int(value)).seconds)
                thread.lock.release()
            elif unit == '分钟':
                thread.lock.acquire()
                job = __sd_do(sd.every(int(value)).minutes)
                thread.lock.release()
            elif unit == '小时':
                thread.lock.acquire()
                job = __sd_do(sd.every(int(value)).hour)
                thread.lock.release()
            elif unit == '天':
                thread.lock.acquire()
                job = __sd_do(sd.every().day.at(value))
                thread.lock.release()
            elif unit == '周一':
                thread.lock.acquire()
                job = __sd_do(sd.every().monday.at(value))
                thread.lock.release()
            elif unit == '周二':
                thread.lock.acquire()
                job = __sd_do(sd.every().tuesday.at(value))
                thread.lock.release()
            elif unit == '周三':
                thread.lock.acquire()
                job = __sd_do(sd.every().wednesday.at(value))
                thread.lock.release()
            elif unit == '周四':
                thread.lock.acquire()
                job = __sd_do(sd.every().thursday.at(value))
                thread.lock.release()
            elif unit == '周五':
                thread.lock.acquire()
                job = __sd_do(sd.every().friday.at(value))
                thread.lock.release()
            elif unit == '周六':
                thread.lock.acquire()
                job = __sd_do(sd.every().saturday.at(value))
                thread.lock.release()
            elif unit == '周日':
                thread.lock.acquire()
                job = __sd_do(sd.every().sunday.at(value))
                thread.lock.release()
            else:
                return '出错: 非法的unit参数取值'
        except Exception:
            return '出错: 已提供的参数无法设置'
        # 添加
        print(f'添加闹钟: {alarm_name}, id:{self.__id}, 备注: {note} | {self}')
        retval = f'添加成功，闹钟信息： \n{self.__get_desc_by_args(alarm_name, self.__id, note)}'
        self.__id += 1
        return retval

    def function_call(self, arguments):
        op = arguments['op']
        type = arguments['add_type'] # 每次/一次
        unit = arguments['add_unit'] # 秒/分钟/小时/天/周一/周二/周三/周四/周五/周六/周日
        value = arguments['add_value']
        note = arguments['add_note']
        name = arguments['rm_name']
        # 操作
        if arguments['op'] == 'add':        # 添加一个闹钟
            return self.add(type, unit, value, note)
        elif arguments['op'] == 'rm':       # 删除指定闹钟
            return self.rm(name)
        elif arguments['op'] == 'list':     # 列出当前存在的闹钟
            return self.list()

    def function_init(self, callback, args):
        self.__callback = callback
        self.__args = args
        self.__id = 0

    def function_deinit(self):
        # 删掉所有
        thread.lock.acquire()
        for job in sd.get_jobs():
            if not self.__is_my_job(job):
                continue
            self.__rm_by_job(job)
        thread.lock.release()
        self.__callback = None
        self.__args = None

    def __init__(self):
        self.__callback = None
        self.__args = None
        self.__id = 0

        desc = f"""
        {function_alarm.__doc__.strip()}
        op包括有以下操作：

        add: {function_alarm.add.__doc__.strip()}

        rm: {function_alarm.rm.__doc__.strip()}

        list: {function_alarm.list.__doc__.strip()}
        """

        self.function_desc = {
            "desc": {
                "type": "function",  # 工具类型，目前主要是 "function"
                "function": {
                    "name": "alarm_clock",  # 函数名
                    "description": desc,    # 功能描述
                    "parameters": {  # 参数定义，遵循 JSON Schema
                        "type": "object",
                        "properties": {
                            "op": {
                                "type": "string",
                                "description": "操作类型",
                                "enum": ["add", "rm", "list"]
                            },
                            "add_type": {
                                "type": "string",
                                "description": "闹钟类型, 是响一次还是每次都响; 响一次的闹钟在到期后会自动删除;"
                                               "仅当op为add时需要这个参数, 其它的op时都应该置空",
                                "enum": ["每次", "一次"]
                            },
                            "add_unit": {
                                "type": "string",
                                "description": "时间单位; 仅当op为add时需要这个参数, 其它的op时都应该置空",
                                "enum": ["秒", "分钟", "小时", "天", "周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                            },
                            "add_value": {
                                "type": "string",
                                "description": "时间值;"
                                               "unit为 秒/分钟/小时 时, 这个值应该是个整数;"
                                               "除此之外这个值应该是个时间, 例如 12:30:01;"
                                               "仅当op为add时需要这个参数, 其它的op时都应该置空",
                            },
                            "add_note": {
                                "type": "string",
                                "description": "闹钟备注，记录闹钟到期后要作的事情;"
                                               "仅当op为add时需要这个参数, 其它的op时都应该置空",
                            },
                            "rm_name": {
                                "type": "string",
                                "description": "需要删除的闹钟名字;"
                                               "仅当op为rm时需要这个参数, 其它的op时都应该置空",
                            },
                        },
                        "required": ["op", "add_type", "add_unit", "add_value", "add_note", "rm_name"]  # 指定必填参数
                    }
                }
            },
            "call": self.function_call,
            "init": self.function_init,
            "deinit": self.function_deinit
        }

def __test(f):
    # 添加闹钟
    f.function_call({'op': 'add', 'add_type': '每次', 'add_unit': '天', 'add_value': '12:30:00', 'add_note': 'test', 'rm_name': ''})
    f.function_call({'op': 'add', 'add_type': '每次', 'add_unit': '秒', 'add_value': '10', 'add_note': 'test', 'rm_name': ''})
    f.function_call({'op': 'add', 'add_type': '一次', 'add_unit': '秒', 'add_value': '15', 'add_note': 'test', 'rm_name': ''})
    f.function_call({'op': 'add', 'add_type': '每次', 'add_unit': '周四', 'add_value': '12:30:00', 'add_note': 'test', 'rm_name': ''})
    f.function_call({'op': 'add', 'add_type': '一次', 'add_unit': '天', 'add_value': '12:30:00', 'add_note': 'test', 'rm_name': ''})
    f.function_call({'op': 'add', 'add_type': '一次', 'add_unit': '周五', 'add_value': '12:30:00', 'add_note': 'test', 'rm_name': ''})
    # 列出闹钟
    f.function_call({'op': 'list', 'add_type': '', 'add_unit': '', 'add_value': '', 'add_note': '', 'rm_name': ''})
    # 删除闹钟
    f.function_call({'op': 'rm', 'add_type': '', 'add_unit': '', 'add_value': '', 'add_note': '', 'rm_name': '每天12:30:00响一次'})
    # 列出闹钟
    f.function_call({'op': 'list', 'add_type': '', 'add_unit': '', 'add_value': '', 'add_note': '', 'rm_name': ''})

if __name__ == "__main__":
    f = function_alarm()
    f.function_init(lambda x,_: print(x), None)
    __test(f)
    print(json.dumps(f.function_desc["desc"], indent=4, ensure_ascii=False))
    time.sleep(60)
    f.function_deinit()
    time.sleep(1)
