[首页](../README.md) |
# 代理部署

由于openai的api接口被墙，所以需要中间商进行转发，中间商要求既能与openai通信也能与我们通信。我们对openai发送的请求将由它代为传达。由于是转述，所以可能存在安全问题的，如果使用了不明代理，有容易信息泄露风险。自己搭建是最好的解决方式

## API方案的代理

Ice-Hazymoon开源的方案，使用[openai-scf-proxy](https://github.com/Ice-Hazymoon/openai-scf-proxy)。这个方案是使用腾讯云的云函数，可以白嫖一段时间，收费其实也不贵。由于是开源，源码可见，也知道做了啥，仓库里有详细的部署教程，一两分钟就能搞定。

获取到地址后可以在openAiConfig.json里面填充proxy，例如
```
"proxy": "https://service-xxxxxx-xxxxxxx.jp.apigw.tencentcs.com"
```

## web方案的代理

代码位于utils/chatgpt_proxy.py，使用flask框架。基于[这个仓库](https://github.com/acheong08/ChatGPT-Proxy-V4/issues?q=is%3Aissue+is%3Aclosed)改写的python版本，源于是更适合服务器部署的go。

* 添加配置文件.env，里面填入ACCESS_TOKEN=xxx和PUID=XXX，前者自己打开[这里](https://chat.openai.com/api/auth/session)，后者在浏览器的cookies里找到puid的值，这个只能plus用户才看得到

* 运行python chatgpt_proxy.py，得到代理地址

例如:
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:9999
 * Running on http://192.168.2.137:9999
```
