import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_base_url():
    env = os.environ.get('ENV', 'development')

    if env == 'production':
        # Read the production base URL from .env file
        return os.environ.get('PRODUCTION_BASE_URL', 'https://your-production-domain.com')
    else:
        # Assuming the application is running on localhost:5000 during development
        return os.environ.get('DEVELOPMENT_BASE_URL', 'http://localhost:5000')
