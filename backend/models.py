from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # api_call, button_click, preference_change
    event_data = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserEvent {self.event_type} by {self.user_id}>' 