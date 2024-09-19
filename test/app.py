from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from openai import OpenAI
import eventlet
import os

app = Flask(__name__)
CORS(app, origins='http://knowlify-frontend-production.up.railway.app')
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="http://knowlify-frontend-production.up.railway.app")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
eventlet.monkey_patch()

def gpt():
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "What is 5 + 5"}
        ],
        max_tokens = 16000,
        stream=True,
        temperature=1,
        top_p=1,
        frequency_penalty = 0,
        presence_penalty = 0,
    )

    total_content = ''

    for chunk in completion:
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content

            total_content += content

    return total_content

import requests

def check_internet():
    try:
        response = requests.get("https://www.cloudflare.com", timeout=30)
        return response.status_code == 200
    
    except requests.ConnectionError:
        return False

print("Internet connected" if check_internet() else "No internet connection")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)