"""
Authentication service with integrated logging for SQL Dojo
"""
import os
from dataclasses import dataclass
from typing import Optional
from supabase import Client


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
        # Input validation
        if not email or not password:
            missing_fields = []
            if not email:
                missing_fields.append('email')
            if not password:
                missing_fields.append('password')

            return AuthResult(
                success=False,
                error_message='Please enter both email and password',
                error_type='validation_error'
            )

        try:
            return self._perform_supabase_authentication(email, password)

        except Exception as e:
            return AuthResult(
                success=False,
                error_message='Invalid email or password',
                error_type=type(e).__name__
            )

    def _perform_supabase_authentication(self, email: str, password: str) -> AuthResult:
        """Internal method to handle Supabase authentication flow"""

        # Attempt Supabase authentication
        auth_response = self.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not auth_response.user:
            return AuthResult(
                success=False,
                error_message='Invalid email or password',
                error_type='supabase_auth_failed'
            )

        # User authenticated with Supabase, now check our users table
        return self._verify_user_in_system(email, auth_response.user.id, auth_response.user.email)

    def _verify_user_in_system(self, email: str, user_id: str, auth_email: str) -> AuthResult:
        """Verify user exists in our users table and update last login"""

        # Check if user exists in our users table
        existing_user = self.supabase.table('users').select('*').eq('id', user_id).execute()

        if not existing_user.data:
            # User authenticated with Supabase but doesn't exist in our system
            return AuthResult(
                success=False,
                error_message='Account not found. Please contact support.',
                error_type='user_not_in_system'
            )

        # Get user data
        user_record = existing_user.data[0]
        username = user_record.get('username', 'User')

        # Update last login
        self._update_last_login(user_id)

        return AuthResult(
            success=True,
            user_id=user_id,
            username=username,
            email=auth_email
        )

    def _update_last_login(self, user_id: str):
        """Update the user's last login timestamp"""
        try:
            update_result = self.supabase.table('users').update({
                'last_login': 'now()'
            }).eq('id', user_id).execute()

        except Exception as e:
            # Silently fail - don't break authentication for last_login update failure
            pass