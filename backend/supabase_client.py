from supabase import create_client
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class SupabaseTracker:
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase = create_client(supabase_url, supabase_key)

    def track_api_call(self, user_id, session_id, endpoint, response_time, status_code, data_size):
        try:
            self.supabase.table('api_metrics').insert({
                'user_id': user_id,
                'session_id': session_id,
                'endpoint': endpoint,
                'response_time': response_time,
                'status_code': status_code,
                'data_size': data_size
            }).execute()
        except Exception as e:
            logger.error(f"Error tracking API call: {str(e)}")

    def track_feature_usage(self, user_id, feature_name, duration_seconds):
        try:
            self.supabase.table('feature_usage').insert({
                'user_id': user_id,
                'feature_name': feature_name,
                'duration_seconds': duration_seconds
            }).execute()
        except Exception as e:
            logger.error(f"Error tracking feature usage: {str(e)}")

    def track_button_click(self, user_id, button_id, page_url):
        try:
            self.supabase.table('button_clicks').insert({
                'user_id': user_id,
                'button_id': button_id,
                'page_url': page_url
            }).execute()
        except Exception as e:
            logger.error(f"Error tracking button click: {str(e)}")

    def track_session(self, user_id, session_id, start_time, end_time=None):
        try:
            if end_time is None:
                end_time = datetime.now(timezone.utc)
            
            duration = int((end_time - start_time).total_seconds())
            
            self.supabase.table('session_activity').insert({
                'user_id': user_id,
                'session_id': session_id,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration
            }).execute()
        except Exception as e:
            logger.error(f"Error tracking session: {str(e)}")

    def track_page_view(self, user_id, session_id, page_url, view_duration):
        try:
            self.supabase.table('page_views').insert({
                'user_id': user_id,
                'session_id': session_id,
                'page_url': page_url,
                'view_duration_seconds': view_duration
            }).execute()
        except Exception as e:
            logger.error(f"Error tracking page view: {str(e)}")

    def update_user_metadata(self, user_id, metadata):
        try:
            self.supabase.table('user_metadata').upsert({
                'user_id': user_id,
                **metadata,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Error updating user metadata: {str(e)}")

    def track_error(self, user_id, session_id, error_type, error_message, stack_trace=None):
        try:
            self.supabase.table('error_logs').insert({
                'user_id': user_id,
                'session_id': session_id,
                'error_type': error_type,
                'error_message': error_message,
                'stack_trace': stack_trace
            }).execute()
        except Exception as e:
            logger.error(f"Error tracking error log: {str(e)}")

    def update_daily_metrics(self, user_id, metrics):
        try:
            date = datetime.now(timezone.utc).date().isoformat()
            
            # Use upsert with on_conflict parameter
            self.supabase.table('user_metrics_daily')\
                .upsert({
                    'user_id': user_id,
                    'date': date,
                    'api_calls_count': metrics.get('api_calls_count', 1),  # Default to 1 for new calls
                    'error_count': metrics.get('error_count', 0),
                    'feature_usage_count': metrics.get('feature_usage_count', 0),
                    'total_session_duration': metrics.get('total_session_duration', 0),
                    'active_minutes': metrics.get('active_minutes', 0)
                }, 
                on_conflict='user_id,date',  # Specify the unique constraint
                count='exact')\
                .execute()

        except Exception as e:
            logger.error(f"Error updating daily metrics: {str(e)}")
            # Log more details about the error
            logger.error(f"User ID: {user_id}")
            logger.error(f"Date: {date}")
            logger.error(f"Metrics: {metrics}") 