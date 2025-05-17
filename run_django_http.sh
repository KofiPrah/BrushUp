#!/bin/bash
export SSL_ENABLED=false
export HTTP_ONLY=true
exec python -c "
import os
os.environ[\"SSL_ENABLED\"] = \"false\"
os.environ[\"HTTP_ONLY\"] = \"true\"
from artcritique.wsgi import application
import gunicorn.app.base

class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

options = {
    \"bind\": \"0.0.0.0:5000\",
    \"workers\": 1,
    \"reload\": True
}

StandaloneApplication(application, options).run()
"
