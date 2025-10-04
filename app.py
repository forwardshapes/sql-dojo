from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv
from modules.exercises import get_exercise, get_all_exercises, build_validation_prompt
from modules.security import sanitize_user_query, validate_sql_input, MAX_REQUEST_SIZE
from modules.ai_validation import validate_sql_with_ai, parse_ai_response
from modules.rate_limiting import dynamic_rate_limit, get_rate_limit_info, handle_rate_limit_exceeded

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour"]
)


@app.route('/')
def index():
    exercises = get_all_exercises()
    return render_template('exercises.html', exercises=exercises)

@app.route('/exercise/<int:exercise_id>')
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
@limiter.limit(dynamic_rate_limit)
def check_sql():
    try:
        # Check request size early to prevent large payloads
        if request.content_length and request.content_length > MAX_REQUEST_SIZE:
            return jsonify({
                'success': False,
                'message': 'Request too large'
            }), 413
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

        # Build validation prompt from exercise data with sanitized query
        prompt_template = build_validation_prompt(exercise_data)
        prompt = prompt_template.format(user_query=sanitized_query)

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
    # Cloud Run provides PORT environment variable, use 5000 for local dev
    port = int(os.getenv('PORT', 5000))
    # Enable debug mode for local development or when FLASK_ENV=development
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)