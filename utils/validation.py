import re

def is_valid_email(email: str) -> bool:
    """
    Validate email format using regex pattern.
    
    Args:
        email: String to validate
        
    Returns:
        bool: True if valid email format, False otherwise
    """
    if not isinstance(email, str) or not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
