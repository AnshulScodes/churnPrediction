from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from supabase import create_client
from datetime import datetime, timezone
import uuid
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# Initialize Supabase
supabase = create_client(
    os.environ.get("SUPABASE_URL", ""),
    os.environ.get("SUPABASE_KEY", "")
)

def verify_api_key(auth_header):
    if not auth_header.startswith('Bearer '):
        return False
    api_key = auth_header.split(' ')[1]
    result = supabase.table('api_keys').select('*').eq('api_key', api_key).eq('active', True).execute()
    return bool(result.data)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/track/user', methods=['POST', 'OPTIONS'])
def track_user():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        body = request.json
        if not verify_api_key(request.headers.get('Authorization', '')):
            return jsonify({"error": "Invalid API key"}), 401

        current_time = datetime.now(timezone.utc).isoformat()
        email = body.get('email')
        plan_type = body.get('planType', 'free')
        status = body.get('status', 'active')

        # Check if user exists
        user_response = supabase.table('users').select('user_id').eq('email', email).execute()
        
        if user_response.data:
            user_id = user_response.data[0]['user_id']
            # Update user
            supabase.table('users').update({
                'plan_type': plan_type,
                'status': status,
                'updated_at': current_time
            }).eq('user_id', user_id).execute()
        else:
            # Create new user
            user_id = str(uuid.uuid4())
            supabase.table('users').insert({
                'user_id': user_id,
                'email': email,
                'plan_type': plan_type,
                'status': status,
                'created_at': current_time
            }).execute()

            # Initialize other metric tables
            tables = ['behavioral_metrics', 'subscription_metrics', 'support_metrics', 'communication_metrics']
            for table in tables:
                supabase.table(table).insert({
                    'user_id': user_id,
                    'created_at': current_time
                }).execute()

        return jsonify({'success': True, 'user_id': user_id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/track/feature', methods=['POST', 'OPTIONS'])
def track_feature():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        body = request.json
        if not verify_api_key(request.headers.get('Authorization', '')):
            return jsonify({"error": "Invalid API key"}), 401

        current_time = datetime.now(timezone.utc).isoformat()
        user_id = body.get('user_id')
        feature_name = body.get('feature_name')

        # Update engagement_metrics
        engagement_result = supabase.table('engagement_metrics').select('*').eq('user_id', user_id).eq('features_used', feature_name).execute()
        
        if engagement_result.data:
            supabase.table('engagement_metrics').update({
                'usage_count': engagement_result.data[0]['usage_count'] + 1,
                'last_used_at': current_time,
                'updated_at': current_time
            }).eq('id', engagement_result.data[0]['id']).execute()
        else:
            supabase.table('engagement_metrics').insert({
                'user_id': user_id,
                'features_used': feature_name,
                'first_used_at': current_time,
                'last_used_at': current_time
            }).execute()

        # Update feature_analytics
        analytics_result = supabase.table('feature_analytics').select('*').eq('feature_name', feature_name).execute()
        
        if analytics_result.data:
            supabase.table('feature_analytics').update({
                'total_usage_count': analytics_result.data[0]['total_usage_count'] + 1,
                'updated_at': current_time
            }).eq('feature_name', feature_name).execute()
        else:
            supabase.table('feature_analytics').insert({
                'feature_name': feature_name,
                'total_usage_count': 1
            }).execute()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/track/session', methods=['POST', 'OPTIONS'])
def track_session():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        body = request.json
        if not verify_api_key(request.headers.get('Authorization', '')):
            return jsonify({"error": "Invalid API key"}), 401

        current_time = datetime.now(timezone.utc).isoformat()
        user_id = body.get('user_id')
        duration = body.get('duration', 0)

        supabase.table('user_sessions').insert({
            'user_id': user_id,
            'session_duration': duration,
            'last_active_date': current_time
        }).execute()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)