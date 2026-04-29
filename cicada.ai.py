# -*- coding:utf-8 -*-

import chainlit as cl
from openai import AsyncOpenAI
import json
import tools.functions

llm_cfg_file = 'llm_cfg.json'
llm_cfg_value = None
llm_client = None

def item_check(json_data):
    """
    配置项检查
    """
    if 'api_key' in json_data and 'base_url' in json_data and 'model' in json_data:
        return True
    return False

def cfg_check_and_set():
    """
    配置文件检查
    """
    global llm_cfg_value
    # 读取配置
    try:
        with open(llm_cfg_file, 'r', encoding='utf-8') as f:
            raw_data = f.read()
            json_data = json.loads(raw_data)
            # print(json.dumps(json_data, indent=4, ensure_ascii=False))
            ret = item_check(json_data)
            if ret:
                llm_cfg_value = json_data
            return ret
    except Exception as e:
        # print(e)
        return False

async def cfg_main(message):
    """
    模型配置
    """
    global llm_cfg_value
    cfg_dict = { }
    author = 'config'
    # print(message.content)

    # 解析字段
    cfg_data = message.content.replace(' ', '').replace('：', ':').replace('\r', '')
    for line in cfg_data.split('\n'):
        kv = line.strip().split(':')
        if len(kv) < 2:
            continue
        k = kv[0]
        v = ':'.join(kv[1:])
        cfg_dict[k] = v

    # 转成json
    json_str = json.dumps(cfg_dict, ensure_ascii=False)
    if item_check(json_str):
        try:
            # 保存配置
            with open(llm_cfg_file, 'w', encoding='utf-8') as f:
                f.write(json_str)
            llm_cfg_value = json.loads(json_str)
            await cl.Message(
                content='配置成功，现在你可以开始和我聊天啦！\n',
                author=author,
            ).send()
        except Exception as e:
            await cl.Message(
                content=f'配置失败: {e}\n',
                author=author,
            ).send()
    else:
        await cl.Message(
            content=f'配置失败: 格式或配置不完整，请重新输入\n',
            author=author,
        ).send()

@cl.step(type='tool', name='工具箱')
async def call_function(func, arguments):
    return tools.functions.call_function(func, arguments)

async def chat_main(message):
    """
    对话聊天
    """
    global llm_client
    if llm_client is None:
        # 初始化客户端 (指向本地 vLLM 服务或 OpenAI)
        llm_client = AsyncOpenAI(
            api_key = llm_cfg_value['api_key'],
            base_url = llm_cfg_value['base_url']
        )

    # 创建一个空的 Chainlit 消息对象
    msg = cl.Message(content='', author='assistant')
    await msg.send()

    # 从会话中获取历史消息
    message_history = cl.user_session.get('message_history')

    # 将用户的新消息加入历史
    if message is not None:
        message_history.append({'role': 'user', 'content': message.content})

    # print(message_history)

    # 调用 LLM
    stream = await llm_client.chat.completions.create(
        model = llm_cfg_value['model'],             # 模型名称
        messages = message_history,                 # 传入历史消息
        tools = tools.functions.get_function_desc(),# 将定义好的工具列表传进去
        tool_choice = 'auto',                       # 让模型自动判断是否需要调用工具
        # max_tokens = 64000,
        stream = True                               # 开启流式模式
    )

    tool_call = False
    # 循环接收数据块并实时推送到前端
    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:       # 提取增量内容
            # 使用 stream_token 将文字流式输出到界面上
            await msg.stream_token(delta.content)
        elif delta.tool_calls:  # 提取工具内容
            print('工具调用:', delta.tool_calls, flush=True)
            tool_call_id = delta.tool_calls[0].id
            function_name = delta.tool_calls[0].function.name
            arguments = delta.tool_calls[0].function.arguments
            # print(tool_call_id, function_name, arguments)
            # 过滤掉异常的工具调用
            if tool_call_id is not None and function_name is not None and arguments is not None:
                # 把发起的动作插入到上下文中
                message_history.append({"role": "assistant", "content": None, "tool_calls": delta.tool_calls})
                cl.user_session.set('message_history', message_history)
                # 调用工具
                result = await call_function(function_name, arguments)
                # 把调用工具的结果加入上下文
                message_history.append({"role": "tool", "tool_call_id": tool_call_id, "name": function_name, "content": result})
                cl.user_session.set('message_history', message_history)
                # print(message_history)
            tool_call = True

    # 更新最终消息状态
    await msg.update()

    # 如果不是工具调用
    if not tool_call:
        # 将 AI 的完整回复加入历史
        message_history.append({'role': 'assistant', 'content': msg.content})
        # 更新会话中的历史列表
        cl.user_session.set('message_history', message_history)
        # print(json.dumps(message_history, indent=4, ensure_ascii=False))

    return tool_call

@cl.on_chat_start
async def on_start():
    # 预设一个 system 角色来定义 AI 的行为
    cl.user_session.set('message_history', [
        {'role': 'system', 'content': '你的名字叫知了·AI，你是一个乐于助人的AI助手。'}
    ])

    # 主动发送欢迎消息
    await cl.Message(
        content='👋 你好！我是 知了·AI。\n\n我可以帮你写代码、回答问题。',
        author='system', # 可以自定义发送者名字
    ).send()

    # 如果配置文件没有载入, 则告知需要配置
    if not cfg_check_and_set():
        await cl.Message(
            content='未找到LLM配置文件，请按如下格式发送给我进行配置:\n'
                    '```\n'
                    'base_url:\n'
                    'api_key:\n'
                    'model:\n'
                    '```\n\n'
                    '例如，你可以给我发送如下内容进行配置:\n'
                    '```\n'
                    'base_url: https://api.deepseek.com/v1\n'
                    'api_key: xxxxxxx\n'
                    'model: DeepSeek-V3-2\n'
                    '```',
            author='config',
        ).send()

    # 可以发送元素，比如图片
    # await cl.Image(path='welcome.png', name='welcome').send()

@cl.on_message
async def on_chat(message: cl.Message):
    if llm_cfg_value is None:
        await cfg_main(message)
    else:
        recall = await chat_main(message)
        # 如果上一轮调用了工具, 那就还需要推理一次让模型输出结果
        if recall:
            await chat_main(None)
