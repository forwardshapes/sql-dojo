"""
AI validation functions for SQL Dojo - Gemini integration and response parsing
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-lite')


def validate_sql_with_ai(prompt):
    """Send SQL validation prompt to Gemini AI"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as gemini_error:
        # Handle Gemini API errors (quota exceeded, network issues, etc.)
        raise Exception("Error validating query. Please try again later.")


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