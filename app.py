# app.py
from flask import Flask, request, render_template
import requests
import json
import os
from device_detector import DeviceDetector

app = Flask(__name__)

LOG_FILE = 'data/user_detail.log'
os.makedirs('data', exist_ok=True)

def log_to_file(data):
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(data, indent=2) + '\n')

def get_ip_apis(ip):
    results = {}
    try:
        results['ipinfo'] = requests.get(f"https://api.ipinfo.io/lite/{ip}?token=bc9a896675dded").json()
    except Exception as e:
        results['ipinfo'] = {'error': str(e)}

    try:
        results['ipapi'] = requests.get(f"https://ipapi.co/{ip}/json/").json()
    except Exception as e:
        results['ipapi'] = {'error': str(e)}

    try:
        results['ipstack'] = requests.get(f"http://api.ipstack.com/{ip}?access_key=8d18ab708969919166f33e19a4b06558").json()
    except Exception as e:
        results['ipstack'] = {'error': str(e)}

    try:
        results['ipify_country'] = requests.get(
            f"https://geo.ipify.org/api/v2/country?apiKey=at_H8GnB6swz45u8dwvnLNlV8H6pLDYl&ipAddress={ip}"
        ).json()
    except Exception as e:
        results['ipify_country'] = {'error': str(e)}

    try:
        results['ipify_full'] = requests.get(
            f"https://geo.ipify.org/api/v2/country,city,vpn?apiKey=at_H8GnB6swz45u8dwvnLNlV8H6pLDYl&ipAddress={ip}"
        ).json()
    except Exception as e:
        results['ipify_full'] = {'error': str(e)}

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log_info', methods=['POST'])
def log_info():
    user_data = request.get_json()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # Get all IP info
    ip_data = get_ip_apis(ip)

    # Parse User-Agent
    user_agent = request.headers.get('User-Agent')
    device_info = DeviceDetector(user_agent).parse()

    log_data = {
        'ip_address': ip,
        'location_apis': ip_data,
        'device_info': {
            'device_type': device_info.device_type(),
            'os_name': device_info.os_name(),
            'os_version': device_info.os_version(),
            'client_name': device_info.client_name(),
            'client_type': device_info.client_type(),
            'client_version': device_info.client_version()
        },
        'browser_data': user_data
    }

    log_to_file(log_data)
    return {'status': 'logged'}

if __name__ == '__main__':
    app.run(debug=True)
