from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Create Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Import routes after app creation to avoid circular imports
from .app import *

def handler(request):
    """Vercel serverless handler"""
    return app(request)