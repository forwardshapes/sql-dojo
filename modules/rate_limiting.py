"""
Rate limiting functions for SQL Dojo - User tier detection and rate limits
"""
from flask import jsonify


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


def dynamic_rate_limit(request):
    """Dynamic rate limit based on user tier"""
    user_tier = get_user_tier(request)
    limits = get_rate_limits_for_user(user_tier)

    return [
        f"{limits['per_minute']} per minute",
        f"{limits['per_hour']} per hour",
        f"{limits['per_day']} per day"
    ]


def get_rate_limit_info(request):
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


def handle_rate_limit_exceeded(e, request):
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