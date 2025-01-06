from http.server import BaseHTTPRequestHandler
import json
import os
from supabase import create_client
import secrets
from datetime import datetime, timezone
import uuid

# Initialize Supabase
supabase = create_client(
    os.environ.get("SUPABASE_URL", ""),
    os.environ.get("SUPABASE_KEY", "")
)

# Store API keys (in memory - will reset on deployment)
API_KEYS = {}

def generate_api_key():
    return secrets.token_urlsafe(32)

def parse_body(handler):
    content_length = int(handler.headers.get('Content-Length', 0))
    return json.loads(handler.rfile.read(content_length))

def send_json_response(handler, data, status=200):
    handler.send_response(status)
    handler.send_header('Content-type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode())

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            send_json_response(self, {"status": "healthy"})
        else:
            send_json_response(self, {"error": "Not found"}, 404)

    def do_POST(self):
        if self.path == '/generate-api-key':
            api_key = generate_api_key()
            API_KEYS[api_key] = {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'active': True
            }
            send_json_response(self, {
                'api_key': api_key,
                'message': 'Store this API key securely. It won\'t be shown again.'
            })
            return

        # Check API key for protected routes
        api_key = self.headers.get('Authorization', '').replace('Bearer ', '')
        if not api_key or api_key not in API_KEYS:
            send_json_response(self, {'error': 'Invalid API key'}, 401)
            return

        try:
            data = parse_body(self)

            if self.path == '/track/user':
                email = data.get('email')
                plan_type = data.get('planType', 'free')
                
                # Check if user exists
                response = supabase.table('users')\
                    .select('user_id')\
                    .eq('email', email)\
                    .execute()
                
                current_time = datetime.now(timezone.utc).isoformat()
                
                if response.data:
                    user_id = response.data[0]['user_id']
                    supabase.table('users')\
                        .update({
                            'plan_type': plan_type,
                            'updated_at': current_time
                        })\
                        .eq('user_id', user_id)\
                        .execute()
                else:
                    user_id = str(uuid.uuid4())
                    supabase.table('users')\
                        .insert({
                            'user_id': user_id,
                            'email': email,
                            'plan_type': plan_type,
                            'created_at': current_time
                        })\
                        .execute()

                send_json_response(self, {'success': True, 'user_id': user_id})

            elif self.path == '/track/metrics':
                user_id = data.get('user_id')
                feature_name = data.get('metrics', {}).get('feature_name')
                
                current_time = datetime.now(timezone.utc).isoformat()
                
                supabase.table('feature_usage').insert({
                    'user_id': user_id,
                    'feature_name': feature_name,
                    'created_at': current_time
                }).execute()

                send_json_response(self, {'success': True})

            else:
                send_json_response(self, {"error": "Not found"}, 404)

        except Exception as e:
            send_json_response(self, {'error': str(e)}, 500)