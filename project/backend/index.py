from http.server import BaseHTTPRequestHandler
import json
import os
from supabase import create_client
from datetime import datetime, timezone
import uuid

# Initialize Supabase
supabase = create_client(
    os.environ.get("SUPABASE_URL", ""),
    os.environ.get("SUPABASE_KEY", "")
)

def handler(request):
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Content-Type': 'application/json'
    }

    # Handle OPTIONS request
    if request.method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers}

    try:
        # Parse body
        body = json.loads(request.body) if request.body else {}
        
        # Verify API key
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({"error": "Unauthorized"})
            }

        api_key = auth_header.split(' ')[1]
        key_check = supabase.table('api_keys').select('*').eq('key', api_key).execute()
        if not key_check.data:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({"error": "Invalid API key"})
            }

        current_time = datetime.now(timezone.utc).isoformat()

        if request.path == '/track/user':
            email = body.get('email')
            plan_type = body.get('planType', 'free')
            status = body.get('status', 'active')
            
            response = supabase.table('users').select('user_id').eq('email', email).execute()
            
            if response.data:
                user_id = response.data[0]['user_id']
                supabase.table('users').update({
                    'plan_type': plan_type,
                    'status': status,
                    'updated_at': current_time
                }).eq('user_id', user_id).execute()
            else:
                user_id = str(uuid.uuid4())
                supabase.table('users').insert({
                    'user_id': user_id,
                    'email': email,
                    'plan_type': plan_type,
                    'status': status,
                    'created_at': current_time
                }).execute()

            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'success': True, 'user_id': user_id})
            }

        elif request.path == '/track/metrics':
            user_id = body.get('user_id')
            metrics = body.get('metrics', {})
            
            supabase.table('metrics').insert({
                'user_id': user_id,
                'metrics': metrics,
                'created_at': current_time
            }).execute()

            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'success': True})
            }

        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({"error": "Not found"})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }