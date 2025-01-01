from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, UserEvent
from tracker import UserTracker
import logging
import os

app = Flask(__name__, static_folder='../frontend')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
tracker = UserTracker()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with app.app_context():
    db.create_all()

# Serve frontend
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/track', methods=['POST'])
def track_event():
    data = request.json
    success = tracker.track_event(
        user_id=data.get('user_id'),
        event_type=data.get('event_type'),
        event_data=data.get('event_data')
    )
    return jsonify({'success': success})

@app.route('/stats/<user_id>')
def get_stats(user_id):
    stats = tracker.get_user_stats(user_id)
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)