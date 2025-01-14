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
    print("\n=== Track User Request ===")
    if request.method == 'OPTIONS':
        print("OPTIONS request received")
        return '', 200

    try:
        print("Request headers:", request.headers)
        print("Request body:", request.json)
        
        body = request.json
        if not verify_api_key(request.headers.get('Authorization', '')):
            print("❌ Invalid API key")
            return jsonify({"error": "Invalid API key"}), 401

        # Validate required fields
        email = body.get('email')
        plan_type = body.get('planType')
        
        print(f"📧 Email: {email}")
        print(f"📋 Plan Type: {plan_type}")
        
        if not email or not plan_type:
            print("❌ Missing required fields")
            return jsonify({"error": "Email and planType are required"}), 400

        current_time = datetime.now(timezone.utc).isoformat()
        status = body.get('status', 'active')
        print(f"👤 Status: {status}")

        try:
            print("🔍 Checking if user exists...")
            user_response = supabase.table('users').select('user_id').eq('email', email).execute()
            print("Supabase response:", user_response)
            
            if user_response.data:
                user_id = user_response.data[0]['user_id']
                print(f"✏️ Updating existing user: {email} ({user_id})")
                
                supabase.table('users').update({
                    'plan_type': plan_type,
                    'status': status,
                    'updated_at': current_time
                }).eq('user_id', user_id).execute()
                
                print("✅ User updated successfully")
            else:
                user_id = str(uuid.uuid4())
                print(f"➕ Creating new user: {email} ({user_id})")
                
                supabase.table('users').insert({
                    'user_id': user_id,
                    'email': email,
                    'plan_type': plan_type,
                    'status': status,
                    'created_at': current_time
                }).execute()
                
                print("✅ User created successfully")
                print("Initializing metric tables...")

                for table in ['behavioral_metrics', 'subscription_metrics']:
                    print(f"  → Initializing {table}")
                    supabase.table(table).insert({
                        'user_id': user_id,
                        'created_at': current_time
                    }).execute()
                    print(f"  ✅ {table} initialized")

            print("🎉 Operation completed successfully")
            return jsonify({'success': True, 'user_id': user_id})

        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            print("Detailed error:", e)
            return jsonify({'error': f"Database error: {str(e)}"}), 500

    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        print("Detailed error:", e)
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