# -*- coding:utf-8 -*-

import chainlit as cl
from openai import AsyncOpenAI
import json

llm_cfg_file = 'llm_cfg.json'
llm_cfg_value = None
llm_client = None

# 配置项检查
def item_check(json_data):
    if 'api_key' in json_data and 'base_url' in json_data and 'model' in json_data:
        return True
    return False

# 配置文件检查
def cfg_check_and_set():
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

# 配置
async def cfg_main(message):
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

# 聊天
async def chat_main(message):
    global llm_client
    if llm_client is None:
        # 初始化客户端 (指向本地 vLLM 服务或 OpenAI)
        llm_client = AsyncOpenAI(
            api_key = llm_cfg_value['api_key'],
            base_url = llm_cfg_value['base_url']
        )

    # 创建一个空的 Chainlit 消息对象
    msg = cl.Message(content='')
    await msg.send()

    # 调用 LLM
    stream = await llm_client.chat.completions.create(
        model = llm_cfg_value['model'], # 模型名称
        messages=[{'role': 'user', 'content': message.content}],
        stream=True  # 开启流式模式
    )

    # 循环接收数据块并实时推送到前端
    async for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            # 使用 stream_token 将文字流式输出到界面上
            await msg.stream_token(token)

    # 更新最终消息状态
    await msg.update()

@cl.on_chat_start
async def on_start():
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
            author='system',
        ).send()

    # 可以发送元素，比如图片
    # await cl.Image(path='welcome.png', name='welcome').send()

@cl.on_message
async def on_chat(message: cl.Message):
    if llm_cfg_value is None:
        await cfg_main(message)
    else:
        await chat_main(message)
