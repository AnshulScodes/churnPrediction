from flask import Flask, request, jsonify
from typing import TypeVar, ClassVar
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from flask_cors import CORS
from functools import wraps
import secrets
from serverless_wsgi import handle_request
from index import app
from flask import render_template

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# Initialize Flask and Supabase
app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
# supabase: Client = create_client(
#     os.environ.get("SUPABASE_URL"),
#     os.environ.get("SUPABASE_KEY")
# )

# Store API keys (in production, use a database)
API_KEYS = {}

# def generate_api_key():
#     """Generate a new API key"""
#     return secrets.token_urlsafe(32)

# @app.route('/generate-api-key', methods=['POST'])
# def create_api_key():
#     """Create a new API key for a client"""
#     api_key = generate_api_key()
#     API_KEYS[api_key] = {
#         'created_at': datetime.now(timezone.utc),
#         'active': True
#     }
#     return jsonify({
#         'api_key': api_key,
#         'message': 'Store this API key securely. It won\'t be shown again.'
#     })

# def require_api_key(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         api_key = request.headers.get('Authorization')
#         if api_key:
#             api_key = api_key.replace('Bearer ', '')
        
#         if not api_key or api_key not in API_KEYS:
#             return jsonify({'error': 'Invalid API key'}), 401
#         return f(*args, **kwargs)
#     return decorated_function

# def log_api_call(endpoint: str, data: Dict[str, Any], result: Dict[str, Any]) -> None:
#     """Log API call details"""
#     logger.info(f"""
#     API Call:
#     Endpoint: {endpoint}
#     Input Data: {data}
#     Result: {result}
#     """)

# @app.route('/track/user', methods=['POST'])
# @require_api_key
# def track_user():
#     """Track new or existing user with proper data validation"""
#     try:
#         data = request.json
#         email = data.get('email')
#         plan_type = data.get('plan_type', 'free')
#         status = data.get('status', 'active')

#         if not email:
#             raise ValueError("Email is required")

#         logger.info(f"""
#         Tracking user:
#         Email: {email}
#         Plan: {plan_type}
#         Status: {status}
#         """)

#         # Check if user exists
#         response = supabase.table('users')\
#             .select('user_id')\
#             .eq('email', email)\
#             .execute()
        
#         current_time = datetime.now(timezone.utc).isoformat()
        
#         if response.data:
#             user_id = response.data[0]['user_id']
#             result = supabase.table('users')\
#                 .update({
#                     'plan_type': plan_type,
#                     'status': status,
#                     'updated_at': current_time
#                 })\
#                 .eq('user_id', user_id)\
#                 .execute()
#             logger.info(f"Updated existing user: {user_id}")
#         else:
#             user_id = str(uuid.uuid4())
#             result = supabase.table('users')\
#                 .insert({
#                     'user_id': user_id,
#                     'email': email,
#                     'plan_type': plan_type,
#                     'status': status,
#                     'sign_up_date': current_time,
#                     'created_at': current_time,
#                     'updated_at': current_time
#                 })\
#                 .execute()
#             logger.info(f"Created new user: {user_id}")

#         response_data = {'success': True, 'user_id': user_id}
#         logger.info(f"Successfully tracked user: {response_data}")
#         return jsonify(response_data)

#     except ValueError as ve:
#         error_msg = str(ve)
#         logger.error(f"Validation error: {error_msg}")
#         return jsonify({'success': False, 'error': error_msg}), 400

#     except Exception as e:
#         error_msg = f"Error tracking user: {str(e)}"
#         logger.error(error_msg)
#         return jsonify({'success': False, 'error': error_msg}), 500

# @app.route('/track/metrics', methods=['POST'])
# @require_api_key
# def track_metrics():
#     try:
#         data = request.json
#         user_id = data.get('user_id')
#         feature_name = data.get('metrics', {}).get('feature_name')
#         current_time = datetime.now(timezone.utc)

#         logger.info(f"Tracking feature usage: {feature_name} for user: {user_id}")

#         # Update engagement_metrics
#         try:
#             # Check if entry exists
#             existing = supabase.table('engagement_metrics')\
#                 .select('*')\
#                 .eq('user_id', user_id)\
#                 .eq('features_used', feature_name)\
#                 .execute()

#             if existing.data:
#                 # Update existing record
#                 result = supabase.table('engagement_metrics')\
#                     .update({
#                         'usage_count': existing.data[0]['usage_count'] + 1,
#                         'last_used_at': current_time.isoformat(),
#                         'updated_at': current_time.isoformat()
#                     })\
#                     .eq('user_id', user_id)\
#                     .eq('features_used', feature_name)\
#                     .execute()
#             else:
#                 # Create new record
#                 result = supabase.table('engagement_metrics')\
#                     .insert({
#                         'user_id': user_id,
#                         'features_used': feature_name,
#                         'usage_count': 1,
#                         'first_used_at': current_time.isoformat(),
#                         'last_used_at': current_time.isoformat()
#                     })\
#                     .execute()

#             # Update feature_analytics
#             hour = current_time.hour
#             day = current_time.strftime('%a').lower()
            
#             # Get time of day
#             if 5 <= hour < 12:
#                 time_of_day = 'morning'
#             elif 12 <= hour < 17:
#                 time_of_day = 'afternoon'
#             elif 17 <= hour < 22:
#                 time_of_day = 'evening'
#             else:
#                 time_of_day = 'night'

#             # Get existing feature analytics
#             feature_data = supabase.table('feature_analytics')\
#                 .select('*')\
#                 .eq('feature_name', feature_name)\
#                 .execute()

#             if feature_data.data:
#                 current = feature_data.data[0]
#                 peak_usage = current['peak_usage_times']
#                 daily_usage = current['usage_by_day']
                
#                 # Update counts
#                 peak_usage[time_of_day] += 1
#                 daily_usage[day] += 1

#                 result = supabase.table('feature_analytics')\
#                     .update({
#                         'total_usage_count': current['total_usage_count'] + 1,
#                         'peak_usage_times': peak_usage,
#                         'usage_by_day': daily_usage,
#                         'updated_at': current_time.isoformat()
#                     })\
#                     .eq('feature_name', feature_name)\
#                     .execute()
#             else:
#                 # Initialize new feature tracking
#                 peak_usage = {'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0}
#                 daily_usage = {'mon': 0, 'tue': 0, 'wed': 0, 'thu': 0, 'fri': 0, 'sat': 0, 'sun': 0}
                
#                 peak_usage[time_of_day] = 1
#                 daily_usage[day] = 1

#                 result = supabase.table('feature_analytics')\
#                     .insert({
#                         'feature_name': feature_name,
#                         'total_usage_count': 1,
#                         'unique_users_count': 1,
#                         'peak_usage_times': peak_usage,
#                         'usage_by_day': daily_usage
#                     })\
#                     .execute()

#             return jsonify({
#                 'success': True,
#                 'message': f"Tracked usage of {feature_name}"
#             })

#         except Exception as e:
#             logger.error(f"Error tracking metrics: {str(e)}")
#             raise

#     except Exception as e:
#         error_msg = f"Error in track_metrics: {str(e)}"
#         logger.error(error_msg)
#         return jsonify({'success': False, 'error': error_msg}), 500

# @app.route('/get/metrics/<user_id>', methods=['GET'])
# def get_metrics(user_id):
#     """Get all metrics for a user"""
#     try:
#         logger.info(f"Fetching metrics for user: {user_id}")

#         # Get all metrics from all tables
#         tables = [
#             'users',
#             'engagement_metrics',
#             'subscription_metrics',
#             'support_metrics',
#             'communication_metrics',
#             'behavioral_metrics'
#         ]

#         metrics = {}
#         for table in tables:
#             response = supabase.table(table)\
#                 .select('*')\
#                 .eq('user_id', user_id)\
#                 .execute()
#             metrics[table] = response.data[0] if response.data else None
#             logger.info(f"Retrieved {table} data: {metrics[table]}")

#         response_data = {'success': True, 'metrics': metrics}
#         log_api_call(f'/get/metrics/{user_id}', {}, response_data)
#         return jsonify(response_data)

#     except Exception as e:
#         error_msg = f"Error getting metrics: {str(e)}"
#         logger.error(error_msg)
#         return jsonify({'success': False, 'error': error_msg}), 500

# def update_behavioral_metrics(user_id, feature_name):
#     """Update behavioral metrics based on user activity"""
#     try:
#         current_time = datetime.now(timezone.utc)
        
#         # Get existing behavioral data
#         existing = supabase.table('behavioral_metrics')\
#             .select('*')\
#             .eq('user_id', user_id)\
#             .execute()

#         # Get user's feature usage history
#         feature_usage = supabase.table('engagement_metrics')\
#             .select('*')\
#             .eq('user_id', user_id)\
#             .execute()

#         # Calculate metrics
#         unique_features = set([f['feature_name'] for f in feature_usage.data])
#         total_features = len(unique_features)
        
#         # Define core features
#         core_features = {'search', 'export', 'reports', 'analytics'}
#         core_features_used = list(unique_features.intersection(core_features))

#         if existing.data:
#             record = existing.data[0]
#             last_seen = datetime.fromisoformat(record['last_seen_date'].replace('Z', '+00:00'))
#             days_since_last = (current_time - last_seen).days
            
#             # Calculate usage trend (-1 to 1)
#             if days_since_last == 0:
#                 usage_trend = min(record['usage_trend'] + 0.1, 1.0)
#             else:
#                 usage_trend = max(record['usage_trend'] - (0.1 * days_since_last), -1.0)

#             # Calculate risk score (0 to 1)
#             risk_factors = [
#                 days_since_last > 7,  # Inactive for a week
#                 len(core_features_used) < 2,  # Using less than 2 core features
#                 usage_trend < 0,  # Declining usage
#                 record['average_session_duration'] < 60  # Short sessions
#             ]
#             churn_risk = sum(risk_factors) / len(risk_factors)

#             # Calculate engagement score (0 to 1)
#             engagement_factors = [
#                 len(core_features_used) / len(core_features),  # Core feature usage
#                 min(record['daily_active_days'] / 30, 1.0),  # Monthly activity
#                 max(usage_trend, 0),  # Positive usage trend
#                 min(record['average_session_duration'] / 300, 1.0)  # Session duration (max 5 min)
#             ]
#             engagement_score = sum(engagement_factors) / len(engagement_factors)

#             # Update record
#             result = supabase.table('behavioral_metrics')\
#                 .update({
#                     'daily_active_days': record['daily_active_days'] + 1,
#                     'weekly_active_days': min(record['weekly_active_days'] + 1, 7),
#                     'features_used': total_features,
#                     'core_features_used': core_features_used,
#                     'usage_trend': usage_trend,
#                     'inactive_days': 0,
#                     'last_seen_date': current_time.isoformat(),
#                     'churn_risk_score': churn_risk,
#                     'engagement_score': engagement_score,
#                     'updated_at': current_time.isoformat()
#                 })\
#                 .eq('user_id', user_id)\
#                 .execute()
#         else:
#             # Create new record
#             result = supabase.table('behavioral_metrics')\
#                 .insert({
#                     'user_id': user_id,
#                     'daily_active_days': 1,
#                     'weekly_active_days': 1,
#                     'features_used': total_features,
#                     'core_features_used': core_features_used,
#                     'last_seen_date': current_time.isoformat(),
#                     'churn_risk_score': 0.75,  # High initial risk for new users
#                     'engagement_score': 0.25  # Low initial engagement for new users
#                 })\
#                 .execute()

#         logger.info(f"Updated behavioral metrics for user {user_id}")
#         return True

#     except Exception as e:
#         logger.error(f"Error updating behavioral metrics: {str(e)}")
#         return False

@app.route("/")
def home():
    return render_template('../../frontend/index.html')
if __name__ == '__main__':
    app.run()
# @app.route('/api/health')
# def health():
#     return jsonify({
#         "status": "healthy",
#         "timestamp": datetime.now(timezone.utc).isoformat(),
#         "supabase_connected": supabase is not None
#     })

# # Handler for Vercel
# def handler(event, context):
#     return handle_request(app, event, context)

# # For Vercel, we need this
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
