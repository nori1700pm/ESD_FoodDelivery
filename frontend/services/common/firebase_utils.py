import os
import json

def get_firebase_credentials():
    """
    Get Firebase credentials or return a mock in development environment
    """
    firebase_config = os.environ.get('FIREBASE_CONFIG', '{}')
    try:
        config_dict = json.loads(firebase_config)
        
        # Check if we're dealing with placeholder credentials
        if "YOUR_ACTUAL_PRIVATE_KEY_HERE" in config_dict.get('private_key', ''):
            print("Using mock Firebase credentials for development")
            # Return minimal mock structure for development
            return {
                "type": "service_account",
                "project_id": "dev-project",
                "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC+175ttvJZCgDd\neoGkOhYpJ+XXBGBuYUNOXgKiLcKP6yZ2mwN8LS8jxGzsLVDuS06x7rQNQZEGPTuT\n9UniPyrA9Z1Q9slbtJsWZpXZJHbiBJqu6Xj9iTT9zuYGjj3F+Rrv7BVwoAvhAV+Q\nhQkJw960Ekg66uCwoTgrJ0O9sUcbmCuIrCYGLAUIBQYcHQwT95ae3g/Iqu7nNNpw\nYJAVPn7zdzjnpqMwFJJN0QZjDbtcDHLHgIYKRO5maEQ1vRIKRkxljUsVs7viam1G\nFjIY5JbI/U5Y7p1eSjQHCgPyxpK9Y8hx7GwKm/4ldCXzC6yK8qUNRu7kPJJBKPwi\nMOXDs3RJAgMBAAECggEAWHGOISE8+xJkt7Fwr+OKvW89/xCzn/u5vlcyZ0QEQpfW\nfGu6+8WPBL//RJuVCwzXM1RZN+AgzEPxHPJf+2ZxV+oMtea5UXX+WDEjYLbaSQl9\nt2K9QnNbSJgy51dwqeR31FNbWJjfTHRLQElMZ/NT1Me4aEB2hS6jFXMYWyz9zjdk\nXjT11LgRN7VDi11HwFsLNXnu3kYPOsHHHXpXWG0a29qI9L63sbCEyIEkX6UsDcKo\nUR9cMzAzEV3zB0F+NmvJmmHKz6EaOk4yn/aLZjjOib4vPdZ1e8oNlkuWJZmTjxX6\nB2NL3v8e3s9kjPg3r3fCX3FRKBJFGVyHOgJ4mrISLQKBgQDtxDdKTvULvIbgHOf/\n-----END PRIVATE KEY-----\n",
                "client_email": "dev-service-account@dev-project.iam.gserviceaccount.com",
                "client_id": "000000000000000000000",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dev-service-account%40dev-project.iam.gserviceaccount.com",
                "universe_domain": "googleapis.com"
            }
        return config_dict
    except json.JSONDecodeError:
        print("Invalid Firebase configuration JSON")
        return {}
