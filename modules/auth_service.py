"""
Authentication service with integrated logging for SQL Dojo
"""
import os
from dataclasses import dataclass
from typing import Optional
from supabase import Client
from modules.logging_config import get_auth_logger, log_auth_event, log_supabase_event, log_error_with_context


@dataclass
class AuthResult:
    """Result of an authentication attempt"""
    success: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None


class AuthenticationService:
    """Handles user authentication with integrated logging"""

    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.logger = get_auth_logger()
        self.debug_enabled = os.getenv('AUTH_DEBUG_ENABLED', 'false').lower() == 'true'

    def authenticate_user(self, email: str, password: str, user_agent: str = '', ip_address: str = '') -> AuthResult:
        """
        Authenticate user with email and password

        Args:
            email: User email address
            password: User password
            user_agent: Request user agent (for logging)
            ip_address: Request IP address (for logging)

        Returns:
            AuthResult with success status and user data or error info
        """
        # Always log authentication attempts (security monitoring)
        log_auth_event(self.logger, 'login_attempt',
                       email=email,
                       has_password=bool(password),
                       user_agent=user_agent,
                       ip_address=ip_address)

        # Input validation
        if not email or not password:
            missing_fields = []
            if not email:
                missing_fields.append('email')
            if not password:
                missing_fields.append('password')

            log_auth_event(self.logger, 'login_validation_failed',
                           email=email,
                           missing_fields=missing_fields)

            return AuthResult(
                success=False,
                error_message='Please enter both email and password',
                error_type='validation_error'
            )

        try:
            return self._perform_supabase_authentication(email, password)

        except Exception as e:
            # Always log authentication exceptions (security monitoring)
            log_error_with_context(self.logger, e, {
                'context': 'authentication_service',
                'email': email,
                'error_type': type(e).__name__,
                'error_message': str(e)
            })

            log_auth_event(self.logger, 'login_exception',
                           email=email,
                           error_type=type(e).__name__,
                           error_message=str(e))

            return AuthResult(
                success=False,
                error_message='Invalid email or password',
                error_type=type(e).__name__
            )

    def _perform_supabase_authentication(self, email: str, password: str) -> AuthResult:
        """Internal method to handle Supabase authentication flow"""

        # Debug logging - detailed step tracking
        if self.debug_enabled:
            log_auth_event(self.logger, 'supabase_auth_request_start', email=email)

        # Attempt Supabase authentication
        auth_response = self.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if self.debug_enabled:
            log_auth_event(self.logger, 'supabase_auth_response_received',
                           email=email,
                           has_user=bool(auth_response.user),
                           user_id=auth_response.user.id if auth_response.user else None)

        if not auth_response.user:
            log_auth_event(self.logger, 'login_failed_no_user_in_response',
                           email=email,
                           auth_response_type=type(auth_response).__name__)

            return AuthResult(
                success=False,
                error_message='Invalid email or password',
                error_type='supabase_auth_failed'
            )

        # User authenticated with Supabase, now check our users table
        return self._verify_user_in_system(email, auth_response.user.id, auth_response.user.email)

    def _verify_user_in_system(self, email: str, user_id: str, auth_email: str) -> AuthResult:
        """Verify user exists in our users table and update last login"""

        if self.debug_enabled:
            log_supabase_event(self.logger, 'user_table_query_start',
                               user_id=user_id,
                               table='users')

        # Check if user exists in our users table
        existing_user = self.supabase.table('users').select('*').eq('id', user_id).execute()

        if self.debug_enabled:
            log_supabase_event(self.logger, 'user_table_query_complete',
                               user_id=user_id,
                               table='users',
                               found_records=len(existing_user.data) if existing_user.data else 0,
                               has_data=bool(existing_user.data))

        if not existing_user.data:
            # User authenticated with Supabase but doesn't exist in our system
            log_auth_event(self.logger, 'login_failed_user_not_in_system',
                           email=email,
                           user_id=user_id)

            return AuthResult(
                success=False,
                error_message='Account not found. Please contact support.',
                error_type='user_not_in_system'
            )

        # Get user data
        user_record = existing_user.data[0]
        username = user_record.get('username', 'User')

        if self.debug_enabled:
            log_auth_event(self.logger, 'user_record_retrieved',
                           user_id=user_id,
                           username=username)

        # Update last login
        self._update_last_login(user_id)

        # Success! Log the successful authentication
        log_auth_event(self.logger, 'login_success',
                       email=email,
                       user_id=user_id,
                       username=username)

        return AuthResult(
            success=True,
            user_id=user_id,
            username=username,
            email=auth_email
        )

    def _update_last_login(self, user_id: str):
        """Update the user's last login timestamp"""
        try:
            if self.debug_enabled:
                log_supabase_event(self.logger, 'update_last_login_start', user_id=user_id)

            update_result = self.supabase.table('users').update({
                'last_login': 'now()'
            }).eq('id', user_id).execute()

            if self.debug_enabled:
                log_supabase_event(self.logger, 'update_last_login_complete',
                                   user_id=user_id,
                                   success=bool(update_result))

        except Exception as e:
            # Log but don't fail authentication for last_login update failure
            log_error_with_context(self.logger, e, {
                'context': 'update_last_login',
                'user_id': user_id
            })