import re

def validate_email(email):
    """Validate email address format.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False if invalid
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
