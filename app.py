from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv
from exercises import get_exercise, get_all_exercises

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour"]
)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

# User tier detection and rate limiting
def get_user_tier(request):
    """Determine if user is paid or free based on headers/auth"""
    # For now, assume all users are free
    # In the future, you could check:
    # - API key in headers
    # - JWT token with subscription info
    # - Database lookup based on user ID
    # - Premium domain/referrer check
    
    # Example: Check for premium API key in headers
    api_key = request.headers.get('X-API-Key')
    if api_key and api_key.startswith('premium_'):
        return 'paid'
    
    # Example: Check for premium cookie/session
    premium_cookie = request.cookies.get('premium_user')
    if premium_cookie == 'true':
        return 'paid'
    
    return 'free'

def get_rate_limits_for_user(user_tier):
    """Get rate limits based on user tier"""
    if user_tier == 'paid':
        return {
            'per_minute': 15,
            'per_hour': 200, 
            'per_day': 1000
        }
    else:  # free user
        return {
            'per_minute': 5,
            'per_hour': 30,
            'per_day': 100
        }

# Security functions for prompt injection protection
def sanitize_user_query(query):
    """Sanitize user input to prevent prompt injection attacks"""
    if not query:
        return query
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'ignore\s+.*?instructions',
        r'forget\s+.*?previous',
        r'you\s+are\s+now',
        r'act\s+as',
        r'pretend\s+to\s+be',
        r'roleplay\s+as',
        r'system\s*:',
        r'assistant\s*:',
        r'user\s*:'
    ]
    
    for pattern in dangerous_patterns:
        query = re.sub(pattern, '', query, flags=re.IGNORECASE)
    
    # Limit length to reasonable SQL query size
    if len(query) > 500:
        query = query[:500]
    
    return query.strip()

def validate_sql_input(user_query):
    """Basic validation to check for prompt injection attempts"""
    if not user_query or not user_query.strip():
        return False, "Query cannot be empty"
    
    # Check for common prompt injection patterns
    dangerous_patterns = [
        r'ignore.*instructions',
        r'forget.*previous',
        r'you are now',
        r'act as',
        r'pretend',
        r'roleplay',
        r'system\s*:',
        r'assistant\s*:',
        r'user\s*:',
        r'---+',  # Common delimiter used in prompt injections
        r'```',   # Code blocks that might contain instructions
        r'<.*>',  # HTML-like tags that might contain instructions
    ]
    
    query_lower = user_query.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, query_lower):
            return False, "Input answer is not valid"
    
    # Check basic SQL structure for beginner exercises
    if not re.match(r'^\s*SELECT\s+', user_query, re.IGNORECASE):
        return False, "Query must start with SELECT statement"
    
    # Check for reasonable length
    if len(user_query) > 500:
        return False, "Query is too long (maximum 500 characters)"
    
    return True, "Valid"

def parse_ai_response(response):
    """Parse and validate AI response format with fallback handling"""
    if not response or not isinstance(response, str):
        return {
            'success': False,
            'correct': False,
            'message': 'Invalid response from validation system'
        }
    
    response = response.strip()
    
    # Check if response follows expected format
    if not response.startswith(('CORRECT:', 'INCORRECT:')):
        return {
            'success': False,
            'correct': False,
            'message': 'Unable to validate query at this time'
        }
    
    # Parse the response
    is_correct = response.startswith('CORRECT:')
    message = response.split(':', 1)[1].strip() if ':' in response else response
    
    # Add celebratory emoji to correct answers
    if is_correct and message:
        message = f'🎉 {message}'
    
    # Sanitize the message to prevent any injected content from being returned
    message = message[:200]  # Limit message length
    
    return {
        'success': True,
        'correct': is_correct,
        'message': message
    }

@app.route('/')
def index():
    exercises = get_all_exercises()
    return render_template('index.html', exercises=exercises)

@app.route('/exercise/<int:exercise_id>')
def exercise(exercise_id):
    exercise_data = get_exercise(exercise_id)
    if not exercise_data:
        return "Exercise not found", 404
    
    return render_template('exercise.html', exercise=exercise_data, exercise_id=exercise_id)

@app.route('/api/rate-limit-info')
def rate_limit_info():
    """Get current user's rate limit information"""
    user_tier = get_user_tier(request)
    limits = get_rate_limits_for_user(user_tier)
    
    return jsonify({
        'user_tier': user_tier,
        'limits': {
            'per_minute': limits['per_minute'],
            'per_hour': limits['per_hour'],
            'per_day': limits['per_day']
        }
    })

@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit exceeded error"""
    user_tier = get_user_tier(request)
    limits = get_rate_limits_for_user(user_tier)
    
    return jsonify({
        'success': False,
        'message': f'Rate limit exceeded. {user_tier.title()} users are limited to {limits["per_minute"]} queries per minute, {limits["per_hour"]} per hour, and {limits["per_day"]} per day.',
        'rate_limit_info': {
            'user_tier': user_tier,
            'limits': limits,
            'retry_after': getattr(e, 'retry_after', None)
        }
    }), 429

def dynamic_rate_limit():
    """Dynamic rate limit based on user tier"""
    user_tier = get_user_tier(request)
    limits = get_rate_limits_for_user(user_tier)
    
    return [
        f"{limits['per_minute']} per minute",
        f"{limits['per_hour']} per hour", 
        f"{limits['per_day']} per day"
    ]

@app.route('/check-sql', methods=['POST'])
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
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Step 3: Parse response with security validation
        parsed_response = parse_ai_response(result_text)
        
        return jsonify(parsed_response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error validating query: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)