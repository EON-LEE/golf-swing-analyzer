import unittest
from email_validator import validate_email

class TestEmailValidator(unittest.TestCase):
    
    def test_valid_emails(self):
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        for email in valid_emails:
            self.assertTrue(validate_email(email))
    
    def test_invalid_emails(self):
        invalid_emails = [
            "invalid.email",
            "@example.com",
            "test@",
            "test@.com",
            "",
            None,
            123
        ]
        for email in invalid_emails:
            self.assertFalse(validate_email(email))

if __name__ == '__main__':
    unittest.main()
