from datetime import datetime, timedelta
from models import db, UserEvent
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserTracker:
    def __init__(self):
        self.model = RandomForestClassifier()
        
    def track_event(self, user_id, event_type, event_data=None):
        try:
            event = UserEvent(
                user_id=user_id,
                event_type=event_type,
                event_data=event_data
            )
            db.session.add(event)
            db.session.commit()
            logger.info(f"Tracked event: {event_type} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}")
            return False

    def get_user_stats(self, user_id, days=30):
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            events = UserEvent.query.filter(
                UserEvent.user_id == user_id,
                UserEvent.timestamp >= cutoff_date
            ).all()
            
            stats = {
                'api_calls': len([e for e in events if e.event_type == 'api_call']),
                'button_clicks': len([e for e in events if e.event_type == 'button_click']),
                'preference_changes': len([e for e in events if e.event_type == 'preference_change'])
            }
            logger.info(f"Retrieved stats for user {user_id}: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return None 