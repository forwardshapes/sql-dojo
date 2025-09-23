"""
AI validation functions for SQL Dojo - Gemini integration and response parsing
"""
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv
load_dotenv()

# Validate and configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is required")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-lite')


def validate_sql_with_ai(prompt):
    """Send SQL validation prompt to Gemini AI with timeout"""

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

        return response.text.strip() if response.text else ""

    except Exception as gemini_error:
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