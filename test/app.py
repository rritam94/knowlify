from flask import Flask
import requests

app = Flask(__name__)

def check_internet():
    try:
        response = requests.get("https://www.cloudflare.com", timeout=30)
        return response.status_code == 200
    
    except requests.ConnectionError:
        return False

print("Internet connected" if check_internet() else "No internet connection")