import os
from flask import Flask, jsonify, redirect

app = Flask(__name__)

@app.route('/')
def index():
    """Redirect to the Django app"""
    return redirect('https://0.0.0.0:5000/')

@app.route('/api/health/')
def health():
    """Health check endpoint to verify the service is running"""
    return jsonify({
        "status": "healthy",
        "message": "Proxy server is running",
        "backend": "https://0.0.0.0:5000/api/health/"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
