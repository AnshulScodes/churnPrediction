from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, UserEvent
from dotenv import load_dotenv
import posthog
import logging
import os
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

# Initialize PostHog
posthog.api_key = os.getenv('POSTHOG_API_KEY')
posthog.host = os.getenv('POSTHOG_HOST')

db.init_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with app.app_context():
    db.create_all()

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/config')
def get_config():
    return jsonify({
        'posthog_api_key': os.getenv('POSTHOG_API_KEY'),
        'posthog_host': os.getenv('POSTHOG_HOST')
    })

@app.route('/stats/<user_id>')
def get_stats(user_id):
    try:
        api_key = os.getenv('POSTHOG_API_KEY')
        if not api_key:
            return jsonify({'error': 'No API key found in environment'}), 500
        if not api_key.startswith('phx_'):
            return jsonify({'error': 'Invalid API key format - must start with phx_'}), 500
            
        host = os.getenv('POSTHOG_HOST', 'https://app.posthog.com').rstrip('/')
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        person_url = f'{host}/api/projects/@current/events'
        params = {
            'distinct_id': user_id,
            'limit': 100
        }
        
        logger.info(f"Request details:")
        logger.info(f"URL: {person_url}")
        logger.info(f"API Key prefix: {api_key[:6]}...")
        logger.info(f"Headers: {headers}")
        
        response = requests.get(
            person_url, 
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            events_data = response.json()
            stats = {
                'pageviews': len([e for e in events_data.get('results', []) if e['event'] == '$pageview']),
                'clicks': len([e for e in events_data.get('results', []) if e['event'] == '$autocapture']),
                'total_events': len(events_data.get('results', [])),
                'recent_events': events_data.get('results', [])[:5]
            }
            return jsonify(stats)
        else:
            return jsonify({
                'error': f"PostHog API error: {response.status_code}",
                'details': response.text,
                'request_url': person_url,
                'key_prefix': api_key[:6],
                'key_length': len(api_key)
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug-key')
def debug_key():
    api_key = os.getenv('POSTHOG_API_KEY')
    return jsonify({
        'key_starts_with': api_key[:6] if api_key else 'None',
        'key_length': len(api_key) if api_key else 0,
        'is_project_key': api_key.startswith('phx_') if api_key else False
    })

if __name__ == '__main__':
    app.run(debug=True)