#!/usr/bin/env python
"""
A simple script to directly render a Google OAuth login page
for debugging styling issues.
"""

import os
from flask import Flask, render_template_string

app = Flask(__name__)

# Our HTML template with styling
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign In Via Google - Art Critique</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Art Critique</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/artworks/">Artworks</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/accounts/login/">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/accounts/signup/">Sign Up</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="py-4">
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-5">
                    <div class="text-center mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" class="bi bi-google text-primary mb-3" viewBox="0 0 16 16">
                            <path d="M15.545 6.558a9.42 9.42 0 0 1 .139 1.626c0 2.434-.87 4.492-2.384 5.885h.002C11.978 15.292 10.158 16 8 16A8 8 0 1 1 8 0a7.689 7.689 0 0 1 5.352 2.082l-2.284 2.284A4.347 4.347 0 0 0 8 3.166c-2.087 0-3.86 1.408-4.492 3.304a4.792 4.792 0 0 0 0 3.063h.003c.635 1.893 2.405 3.301 4.492 3.301 1.078 0 2.004-.276 2.722-.764h-.003a3.702 3.702 0 0 0 1.599-2.431H8v-3.08h7.545z"/>
                        </svg>
                        <h1 class="display-6 fw-bold">Sign In Via Google</h1>
                        <p class="text-muted">You are about to sign in using a third-party account from Google.</p>
                    </div>
                    
                    <div class="card border-0 shadow rounded-4">
                        <div class="card-body p-4 p-md-5">
                            <form method="post">
                                <input type="hidden" name="csrfmiddlewaretoken" value="demo-csrf-token">
                                <div class="d-grid">
                                    <button type="submit" class="btn btn-primary btn-lg">Continue with Google</button>
                                </div>
                            </form>
                        </div>
                    </div>
                    
                    <div class="text-center mt-4">
                        <p class="mb-1">Have a username and password? <a href="/accounts/login/" class="text-primary fw-bold text-decoration-none">Sign In</a></p>
                        <p class="mb-0">Need an account? <a href="/accounts/signup/" class="text-primary fw-bold text-decoration-none">Sign Up</a></p>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer class="py-4 bg-dark text-white mt-5">
        <div class="container text-center">
            <p class="mb-0">&copy; 2025 Art Critique. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    # Define the port to use
    port = int(os.environ.get('PORT', 8090))
    
    print(f"Starting Flask server with Google auth template preview on port {port}")
    print(f"Visit http://localhost:{port} to see the styled page")
    print("Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=port, debug=True)