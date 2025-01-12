from flask import Flask
from supabase import create_client, Client, supabase
from flask import send_json_response

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

def init_tables():
    """Ensure tables exist"""
    tables = ['users', 'engagement_metrics', 'feature_analytics', 'api_keys']
    for table in tables:
        try:
            supabase.table(table).select('id').limit(1).execute()
        except Exception as e:
            print(f"Table {table} check failed: {e}")

def do_GET(self):
    if self.path == '/health':
        send_json_response(self, {"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)