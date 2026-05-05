# -*- coding:utf-8 -*-

import json
import fcntl

memory_file = 'memory.json'

class function_memory:
    """
    这是一个记忆工具，可以用于保存长期记忆
    """

    def all(self):
        """
        读取所有的记忆
        返回值: 返回json格式数据，每一项中都包含俩个属性
               value: 这个是记忆内容，是你回答问题时需要关注的
               type: 这个是记忆的属性，进行记忆操作时需要关注，取值有 可修改/不可修改/可删除/不可删除
        """
        with open(memory_file, 'r', encoding='utf-8') as f:
            return f.read()

    def remember(self, name, value, type):
        """
        添加记忆或者修正已有的记忆
        返回值: success表示成功，其它值则表示没有成功的原因
        """
        with open(memory_file, 'r+', encoding='utf-8') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            # 先读出来
            memory = json.loads(f.read())
            # 检测属性
            if name in memory and '不可修改' in memory[name]['type']:
                raise Exception(f'不可修改的记忆: {name}')
            memory[name] = {'value': value, 'type': type}
            f.seek(0)        # 将指针移到文件开头
            f.truncate()     # 清空所有内容
            # 重新写入
            f.write(json.dumps(memory, indent=4, ensure_ascii=False))
            fcntl.flock(f, fcntl.LOCK_UN)
        return 'success'

    def forget(self, name):
        """
        遗忘指定的记忆
        返回值: success表示成功，其它值则表示没有成功的原因
        """
        with open(memory_file, 'r+', encoding='utf-8') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            # 先读出来
            memory = json.loads(f.read())
            # 检测属性
            if name not in memory:
                raise Exception(f'不存在的记忆: {name}')
            if '不可删除' in memory[name]['type']:
                raise Exception(f'{name} 是无法删除的记忆')
            del memory[name]
            f.seek(0)        # 将指针移到文件开头
            f.truncate()     # 清空所有内容
            # 重新写入
            f.write(json.dumps(memory, indent=4, ensure_ascii=False))
            fcntl.flock(f, fcntl.LOCK_UN)
        return 'success'

    def function_call(self, arguments):
        try:
            op = arguments['op']
            # 调用
            if op == 'all':
                return self.all()
            elif op == 'remember':
                name = arguments['name']
                value = arguments['value']
                type = arguments['type']
                return self.remember(name, value, type)
            elif op == 'forget':
                name = arguments['name']
                return self.forget(name)
            else:
                return f'非法的op: {op}'
        except Exception as e:
            return str(e)

    def __init__(self):
        desc = f"""
        {function_memory.__doc__.strip()}
        op包括有以下操作：

        all: {function_memory.all.__doc__.strip()}

        remember: {function_memory.remember.__doc__.strip()}

        forget: {function_memory.forget.__doc__.strip()}
        """

        self.function_desc = {
            "desc": {
                "type": "function",  # 工具类型，目前主要是 "function"
                "function": {
                    "name": "memory_op",  # 函数名
                    "description": desc.strip(),  # 功能描述
                    "parameters": {  # 参数定义，遵循 JSON Schema
                        "type": "object",
                        "properties": {
                            "op": {
                                "type": "string",
                                "description": "要执行的记忆操作",
                                "enum": ["all", "remember", "forget"]
                            },
                            "name": {
                                "type": "string",
                                "description": "记忆的名字，全局唯一;"
                                               "仅op为remember/forget需要这个参数，其他操作这个参数应该留空"
                            },
                            "value": {
                                "type": "string",
                                "description": "要记住的内容;"
                                               "仅op为remember需要这个参数，其他操作这个参数应该留空"
                            },
                            "type": {
                                "type": "string",
                                "description": "remember操作时可用的值为: 可修改/不可修改/可删除;"
                                               "多个值中间用'/'符号隔开;"
                                               "仅op为remember需要这个参数，其他操作这个参数应该留空"
                            },
                        },
                        "required": ["op", "name", "value", "type"]  # 指定必填参数
                    }
                }
            },
            "call": self.function_call
        }

if __name__ == "__main__":
    mem = function_memory()

    print(mem.remember('姓名', 'XXX', '可修改/不可删除'))
    # print(mem.all())
    try:
        print(mem.forget('姓名'))
    except Exception as e:
        print(e)
    print(mem.remember('姓名', 'XXX', '可修改/可删除'))
    try:
        print(mem.forget('姓名'))
    except Exception as e:
        print(e)
    # print(mem.all())

    print(mem.remember('姓名', 'XXX', '不可修改/可删除'))
    # print(mem.all())
    try:
        print(mem.remember('姓名', 'XXXDDD', '可修改/可删除'))
    except Exception as e:
        print(e)
    try:
        print(mem.forget('姓名'))
    except Exception as e:
        print(e)
    # print(mem.all())

    print(json.dumps(mem.function_desc["desc"], indent=4, ensure_ascii=False))

