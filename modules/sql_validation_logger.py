"""
SQL validation logging utilities for debugging production issues
"""
import os
from typing import Optional, Dict, Any
from modules.logging_config import get_app_logger


def log_sql_validation_event(event: str, request_id: str, **kwargs):
    """
    Log SQL validation events with structured data

    Args:
        event: Event type (e.g., 'request_start', 'gemini_api_start', 'gemini_api_error')
        request_id: Unique request identifier for tracking
        **kwargs: Additional context data
    """
    # Only log if GEMINI_DEBUG_ENABLED is true
    if not os.getenv('GEMINI_DEBUG_ENABLED', 'false').lower() == 'true':
        return

    logger = get_app_logger()

    extra_data = {
        'event_type': 'sql_validation',
        'event': event,
        'request_id': request_id,
        **kwargs
    }

    logger.info(f"SQL validation: {event}", extra={'extra_data': extra_data})


def log_sql_validation_error(event: str, request_id: str, error: Exception, **kwargs):
    """
    Log SQL validation errors with structured data

    Args:
        event: Error event type (e.g., 'gemini_api_error', 'unexpected_error')
        request_id: Unique request identifier
        error: Exception that occurred
        **kwargs: Additional context data
    """
    # Only log if GEMINI_DEBUG_ENABLED is true
    if not os.getenv('GEMINI_DEBUG_ENABLED', 'false').lower() == 'true':
        return

    logger = get_app_logger()

    extra_data = {
        'event_type': 'sql_validation',
        'event': event,
        'request_id': request_id,
        'error_type': type(error).__name__,
        'error_message': str(error),
        **kwargs
    }

    logger.error(f"SQL validation error: {event}", extra={'extra_data': extra_data}, exc_info=True)


def generate_request_id(request) -> str:
    """Generate a unique request ID for tracking"""
    import hashlib

    # Create a simple hash-based ID from request data
    data = f"{request.remote_addr}{request.get_json()}"
    return f"req_{hash(data) % 10000:04d}"


class SQLValidationLogger:
    """Context manager for tracking SQL validation requests"""

    def __init__(self, request):
        self.request_id = generate_request_id(request)
        self.request = request

    def __enter__(self):
        log_sql_validation_event(
            'request_start',
            self.request_id,
            user_ip=self.request.remote_addr
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            log_sql_validation_error(
                'request_failed',
                self.request_id,
                exc_val,
                completed=False
            )
        else:
            log_sql_validation_event(
                'request_complete',
                self.request_id,
                completed=True
            )

    def log_step(self, step: str, **kwargs):
        """Log a step in the validation process"""
        log_sql_validation_event(step, self.request_id, **kwargs)

    def log_error(self, step: str, error: Exception, **kwargs):
        """Log an error in the validation process"""
        log_sql_validation_error(step, self.request_id, error, **kwargs)