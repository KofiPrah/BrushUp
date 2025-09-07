#!/usr/bin/env python
"""
Simple HTTP-only proxy that forwards requests to the Django application
"""
import flask
import requests
import subprocess
import time
import os

app = flask.Flask(__name__)
django_port = 8000
django_process = None

def start_django():
    global django_process
    if django_process is None or django_process.poll() is not None:
        print("Starting Django on port", django_port)
        cmd = ["python", "manage.py", "runserver", f"127.0.0.1:{django_port}"]
        django_process = subprocess.Popen(cmd)
        time.sleep(3)  # Give Django time to start
    return django_process

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    start_django()
    
    url = f"http://127.0.0.1:{django_port}/{path}"
    headers = {k: v for k, v in flask.request.headers.items() if k.lower() != 'host'}
    
    if flask.request.method == 'GET':
        resp = requests.get(url, headers=headers, params=flask.request.args)
    elif flask.request.method == 'POST':
        resp = requests.post(url, headers=headers, data=flask.request.get_data())
    elif flask.request.method == 'PUT':
        resp = requests.put(url, headers=headers, data=flask.request.get_data())
    elif flask.request.method == 'DELETE':
        resp = requests.delete(url, headers=headers)
    
    response = flask.Response(resp.content)
    for key, value in resp.headers.items():
        if key.lower() not in ('content-length', 'transfer-encoding', 'content-encoding'):
            response.headers[key] = value
    
    return response

if __name__ == '__main__':
    port = 8080
    print(f"Starting proxy server on port {port}")
    app.run(host='0.0.0.0', port=port)
