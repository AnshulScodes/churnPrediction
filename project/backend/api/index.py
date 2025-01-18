from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import json
import os
from supabase import create_client
from datetime import datetime, timezone, timedelta
import uuid
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://churn-prediction-nine.vercel.app",
            "https://churn-prediction-anshulscodes-projects.vercel.app/"
            "https://churn-prediction-git-main-anshulscodes-projects.vercel.app/"
            "*"  # Allow all origins in production
        ]
    }
})

# Initialize Supabase
supabase = create_client(
    os.environ.get("SUPABASE_URL", ""),
    os.environ.get("SUPABASE_KEY", "")
)

def update_behavioral_metrics(user_id: str):
    print(f"🔄 Updating behavioral metrics for user {user_id}")
    current_time = datetime.now(timezone.utc)
    
    try:
        # Get session data
        sessions = supabase.table('user_sessions').select('*').eq('user_id', user_id).execute()
        print(f"📊 Found {len(sessions.data)} sessions")
        
        # Get feature usage data
        features = supabase.table('engagement_metrics').select('*').eq('user_id', user_id).execute()
        print(f"🎯 Found {len(features.data)} feature records")
        
        # Calculate metrics
        avg_session = int(sum(s['session_duration'] for s in sessions.data) / len(sessions.data)) if sessions.data else 0
        unique_features = len(set(f['features_used'] for f in features.data)) if features.data else 0
        core_features = list(set(f['features_used'] for f in features.data))
        
        # Calculate active days
        month_start = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        week_start = current_time - timedelta(days=current_time.weekday())
        
        daily_sessions = supabase.table('user_sessions')\
            .select('created_at')\
            .eq('user_id', user_id)\
            .gte('created_at', month_start.isoformat())\
            .execute()
        
        weekly_sessions = [s for s in daily_sessions.data 
                         if datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')) >= week_start]
        
        daily_active = len(set(datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')).date() 
                            for s in daily_sessions.data))
        weekly_active = len(set(datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')).date() 
                            for s in weekly_sessions))
        
        # Calculate inactive days
        last_seen = max([s['created_at'] for s in sessions.data]) if sessions.data else current_time.isoformat()
        inactive_days = (current_time - datetime.fromisoformat(last_seen.replace('Z', '+00:00'))).days
        
        # Calculate usage trend (compare this week's activity to last week's)
        last_week_start = week_start - timedelta(days=7)
        last_week_sessions = supabase.table('user_sessions')\
            .select('created_at')\
            .eq('user_id', user_id)\
            .gte('created_at', last_week_start.isoformat())\
            .lt('created_at', week_start.isoformat())\
            .execute()
        
        this_week_count = len(weekly_sessions)
        last_week_count = len(last_week_sessions.data)
        usage_trend = (this_week_count - last_week_count) / (last_week_count + 1)  # Add 1 to avoid division by zero
        
        # Calculate simple engagement score (can be made more sophisticated later)
        engagement_score = (daily_active / 30.0 * 0.4 +  # Weight monthly activity
                          weekly_active / 7.0 * 0.3 +    # Weight weekly activity
                          min(unique_features / 5.0, 1) * 0.3)  # Weight feature usage
        
        print(f"📈 Calculated metrics for user {user_id}:")
        print(f"Daily active days: {daily_active}")
        print(f"Weekly active days: {weekly_active}")
        print(f"Average session duration: {avg_session}")
        print(f"Features used: {unique_features}")
        print(f"Usage trend: {usage_trend}")
        print(f"Engagement score: {engagement_score}")
        
        # Update the behavioral_metrics table
        supabase.table('behavioral_metrics').upsert({
            'user_id': user_id,
            'daily_active_days': daily_active,
            'weekly_active_days': weekly_active,
            'average_session_duration': avg_session,
            'last_seen_date': current_time.isoformat(),
            'features_used': unique_features,
            'core_features_used': ','.join(core_features) if core_features else '',
            'usage_trend': usage_trend,
            'inactive_days': inactive_days,
            'engagement_score': engagement_score,
            'updated_at': current_time.isoformat()
        }).execute()
        
        print(f"✅ Successfully updated behavioral metrics for user {user_id}")
        
    except Exception as e:
        print(f"❌ Error updating behavioral metrics: {str(e)}")
        print("Detailed error:", e)

@app.route('/track/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def track(path):
    if request.method == 'OPTIONS':
        return jsonify({'message': 'Preflight OK'}), 204
    return jsonify({'message': f'Tracking {path}'})

def verify_api_key(auth_header):
    if not auth_header.startswith('Bearer '):
        return False
    api_key = auth_header.split(' ')[1]
    result = supabase.table('api_keys').select('*').eq('api_key', api_key).eq('active', True).execute()
    return bool(result.data)

@app.route('/health', methods=['GET'])
@cross_origin(origins='*')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/track/user', methods=['POST', 'OPTIONS'])
@cross_origin(origins='*')
def track_user():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        print("\n=== Track User Request ===")
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

            # Just call it directly
            update_behavioral_metrics(user_id)
            
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
@cross_origin(origins='*')
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

        # Just call it directly
        update_behavioral_metrics(user_id)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/track/session', methods=['POST', 'OPTIONS'])
@cross_origin(origins='*')
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

        # Just call it directly
        update_behavioral_metrics(user_id)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)