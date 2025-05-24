"""
Start the Brush Up application in HTTP-only mode
Using Flask as a proxy server to avoid SSL issues
"""

import os
import sys
import subprocess
import time
import threading
import signal

def run_django():
    """Run Django in the background"""
    django_cmd = [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"]
    django_env = os.environ.copy()
    django_env["HTTPS"] = "off"
    django_env["HTTP_MODE"] = "true"
    
    print("\n=== Starting Django server on port 8000 ===\n")
    
    django_process = subprocess.Popen(
        django_cmd,
        env=django_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    # Print Django output
    def print_output():
        for line in django_process.stdout:
            print(line.decode('utf-8').strip())
    
    thread = threading.Thread(target=print_output)
    thread.daemon = True
    thread.start()
    
    # Give Django time to start
    time.sleep(3)
    
    return django_process

def run_flask_proxy():
    """Run Flask as a proxy to Django"""
    # Import Flask here to avoid issues with Django setup
    from flask import Flask, request, Response
    import requests
    
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return "OK"
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def proxy(path):
        target_url = f"http://localhost:8000/{path}"
        
        # Copy request headers but exclude Host
        headers = {key: value for (key, value) in request.headers if key != 'Host'}
        
        # Forward the request to Django
        try:
            resp = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request.get_data(),
                cookies=request.cookies,
                params=request.args,
                allow_redirects=False
            )
            
            # Create Flask response
            response = Response(resp.content, resp.status_code)
            
            # Copy response headers
            for key, value in resp.headers.items():
                if key.lower() not in ('content-length', 'connection', 'content-encoding'):
                    response.headers[key] = value
            
            return response
        except requests.exceptions.RequestException as e:
            return f"Error proxying to Django: {str(e)}", 500
    
    print("\n=== Starting Flask proxy on port 5000 ===\n")
    app.run(host='0.0.0.0', port=5000)

def signal_handler(sig, frame):
    """Handle termination signals"""
    print("\n=== Shutting down servers ===\n")
    sys.exit(0)

def main():
    """Main function to run both servers"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run Django in the background
    django_process = run_django()
    
    try:
        # Run Flask proxy in the foreground
        run_flask_proxy()
    except KeyboardInterrupt:
        print("\n=== Shutting down servers ===\n")
    finally:
        # Clean up Django process
        if django_process:
            django_process.terminate()
            django_process.wait()

if __name__ == "__main__":
    main()