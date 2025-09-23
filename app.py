from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from modules.exercises import get_exercise, get_all_exercises, build_validation_prompt
from modules.auth import login_required, inject_user_context, create_session
from modules.security import sanitize_user_query, validate_sql_input
from modules.ai_validation import validate_sql_with_ai, parse_ai_response
from modules.rate_limiting import dynamic_rate_limit, get_rate_limit_info, handle_rate_limit_exceeded
from modules.logging_config import setup_logging, get_auth_logger, get_app_logger, log_auth_event, log_supabase_event, log_error_with_context
from modules.sql_validation_logger import SQLValidationLogger
from modules.auth_service import AuthenticationService

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
CORS(app)

# Initialize logging after Flask app creation
setup_logging()
auth_logger = get_auth_logger()
app_logger = get_app_logger()

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

# Initialize authentication service
auth_service = AuthenticationService(supabase)

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

    # Use authentication service for clean, logged authentication
    auth_result = auth_service.authenticate_user(
        email=email,
        password=password,
        user_agent=request.headers.get('User-Agent', ''),
        ip_address=request.remote_addr
    )

    if auth_result.success:
        # Create secure session with timeout tracking
        create_session(
            user_id=auth_result.user_id,
            user_email=auth_result.email,
            username=auth_result.username
        )
        return redirect(url_for('exercises'))
    else:
        return render_template('index.html', error=auth_result.error_message)

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
    with SQLValidationLogger(request) as logger:
        try:
            data = request.get_json()
            user_query = data.get('query', '').strip()
            exercise_id = data.get('exercise_id', 1)

            logger.log_step('data_parsed', exercise_id=exercise_id, query_length=len(user_query))

            if not user_query:
                logger.log_step('validation_failed', reason='empty_query')
                return jsonify({
                    'success': False,
                    'message': 'Please enter a SQL query.'
                })

            # Step 1: Validate input for security threats
            logger.log_step('security_validation_start')
            is_valid, validation_message = validate_sql_input(user_query)
            if not is_valid:
                logger.log_step('security_validation_failed', validation_message=validation_message)
                return jsonify({
                    'success': False,
                    'message': validation_message
                })

            # Step 2: Sanitize the user query
            logger.log_step('query_sanitization')
            sanitized_query = sanitize_user_query(user_query)

            # Get exercise data
            logger.log_step('exercise_data_retrieval', exercise_id=exercise_id)
            exercise_data = get_exercise(exercise_id)
            if not exercise_data:
                logger.log_step('exercise_not_found', exercise_id=exercise_id)
                return jsonify({
                    'success': False,
                    'message': 'Exercise not found.'
                })

            # Build validation prompt from exercise data with sanitized query
            logger.log_step('prompt_building')
            prompt_template = build_validation_prompt(exercise_data)
            prompt = prompt_template.format(user_query=sanitized_query)

            # Send to Gemini
            logger.log_step('gemini_api_start', prompt_length=len(prompt))
            try:
                result_text = validate_sql_with_ai(prompt)
                logger.log_step('gemini_api_success', response_length=len(result_text) if result_text else 0)
            except Exception as gemini_error:
                # Handle Gemini API errors (quota exceeded, network issues, etc.)
                logger.log_error('gemini_api_error', gemini_error)
                return jsonify({
                    'success': False,
                    'message': 'Error validating query. Please try again later.'
                })

            # Step 3: Parse response with security validation
            logger.log_step('response_parsing')
            parsed_response = parse_ai_response(result_text)

            logger.log_step('request_complete',
                          success=parsed_response.get('success', False),
                          correct=parsed_response.get('correct', False))

            return jsonify(parsed_response)

        except Exception as e:
            # Handle any other unexpected errors
            logger.log_error('unexpected_error', e)
            return jsonify({
                'success': False,
                'message': 'Error validating query. Please try again later.'
            })

if __name__ == '__main__':
    # Cloud Run provides PORT environment variable, use 5000 for local dev
    port = int(os.getenv('PORT', 5000))
    # Enable debug mode for local development or when FLASK_ENV=development
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)