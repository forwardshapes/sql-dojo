from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from modules.exercises import get_exercise, get_all_exercises
from modules.auth import login_required, inject_user_context, create_session
from modules.security import sanitize_user_query, validate_sql_input
from modules.ai_validation import validate_sql_with_ai, parse_ai_response
from modules.rate_limiting import dynamic_rate_limit, get_rate_limit_info, handle_rate_limit_exceeded

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour"]
)


# Configure Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_PUBLISHABLE_KEY')

if not supabase_url or not supabase_key:
    raise ValueError("Missing required database configuration")

supabase: Client = create_client(supabase_url, supabase_key)

# Context processor to make user data available to all templates
@app.context_processor
def inject_user_data():
    current_user = inject_user_context()
    return {'current_user': current_user}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/exercises')
@login_required
def exercises():
    exercises = get_all_exercises()
    return render_template('exercises.html', exercises=exercises)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return render_template('index.html', error='Please enter both email and password')

    try:
        # Attempt to sign in with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if auth_response.user:
            # Check if user exists in our users table
            user_id = auth_response.user.id
            existing_user = supabase.table('users').select('*').eq('id', user_id).execute()

            if not existing_user.data:
                # User authenticated with Supabase but doesn't exist in our system
                return render_template('index.html', error='Account not found. Please contact support.')

            # Get user data for session caching
            user_record = existing_user.data[0]

            # Update last login for existing user
            supabase.table('users').update({
                'last_login': 'now()'
            }).eq('id', user_id).execute()

            # Create secure session with timeout tracking
            create_session(
                user_id=user_id,
                user_email=auth_response.user.email,
                username=user_record.get('username', 'User')
            )

            # Login successful - redirect to exercises
            return redirect(url_for('exercises'))
        else:
            return render_template('index.html', error='Invalid email or password')

    except Exception as e:
        # Handle authentication errors (invalid credentials, etc.)
        return render_template('index.html', error='Invalid email or password')

@app.route('/logout')
@login_required
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('index'))

@app.route('/exercise/<int:exercise_id>')
@login_required
def exercise(exercise_id):
    exercise_data = get_exercise(exercise_id)
    if not exercise_data:
        return "Exercise not found", 404

    return render_template('exercise.html', exercise=exercise_data, exercise_id=exercise_id)

@app.route('/api/rate-limit-info')
def rate_limit_info():
    """Get current user's rate limit information"""
    return get_rate_limit_info(request)

@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit exceeded error"""
    return handle_rate_limit_exceeded(e, request)

@app.route('/check-sql', methods=['POST'])
@login_required
@limiter.limit(dynamic_rate_limit)
def check_sql():
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        exercise_id = data.get('exercise_id', 1)
        
        if not user_query:
            return jsonify({
                'success': False,
                'message': 'Please enter a SQL query.'
            })
        
        # Step 1: Validate input for security threats
        is_valid, validation_message = validate_sql_input(user_query)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': validation_message
            })
        
        # Step 2: Sanitize the user query
        sanitized_query = sanitize_user_query(user_query)
        
        # Get exercise data
        exercise_data = get_exercise(exercise_id)
        if not exercise_data:
            return jsonify({
                'success': False,
                'message': 'Exercise not found.'
            })
        
        # Create validation prompt from exercise data with sanitized query
        prompt = exercise_data['validation_prompt'].format(user_query=sanitized_query)
        
        # Send to Gemini
        try:
            result_text = validate_sql_with_ai(prompt)
        except Exception as gemini_error:
            # Handle Gemini API errors (quota exceeded, network issues, etc.)
            return jsonify({
                'success': False,
                'message': 'Error validating query. Please try again later.'
            })
        
        # Step 3: Parse response with security validation
        parsed_response = parse_ai_response(result_text)
        
        return jsonify(parsed_response)
        
    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({
            'success': False,
            'message': 'Error validating query. Please try again later.'
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)