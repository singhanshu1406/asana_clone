"""
Configuration file for API Comparison
You can set your Asana API key here or use environment variables
"""
import os

# Asana API Key
# Option 1: Set it here directly (not recommended for production)
ASANA_API_KEY =  "2/1212431066135818/1212431067955184:01442df2fff4c053d4421defeaa312e5"

# Option 2: Read from .env file (if using python-dotenv)
# Uncomment the following lines if you install python-dotenv:
# from dotenv import load_dotenv
# load_dotenv()
# ASANA_API_KEY = os.getenv("ASANA_API_KEY", "")

# Local API configuration
LOCAL_API_URL = "http://localhost:8000/api/1.0"

# Asana API configuration
ASANA_API_URL = "https://app.asana.com/api/1.0"

# Database connection (for fetching test GIDs)
DATABASE_URL = "postgresql://anshuanshu:anshu1406@localhost:5432/asana"

