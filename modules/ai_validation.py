"""
AI validation functions for SQL Dojo - Gemini integration and response parsing
"""
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv
from modules.logging_config import get_app_logger

load_dotenv()

logger = get_app_logger()

# Validate and configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')

# Log environment validation if debug is enabled
if os.getenv('GEMINI_DEBUG_ENABLED', 'false').lower() == 'true':
    logger.info("Gemini environment validation", extra={'extra_data': {
        'event_type': 'gemini_setup',
        'event': 'environment_validation',
        'api_key_present': bool(api_key),
        'api_key_length': len(api_key) if api_key else 0,
        'api_key_prefix': api_key[:8] + '...' if api_key and len(api_key) > 8 else '[MISSING]'
    }})

if not api_key:
    logger.error("Missing GEMINI_API_KEY environment variable", extra={'extra_data': {
        'event_type': 'gemini_setup',
        'event': 'missing_api_key'
    }})
    raise ValueError("GEMINI_API_KEY environment variable is required")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-lite')


def validate_sql_with_ai(prompt):
    """Send SQL validation prompt to Gemini AI with detailed logging and timeout"""
    request_id = f"gemini_{hash(prompt) % 10000:04d}"

    # Log request start if debug enabled
    if os.getenv('GEMINI_DEBUG_ENABLED', 'false').lower() == 'true':
        logger.info("Gemini API request starting", extra={'extra_data': {
            'event_type': 'gemini_api',
            'event': 'request_start',
            'request_id': request_id,
            'prompt_length': len(prompt),
            'model': 'gemini-2.0-flash-lite'
        }})

    start_time = time.time()

    try:
        # Add timeout to prevent hanging
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                # Add basic safeguards
                max_output_tokens=1000,
                temperature=0.1,
            ),
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        )

        duration = time.time() - start_time

        # Log successful response
        if os.getenv('GEMINI_DEBUG_ENABLED', 'false').lower() == 'true':
            logger.info("Gemini API request completed", extra={'extra_data': {
                'event_type': 'gemini_api',
                'event': 'request_success',
                'request_id': request_id,
                'duration_seconds': round(duration, 3),
                'response_length': len(response.text) if response.text else 0,
                'response_preview': response.text[:100] + '...' if response.text and len(response.text) > 100 else response.text
            }})

        return response.text.strip() if response.text else ""

    except Exception as gemini_error:
        duration = time.time() - start_time

        # Log detailed error information
        if os.getenv('GEMINI_DEBUG_ENABLED', 'false').lower() == 'true':
            logger.error("Gemini API request failed", extra={'extra_data': {
                'event_type': 'gemini_api',
                'event': 'request_error',
                'request_id': request_id,
                'duration_seconds': round(duration, 3),
                'error_type': type(gemini_error).__name__,
                'error_message': str(gemini_error),
                'error_details': str(gemini_error)
            }}, exc_info=True)

        # Handle Gemini API errors (quota exceeded, network issues, etc.)
        raise Exception(f"Gemini API error: {type(gemini_error).__name__} - {str(gemini_error)}")


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
    message = message[:300]  # Limit message length

    return {
        'success': True,
        'correct': is_correct,
        'message': message
    }