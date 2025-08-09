#!/usr/bin/env python3
"""
ASGI server startup script with WebSocket support for Django Channels.
This provides real-time notifications via WebSockets.
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artcritique.settings')
django.setup()

def start_asgi_server():
    """Start ASGI server with WebSocket support."""
    from django.conf import settings
    
    # Temporarily enable ASGI for this session
    settings.ASGI_APPLICATION = 'artcritique.asgi.application'
    
    # Import uvicorn for ASGI server
    import uvicorn
    from artcritique.asgi import application
    
    print("🚀 Starting Brush Up with WebSocket support...")
    print("📡 Real-time notifications enabled")
    print("🌐 Server running at: http://0.0.0.0:5000")
    print("⚡ WebSocket endpoint: ws://0.0.0.0:5000/ws/notifications/")
    print("\n" + "="*50)
    
    # Start ASGI server
    uvicorn.run(
        application,
        host='0.0.0.0',
        port=5000,
        log_level='info',
        access_log=True,
        reload=False,
        workers=1
    )

if __name__ == '__main__':
    try:
        start_asgi_server()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("💡 Installing uvicorn...")
        os.system("pip install uvicorn")
        print("✅ Please restart the server")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)