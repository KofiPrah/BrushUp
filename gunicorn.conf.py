"""
Production Gunicorn configuration for Brush Up deployment
Optimized for Replit Autoscale with memory and timeout management
"""

import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
backlog = 2048

# Worker processes
workers = 1  # Reduced to prevent memory issues on autoscale
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Increased timeout for startup
keepalive = 2

# Restart workers after this many requests, to help control memory usage
max_requests = 1000
max_requests_jitter = 100

# Preload application for better memory usage
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "brushup"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (disabled for Replit)
keyfile = None
certfile = None

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)