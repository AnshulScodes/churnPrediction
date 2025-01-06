from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import os
from supabase import create_client, Client
import logging
import uuid
from typing_extensions import TypeVar, ClassVar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize Supabase
try:
    supabase: Client = create_client(
        os.environ.get("SUPABASE_URL", ""),
        os.environ.get("SUPABASE_KEY", "")
    )
    logger.info("Supabase initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase: {e}")
    supabase = None

def validate_api_key(api_key):
    if not api_key:
        return False
    if not supabase:
        return True  # For development without Supabase
    result = supabase.table('api_keys').select('*').eq('key', api_key).execute()
    return bool(result.data)

@app.route('/')
def home():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "supabase_connected": supabase is not None
    })

@app.route('/generate-api-key', methods=['POST'])
def generate_api_key():
    try:
        api_key = str(uuid.uuid4())
        
        if supabase:
            result = supabase.table('api_keys').insert({
                'key': api_key,
                'created_at': datetime.now(timezone.utc).isoformat()
            }).execute()
            logger.info(f"API key stored: {api_key}")
        
        return jsonify({"api_key": api_key})
    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/track/user', methods=['POST'])
def track_user():
    try:
        data = request.json
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not validate_api_key(api_key):
            return jsonify({"error": "Invalid API key"}), 401

        user_id = str(uuid.uuid4())
        
        if supabase:
            result = supabase.table('users').insert({
                'id': user_id,
                'email': data.get('email'),
                'plan_type': data.get('planType'),
                'created_at': datetime.now(timezone.utc).isoformat()
            }).execute()
            logger.info(f"User tracked: {user_id}")
        
        return jsonify({"success": True, "user_id": user_id})
    except Exception as e:
        logger.error(f"Error tracking user: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/track/feature', methods=['POST'])
def track_feature():
    try:
        data = request.json
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not validate_api_key(api_key):
            return jsonify({"error": "Invalid API key"}), 401

        if supabase:
            result = supabase.table('feature_usage').insert({
                'user_id': data.get('user_id'),
                'feature_name': data.get('type'),
                'metrics': data.get('metrics', {}),
                'created_at': datetime.now(timezone.utc).isoformat()
            }).execute()
            logger.info(f"Feature usage tracked for user: {data.get('user_id')}")
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error tracking feature: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/metrics', methods=['GET'])
def get_metrics():
    try:
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not validate_api_key(api_key):
            return jsonify({"error": "Invalid API key"}), 401

        if not supabase:
            return jsonify({"error": "Database not connected"}), 500

        # Get all feature usage data
        result = supabase.table('feature_usage').select('*').execute()
        
        # Process and aggregate metrics
        metrics = {}
        for usage in result.data:
            feature = usage['feature_name']
            if feature not in metrics:
                metrics[feature] = {
                    'total_uses': 0,
                    'unique_users': set(),
                    'metrics': {}
                }
            metrics[feature]['total_uses'] += 1
            metrics[feature]['unique_users'].add(usage['user_id'])
            
            # Aggregate custom metrics
            if usage.get('metrics'):
                for key, value in usage['metrics'].items():
                    if key not in metrics[feature]['metrics']:
                        metrics[feature]['metrics'][key] = 0
                    metrics[feature]['metrics'][key] += value

        # Convert sets to lengths for JSON serialization
        for feature in metrics:
            metrics[feature]['unique_users'] = len(metrics[feature]['unique_users'])

        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({"error": str(e)}), 500

def handler(request):
    """Handle Vercel serverless function requests"""
    return app(request)

if __name__ == '__main__':
    # For local development only
    app.run(port=5000) 