import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.api.app import app

# Vercel serverless handler
def handler(request):
    return app(request) 