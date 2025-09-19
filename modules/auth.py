"""
Authentication and authorization functions for SQL Dojo
"""
from functools import wraps
from flask import session, redirect, url_for
from datetime import datetime, timedelta


def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('index'))

        # Check session timeout (2 hours)
        if is_session_expired():
            session.clear()
            return redirect(url_for('index'))

        # Refresh session timestamp
        session['last_activity'] = datetime.now().isoformat()
        return f(*args, **kwargs)
    return decorated_function


def is_session_expired():
    """Check if session has expired (2 hour timeout)"""
    last_activity = session.get('last_activity')
    if not last_activity:
        return True

    try:
        last_activity_time = datetime.fromisoformat(last_activity)
        return datetime.now() - last_activity_time > timedelta(hours=2)
    except (ValueError, TypeError):
        return True


def create_session(user_id, user_email, username):
    """Create a new user session with timeout tracking"""
    # Regenerate session ID for security
    session.permanent = True

    # Store user data
    session['user_id'] = user_id
    session['user_email'] = user_email
    session['username'] = username
    session['logged_in'] = True
    session['last_activity'] = datetime.now().isoformat()



def inject_user_context():
    """Get current user data for template context"""
    if session.get('logged_in'):
        # Return user data from session (will be implemented in step 2)
        return {
            'username': session.get('username', 'User'),
            'email': session.get('user_email', ''),
            'avatar_letter': session.get('username', 'U')[0].upper()
        }
    return None