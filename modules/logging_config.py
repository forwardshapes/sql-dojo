"""
Enhanced logging configuration for SQL Dojo with Google Cloud Run compatibility
"""
import logging
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any


class CloudRunJsonFormatter(logging.Formatter):
    """JSON formatter optimized for Google Cloud Logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON for Cloud Logging"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'severity': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Pretty print for local development, compact for production
        if os.getenv('FLASK_ENV') == 'development' or not os.getenv('PORT'):
            return json.dumps(log_entry, indent=2)
        else:
            return json.dumps(log_entry)


def setup_logging():
    """Configure logging for the application"""
    # Get log level from environment (default to INFO)
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    # Only configure our app loggers, not the root logger
    # This prevents interference with Flask's startup messages

    # Configure our app-specific loggers
    for logger_name in ['sql_dojo.auth', 'sql_dojo.app']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Remove any existing handlers
        logger.handlers.clear()

        # Create console handler with JSON formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CloudRunJsonFormatter())
        logger.addHandler(console_handler)

        # Prevent propagation to root logger to avoid double logging
        logger.propagate = False

    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


def get_auth_logger():
    """Get logger specifically for authentication events"""
    return logging.getLogger('sql_dojo.auth')


def get_app_logger():
    """Get logger for general application events"""
    return logging.getLogger('sql_dojo.app')


def log_auth_event(logger: logging.Logger, event: str, **kwargs):
    """
    Log authentication event with structured data

    Args:
        logger: Logger instance
        event: Event type (e.g., 'login_attempt', 'login_success', 'login_failure')
        **kwargs: Additional structured data to log
    """
    # Check if auth debug logging is enabled
    if not os.getenv('AUTH_DEBUG_ENABLED', 'false').lower() == 'true':
        return

    # Sanitize sensitive data
    sanitized_data = _sanitize_auth_data(kwargs)

    extra_data = {
        'event_type': 'authentication',
        'event': event,
        **sanitized_data
    }

    logger.info(f"Auth event: {event}", extra={'extra_data': extra_data})


def log_supabase_event(logger: logging.Logger, event: str, **kwargs):
    """
    Log Supabase-related events with structured data

    Args:
        logger: Logger instance
        event: Event type (e.g., 'client_init', 'auth_request', 'table_query')
        **kwargs: Additional structured data to log
    """
    # Check if auth debug logging is enabled
    if not os.getenv('AUTH_DEBUG_ENABLED', 'false').lower() == 'true':
        return

    # Sanitize sensitive data
    sanitized_data = _sanitize_supabase_data(kwargs)

    extra_data = {
        'event_type': 'supabase',
        'event': event,
        **sanitized_data
    }

    logger.info(f"Supabase event: {event}", extra={'extra_data': extra_data})


def _sanitize_auth_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove or mask sensitive authentication data"""
    sanitized = {}

    for key, value in data.items():
        if key.lower() in ['password', 'token', 'secret', 'key']:
            sanitized[key] = '[REDACTED]'
        elif key.lower() == 'email':
            # Hash email for privacy while maintaining debuggability
            sanitized[key] = f"user_{hash(str(value)) % 10000:04d}"
        elif key.lower() == 'user_id':
            # Keep first 8 chars of user_id for debugging
            sanitized[key] = str(value)[:8] + '...' if len(str(value)) > 8 else str(value)
        else:
            sanitized[key] = value

    return sanitized


def _sanitize_supabase_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove or mask sensitive Supabase data"""
    sanitized = {}

    for key, value in data.items():
        if key.lower() in ['api_key', 'secret_key', 'access_token', 'refresh_token']:
            sanitized[key] = '[REDACTED]'
        elif key.lower() == 'supabase_url':
            # Keep URL structure but mask project ID
            if isinstance(value, str) and 'supabase.co' in value:
                sanitized[key] = value.replace(value.split('.')[0].split('//')[-1], 'project_***')
            else:
                sanitized[key] = str(value)
        else:
            sanitized[key] = value

    return sanitized


def log_error_with_context(logger: logging.Logger, error: Exception, context: Dict[str, Any] = None):
    """
    Log an error with additional context information

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context data
    """
    context = context or {}

    extra_data = {
        'event_type': 'error',
        'error_type': type(error).__name__,
        'error_message': str(error),
        **context
    }

    logger.error(f"Error occurred: {type(error).__name__}",
                extra={'extra_data': extra_data},
                exc_info=True)