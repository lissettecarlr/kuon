# pip install python-dotenv
# pip install requests
# pip install flask

import os
import time
from threading import Thread
from flask import Flask, request, jsonify, Response, stream_with_context
import requests

app = Flask(__name__)


from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv('.env'))
# 新建.env文件，然后添加ACCESS_TOKEN=xxx  和 PUID=xxx

# https://chat.openai.com/api/auth/session 获得
access_token = os.environ.get('ACCESS_TOKEN')
# 付费用户cookie里面找
puid = os.environ.get('PUID')

def refresh_puid_cookie():
    global puid
    headers = {
        'Host': 'chat.openai.com',
        'origin': 'https://chat.openai.com/chat',
        'referer': 'https://chat.openai.com/chat',
        'sec-ch-ua': 'Chromium";v="110", "Not A(Brand";v="24", "Brave";v="110',
        'sec-ch-ua-platform': 'Linux',
        'content-type': 'application/json',
        'accept': 'text/event-stream',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Authorization': f'Bearer {access_token}',
    }
    url = 'https://chat.openai.com/backend-api/models'

    while True:
        resp = requests.get(url, headers=headers, cookies={'_puid': puid})
        if resp.status_code != 200:
            print(f"Error: {resp.status_code}")
            print(resp.text)
            break

        puid = resp.cookies.get('_puid')
        print(f"puid: {puid}")

        time.sleep(6 * 60 * 60)  # Sleep for 6 hours


if access_token and puid:
    Thread(target=refresh_puid_cookie).start()
else:
    print("Error: ACCESS_TOKEN and PUID are not set")


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'})


@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    url = f'https://chat.openai.com/backend-api/{path}'
    req_puid = request.headers.get('Puid', puid)

    headers = {
        'Host': 'chat.openai.com',
        'Origin': 'https://chat.openai.com/chat',
        'Content-Type': 'application/json',
        'Connection': 'keep-alive',
        'Keep-Alive': 'timeout=360',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Authorization': request.headers.get('Authorization', ''),
    }

    response = requests.request(
        request.method,
        url,
        headers=headers,
        cookies={'_puid': req_puid},
        data=request.get_data(),
        stream=True,
    )

    def generate():
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return Response(
        stream_with_context(generate()),
        content_type=response.headers.get('Content-Type', 'application/json'),
        status=response.status_code,
    )


if __name__ == '__main__':
    port = os.environ.get('PORT', 9999)
    app.run(host='0.0.0.0', port=port)