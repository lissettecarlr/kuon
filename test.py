import requests
import json

url = 'http://localhost:5000/chat'  # 这里的 URL 需要替换为你自己的对话服务 URL

# 准备请求数据，这里的 message 字段值可以根据实际需要修改
data = {
    'message': '你好'
}

# 将请求数据转换为 JSON 格式
json_data = json.dumps(data)

# 设置请求头信息
headers = {'Content-Type': 'application/json'}

# 发送 POST 请求，并获取返回结果
response = requests.post(url, data=json_data, headers=headers)

# 解析返回的结果，并输出回复消息
result = json.loads(response.text)
print(result['message'])