"""
Security functions for SQL Dojo - Input validation and sanitization
"""
import re


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