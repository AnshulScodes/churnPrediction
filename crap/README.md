# Churn Analytics Tracking System

A comprehensive system for tracking user behavior, engagement, and potential churn signals using Supabase as the backend database.

## Project Structure

project/
├── backend/
│ ├── app.py # Main Flask server
│ ├── test_all.py # Comprehensive testing suite
│ ├── test.py # PostHog integration test
│ ├── requirements.txt # Python dependencies
│ └── .env # Environment variables
└── frontend/
├── churn-tracker.js # JavaScript SDK
└── example.html # Example implementation


## Setup & Installation

1. Clone the repository
2. Install dependencies:

bash
cd backend
pip install -r requirements.txt

3. Set up environment variables in `.env`:

env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key
POSTHOG_API_KEY=your_posthog_key # Optional for PostHog integration
POSTHOG_HOST=https://app.posthog.com
DATABASE_URL=sqlite:///events.db
FLASK_SECRET_KEY=your_secret_key


## Core Components

### Backend (app.py)
- Flask server providing REST API endpoints
- Handles all metric tracking operations
- Endpoints:
  - `/track/user` - Create/update users
  - `/track/metrics` - Track various metric types
  - `/get/metrics/<user_id>` - Retrieve all metrics for a user
- Implements CORS for frontend integration
- Extensive logging for debugging

### Testing Suite (test_all.py)
- Comprehensive testing of all functionality
- Tests and verifies:
  1. User creation
  2. Engagement metrics
  3. Subscription metrics
  4. Support metrics
  5. Communication metrics
  6. Behavioral metrics
- Verifies data storage in Supabase
- Provides detailed test output with success/failure indicators

### Frontend SDK (churn-tracker.js)
JavaScript SDK for easy integration into web applications:
- Automatic session tracking
- User engagement monitoring
- Feature usage tracking
- Support ticket tracking
- Communication metrics
- Behavioral patterns

### Example Implementation (example.html)
- Demonstrates SDK usage
- Includes test buttons for:
  - Feature usage tracking
  - Support ticket creation
- Shows automatic session tracking

## Data Schema

### Users Table
- user_id (UUID, Primary Key)
- email
- plan_type
- sign_up_date
- status (active/inactive)

### Engagement Metrics
- user_id (Foreign Key)
- last_active_date
- login_frequency
- average_session_duration
- feature_usage_frequency

### Subscription Metrics
- user_id (Foreign Key)
- billing_status
- cancellation_attempt
- churn_propensity_score

### Support Metrics
- user_id (Foreign Key)
- open_tickets
- average_ticket_resolution_time

### Communication Metrics
- user_id (Foreign Key)
- email_open_rate
- notification_click_rate

### Behavioral Metrics
- user_id (Foreign Key)
- onboarding_completion
- usage_decline

## Usage

### 1. Start the Backend Server

bash
cd backend
python app.py


### 2. Run Tests
bash
python test_all.py

Expected output will show:
- User creation verification
- Metrics tracking confirmation
- Supabase data verification
- Success/failure indicators for each step

### 3. Implement in Your Web Application
html
<script src="path/to/churn-tracker.js"></script>
<script>
const tracker = new ChurnTracker('http://your-api-url');
// Initialize user
await tracker.initUser('user@example.com', 'pro');
// Track feature usage
await tracker.trackFeatureUsage('search');
// Track support ticket
await tracker.trackSupport(true);
</script>


## API Methods

### User Tracking
javascript
tracker.initUser(email, planType)


### Engagement Tracking
javascript
tracker.trackEngagement({
login_frequency: number,
average_session_duration: number,
feature_usage_frequency: number
})


### Subscription Tracking
javascript
tracker.trackSubscription(status, cancellationAttempted)


### Support Tracking
javascript
tracker.trackSupport(ticketOpened, ticketClosed, resolutionTime)


### Communication Tracking
javascript
tracker.trackCommunication(emailOpened, notificationClicked)


### Behavioral Tracking

## Debugging

1. Check Flask server logs for backend issues
2. Browser console for frontend SDK issues
3. Supabase dashboard for data verification
4. test_all.py output for comprehensive system testing

## Security Notes
- Keep your Supabase credentials secure
- Use environment variables for sensitive data
- Implement proper user authentication before deployment
- Consider rate limiting for production use

## Common Issues & Solutions

1. CORS Errors
   - Ensure CORS is properly configured in Flask
   - Check API URL in frontend configuration

2. Database Errors
   - Verify Supabase credentials
   - Check table structure matches schema
   - Ensure proper foreign key relationships

3. Tracking Issues
   - Verify user initialization
   - Check network requests in browser console
   - Ensure proper event triggering

## Future Improvements
1. Add user authentication
2. Implement rate limiting
3. Add batch processing for metrics
4. Create dashboard for metrics visualization
5. Add real-time notifications for high churn risk

## Contributing
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License
MIT License

## Support
For issues and feature requests, please create an issue in the repository.

This README provides a comprehensive guide to understanding, setting up, and using the churn tracking system. Let me know if you need any specific section expanded or clarified!
