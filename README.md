# cicada.ai
知了·AI

## 环境
* 安装依赖: `pip install -r requirements.txt`

## 运行
* 不带热重载: `chainlit run cicada.ai.py`
* 带热重载(用于调试): `chainlit run -w cicada.ai.py`
* 指定端口: `chainlit run cicada.ai.py --port 8080`
* 监听所有网络: `chainlit run cicada.ai.py --host 0.0.0.0 --port 8080`
* 带密码验证的:
  ```
  chainlit create-secret # 生成秘钥
  CHAINLIT_AUTH_SECRET="刚生成的秘钥" APP_USERNAME="自定义账户名" APP_PASSWORD="账户密码" chainlit run cicada.ai.py --host 0.0.0.0 --port 7612
  ```
