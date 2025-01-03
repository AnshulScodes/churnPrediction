import requests
import time
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = 'http://localhost:5000'

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def verify_supabase_data(user_id, table_name, expected_data):
    """Verify data was correctly stored in Supabase"""
    try:
        response = supabase.table(table_name)\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        if not response.data:
            print(f"❌ No data found in {table_name} for user {user_id}")
            return False
            
        actual_data = response.data[0]
        for key, value in expected_data.items():
            if key in actual_data and actual_data[key] != value:
                print(f"❌ Mismatch in {table_name}: expected {key}={value}, got {actual_data[key]}")
                return False
                
        print(f"✅ Data verified in {table_name}")
        print(f"   Stored data: {actual_data}")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying {table_name}: {str(e)}")
        return False

def test_all_functionality():
    print("\n=== Starting Comprehensive Test ===\n")
    
    # 1. Create a test user
    print("1. Testing User Creation...")
    test_email = f'test_{int(time.time())}@example.com'
    user_response = requests.post(f'{BASE_URL}/track/user', json={
        'email': test_email,
        'plan_type': 'pro',
        'status': 'active'
    })
    print(f"User Creation Response: {user_response.json()}")
    
    if not user_response.json().get('success'):
        print("❌ User creation failed!")
        return
        
    user_id = user_response.json()['user_id']
    print(f"✅ User created with ID: {user_id}")
    
    # Verify user in Supabase
    verify_supabase_data(user_id, 'users', {
        'email': test_email,
        'plan_type': 'pro',
        'status': 'active'
    })

    # 2. Track Engagement Metrics
    print("\n2. Testing Engagement Metrics...")
    engagement_metrics = {
        'last_active_date': datetime.now().isoformat(),
        'login_frequency': 5,
        'average_session_duration': 30,
        'feature_usage_frequency': 10
    }
    engagement_response = requests.post(f'{BASE_URL}/track/metrics', json={
        'user_id': user_id,
        'type': 'engagement',
        'metrics': engagement_metrics
    })
    print(f"Engagement Response: {engagement_response.json()}")
    verify_supabase_data(user_id, 'engagement_metrics', engagement_metrics)

    # 3. Track Subscription Metrics
    print("\n3. Testing Subscription Metrics...")
    subscription_metrics = {
        'billing_status': 'success',
        'cancellation_attempt': False,
        'churn_propensity_score': 0.1
    }
    subscription_response = requests.post(f'{BASE_URL}/track/metrics', json={
        'user_id': user_id,
        'type': 'subscription',
        'metrics': subscription_metrics
    })
    print(f"Subscription Response: {subscription_response.json()}")
    verify_supabase_data(user_id, 'subscription_metrics', subscription_metrics)

    # 4. Track Support Metrics
    print("\n4. Testing Support Metrics...")
    support_metrics = {
        'open_tickets': 2,
        'average_ticket_resolution_time': 48
    }
    support_response = requests.post(f'{BASE_URL}/track/metrics', json={
        'user_id': user_id,
        'type': 'support',
        'metrics': support_metrics
    })
    print(f"Support Response: {support_response.json()}")
    verify_supabase_data(user_id, 'support_metrics', support_metrics)

    # 5. Track Communication Metrics
    print("\n5. Testing Communication Metrics...")
    communication_metrics = {
        'email_open_rate': 0.75,
        'notification_click_rate': 0.45
    }
    communication_response = requests.post(f'{BASE_URL}/track/metrics', json={
        'user_id': user_id,
        'type': 'communication',
        'metrics': communication_metrics
    })
    print(f"Communication Response: {communication_response.json()}")
    verify_supabase_data(user_id, 'communication_metrics', communication_metrics)

    # 6. Track Behavioral Metrics
    print("\n6. Testing Behavioral Metrics...")
    behavioral_metrics = {
        'onboarding_completion': True,
        'usage_decline': 0.15
    }
    behavioral_response = requests.post(f'{BASE_URL}/track/metrics', json={
        'user_id': user_id,
        'type': 'behavioral',
        'metrics': behavioral_metrics
    })
    print(f"Behavioral Response: {behavioral_response.json()}")
    verify_supabase_data(user_id, 'behavioral_metrics', behavioral_metrics)

    # 7. Get All Metrics
    print("\n7. Testing Get All Metrics...")
    get_metrics_response = requests.get(f'{BASE_URL}/get/metrics/{user_id}')
    metrics_data = get_metrics_response.json()
    print("\nFinal Metrics for User:")
    for table, data in metrics_data['metrics'].items():
        print(f"\n{table.upper()}:")
        print(data)
    
    # 8. Verify all data in Supabase
    print("\n8. Final Supabase Verification...")
    all_tables = [
        'users',
        'engagement_metrics',
        'subscription_metrics',
        'support_metrics',
        'communication_metrics',
        'behavioral_metrics'
    ]
    
    verification_success = True
    for table in all_tables:
        response = supabase.table(table).select('*').eq('user_id', user_id).execute()
        if response.data:
            print(f"\n✅ {table.upper()} verified in Supabase:")
            print(response.data[0])
        else:
            print(f"\n❌ No data found in {table}")
            verification_success = False
    
    print("\n=== Test Complete ===")
    if verification_success:
        print("✅ All data verified in Supabase!")
    else:
        print("❌ Some data missing in Supabase")

if __name__ == "__main__":
    test_all_functionality() 