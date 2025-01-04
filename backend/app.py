from flask import Flask, request, jsonify
from dotenv import load_dotenv
from supabase import create_client
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask and Supabase
app = Flask(__name__)
CORS(app)
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def log_api_call(endpoint: str, data: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Log API call details"""
    logger.info(f"""
    API Call:
    Endpoint: {endpoint}
    Input Data: {data}
    Result: {result}
    """)

@app.route('/track/user', methods=['POST'])
def track_user():
    """Track new or existing user"""
    try:
        data = request.json
        email = data.get('email')
        plan_type = data.get('plan_type', 'free')
        status = data.get('status', 'active')

        logger.info(f"Tracking user: {email} with plan: {plan_type}, status: {status}")

        # Check if user exists
        response = supabase.table('users').select('user_id').eq('email', email).execute()
        
        if response.data:
            user_id = response.data[0]['user_id']
            result = supabase.table('users').update({
                'plan_type': plan_type,
                'status': status,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }).eq('user_id', user_id).execute()
            logger.info(f"Updated existing user: {user_id}")
        else:
            user_id = str(uuid.uuid4())
            result = supabase.table('users').insert({
                'user_id': user_id,
                'email': email,
                'plan_type': plan_type,
                'status': status,
                'sign_up_date': datetime.now(timezone.utc).isoformat()
            }).execute()
            logger.info(f"Created new user: {user_id}")

        response_data = {'success': True, 'user_id': user_id}
        log_api_call('/track/user', data, response_data)
        return jsonify(response_data)

    except Exception as e:
        error_msg = f"Error tracking user: {str(e)}"
        logger.error(error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/track/metrics', methods=['POST'])
def track_metrics():
    """Track various metrics"""
    try:
        data = request.json
        user_id = data.get('user_id')
        metric_type = data.get('type')
        metrics = data.get('metrics', {})

        logger.info(f"""
        Tracking metrics:
        User ID: {user_id}
        Type: {metric_type}
        Metrics: {metrics}
        """)

        # Map metric types to table names
        table_map = {
            'engagement': 'engagement_metrics',
            'subscription': 'subscription_metrics',
            'support': 'support_metrics',
            'communication': 'communication_metrics',
            'behavioral': 'behavioral_metrics'
        }

        if metric_type not in table_map:
            error_msg = f'Invalid metric type. Must be one of: {", ".join(table_map.keys())}'
            logger.error(error_msg)
            return jsonify({'success': False, 'error': error_msg}), 400

        # Add timestamps
        metrics.update({
            'user_id': user_id,
            'updated_at': datetime.now(timezone.utc).isoformat()
        })

        logger.info(f"Attempting to upsert into table: {table_map[metric_type]}")
        logger.info(f"Upsert data: {metrics}")

        # Update metrics in appropriate table
        try:
            result = supabase.table(table_map[metric_type])\
                .upsert(metrics)\
                .execute()
            logger.info(f"Upsert result: {result}")
        except Exception as e:
            logger.error(f"Supabase error: {str(e)}")
            raise

        response_data = {'success': True, 'updated': metric_type}
        log_api_call('/track/metrics', data, response_data)
        return jsonify(response_data)

    except Exception as e:
        error_msg = f"Error tracking metrics: {str(e)}"
        logger.error(error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/get/metrics/<user_id>', methods=['GET'])
def get_metrics(user_id):
    """Get all metrics for a user"""
    try:
        logger.info(f"Fetching metrics for user: {user_id}")

        # Get all metrics from all tables
        tables = [
            'users',
            'engagement_metrics',
            'subscription_metrics',
            'support_metrics',
            'communication_metrics',
            'behavioral_metrics'
        ]

        metrics = {}
        for table in tables:
            response = supabase.table(table)\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()
            metrics[table] = response.data[0] if response.data else None
            logger.info(f"Retrieved {table} data: {metrics[table]}")

        response_data = {'success': True, 'metrics': metrics}
        log_api_call(f'/get/metrics/{user_id}', {}, response_data)
        return jsonify(response_data)

    except Exception as e:
        error_msg = f"Error getting metrics: {str(e)}"
        logger.error(error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True)
