# -*- coding:utf-8 -*-

import os
import shutil
from pathlib import Path
import json

# 工作目录
workspace_dir = 'workspace'

# 检查工作目录
if not os.path.exists(workspace_dir):
    os.makedirs(workspace_dir, exist_ok=True)

class RestrictedPath:
    def __init__(self, root_path):
        self.root_path = Path(root_path).resolve()

    def __check_path(self, user_path):
        """检查路径是否在根目录下"""
        if user_path == '/':
            user_path = '.'
        full_path = (self.root_path / user_path).resolve()
        # 确保路径在根目录内
        if not str(full_path).startswith(str(self.root_path)):
            raise PermissionError(f"Access denied: {user_path} is outside root directory")
        return full_path

    def open(self, path, mode='r', encoding='utf-8'):
        """打开文件"""
        full_path = self.__check_path(path)
        return open(full_path, mode, encoding=encoding)

    def rm(self, path):
        """删除文件"""
        full_path = self.__check_path(path)
        os.remove(full_path)
        return not full_path.exists()

    def exists(self, path):
        """检查给出的路径是否存在，路径可以是目录或者文件"""
        full_path = self.__check_path(path)
        return full_path.exists()

    def listdir(self, path='.'):
        """递归列出指定目录下所有的文件和文件夹"""
        full_path = self.__check_path(path)
        result_list = [ ]
        for root, dirs, files in os.walk(full_path):
            # 去掉workspace往前的路径
            root = 'workspace_dir'.join(root.split(workspace_dir)[1:])
            if root.startswith('/') or root.startswith('\\'):
                root = root[1:]
            #
            for dir_name in dirs:
                result_list.append(["dir", os.path.join(root, dir_name).replace('\\', '/')])
            for file_name in files:
                result_list.append(["file", os.path.join(root, file_name).replace('\\', '/')])
        return result_list

    def mkdir(self, path):
        """创建目录，父目录如果不存在则会自动创建"""
        full_path = self.__check_path(path)
        os.makedirs(full_path, exist_ok=True)
        return full_path.exists()

    def rmdir(self, path):
        """递归删除目录及其所有内容"""
        full_path = self.__check_path(path)
        shutil.rmtree(full_path)
        return not full_path.exists()

class function_file:
    """提供存储功能，可以进行文件和目录的操作"""
    def exists(self, path):
        """
        检查给出的路径是否存在，路径可以是目录或者文件
        返回值: true为存在，false则不存在，其它值则表示出错内容
        """
        try:
            result = self.__restricted.exists(path)
            return 'true' if result else 'false'
        except Exception as e:
            return str(e)

    def listdir(self, path):
        """
        递归列出指定目录下所有的文件和文件夹
        返回值 json格式:
            msg: success表示成功，其它值则表示没有成功的原因
            data: list格式的数据；其中type表示文件类型，file为文件，dir为目录；path则表示路径
        """
        result_dict = {"msg": "success", "data": ""}
        try:
            l = self.__restricted.listdir(path)
            list_data = [ ]
            for type, path in l:
                list_data.append({"type": type, "path": path})
            result_dict["data"] = list_data
        except Exception as e:
            result_dict["msg"] = str(e)
        result_json_str = json.dumps(result_dict, indent=4, ensure_ascii=False)
        # print(result_json_str)
        return result_json_str

    def mkdir(self, path):
        """
        创建目录，父目录如果不存在则会自动创建
        返回值: true为创建成功，false则创建失败，其它值则表示出错内容
        """
        try:
            result = self.__restricted.mkdir(path)
            return 'true' if result else 'false'
        except Exception as e:
            return str(e)

    def rmdir(self, path):
        """
        递归删除目录及其所有内容
        返回值: true为删除成功，false则失败，其它值则表示出错内容
        """
        try:
            result = self.__restricted.rmdir(path)
            return 'true' if result else 'false'
        except Exception as e:
            return str(e)

    def write(self, path, data):
        """
        读取文件内容
        返回值: success表示成功，其它值则表示没有成功的原因
        """
        try:
            with self.__restricted.open(path, 'w', encoding='utf-8') as f:
                f.write(data)
            return 'success'
        except Exception as e:
            return str(e)

    def read(self, path):
        """
        读取文件内容
        返回值 json格式:
            msg: success表示成功，其它值则表示没有成功的原因
            data: 文件内容
        """
        result_dict = {"msg": "success", "data": ""}
        try:
            with self.__restricted.open(path, 'r', encoding='utf-8') as f:
                file_data = f.read()
                result_dict["data"] = file_data
        except Exception as e:
            result_dict["msg"] = str(e)
        result_json_str = json.dumps(result_dict, indent=4, ensure_ascii=False)
        # print(result_json_str)
        return result_json_str

    def rm(self, path):
        """
        删除指定文件
        返回值: true为删除成功，false则失败，其它值则表示出错内容
        """
        try:
            result = self.__restricted.rm(path)
            return 'true' if result else 'false'
        except Exception as e:
            return str(e)

    def function_call(self, arguments):
        """调用入口"""
        op = arguments["op"]
        path = arguments["path"]
        data = arguments["data"]
        if op == 'exists':
            return self.exists(path)
        elif op == 'listdir':
            return self.listdir(path)
        elif op == 'mkdir':
            return self.mkdir(path)
        elif op == 'rmdir':
            return self.rmdir(path)
        elif op == 'write':
            return self.write(path, data)
        elif op == 'read':
            return self.read(path)
        elif op == 'rm':
            return self.rm(path)
        else:
            return f'出错：不支持的操作 {op}'

    def __init__(self):
        self.__restricted = RestrictedPath(workspace_dir)

        func_list = [
            ['exists', function_file.exists.__doc__.strip()],
            ['listdir', function_file.listdir.__doc__.strip()],
            ['mkdir', function_file.mkdir.__doc__.strip()],
            ['rmdir', function_file.rmdir.__doc__.strip()],
            ['write', function_file.write.__doc__.strip()],
            ['read', function_file.read.__doc__.strip()],
            ['rm', function_file.rm.__doc__.strip()],
        ]
        desc = f'{function_file.__doc__.strip()}，包含了如下功能：\n'
        for n, d in func_list:
            desc += f'\n{n}: {d}\n'

        self.function_desc = {
            "desc": {
                "type": "function",  # 工具类型，目前主要是 "function"
                "function": {
                    "name": "file_dir_op",  # 函数名
                    "description": desc,  # 功能描述
                    "parameters": {  # 参数定义，遵循 JSON Schema
                        "type": "object",
                        "properties": {
                            "op": {
                                "type": "string",
                                "description": "操作类型",
                                "enum": [name for name,_ in func_list]
                            },
                            "path": {
                                "type": "string",
                                "description": "要操作的文件/目录的路径",
                            },
                            "data": {
                                "type": "string",
                                "description": "要写入的文件内容, 只有op为write时需要, 其它的操作这个参数留空",
                            },
                        },
                        "required": ["op", "path", "data"]  # 指定必填参数
                    }
                }
            },
            "call": self.function_call
        }

if __name__ == "__main__":
    restricted = RestrictedPath(workspace_dir)
    # 测试在目录下创建
    with restricted.open('test.txt', 'w') as f:
        f.write('this is test file')
    # 测试在非目录下创建
    try:
        with restricted.open('../outside.txt', 'w') as f:
            f.write('this is test file')
    except Exception as e:
        print(f'失败: {e}')
    print('文件存在:', restricted.exists('test.txt'))
    print('目录下内容:\n', restricted.listdir('.'))
    print('文件已删除:', restricted.rm('test.txt'))
    print('建立目录:', restricted.mkdir('test_dir/xxx'))
    print('目录已删除:', restricted.rmdir('test_dir'))

    ff = function_file()
    print('文件存在:', ff.exists('test.txt'))
    print('文件存在:', ff.exists('../test.txt'))
    print('建立目录:', ff.mkdir('test_dir/xxx'))
    print('建立目录:', ff.mkdir('test_dir/123'))
    print('文件存在:', ff.exists('test_dir/123'))
    print('目录下内容:', ff.listdir('.'))
    print('目录已删除:', ff.rmdir('test_dir'))
    print('写入文件:', ff.write('test.txt', 'This is test file!!'))
    print('读取文件:', ff.read('test.txt'))
    print('删除文件:', ff.rm('test.txt'))
