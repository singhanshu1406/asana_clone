# How to Set Asana API Key

You have **3 options** to set your Asana API key for API comparison testing:

## Option 1: Environment Variable (Recommended) ✅

**Temporary (current session only):**
```bash
export ASANA_API_KEY="your_asana_api_key_here"
python test_api_comparison.py
```

**Permanent (add to ~/.zshrc or ~/.bashrc):**
```bash
echo 'export ASANA_API_KEY="your_asana_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

## Option 2: Configuration File

Edit `config.py` and set the API key directly:

```python
ASANA_API_KEY = "your_asana_api_key_here"
```

**Note:** Be careful not to commit this file to version control if it contains your key!

## Option 3: Direct in Script

Edit `test_api_comparison.py` and modify the main function:

```python
def main():
    tester = EnhancedAPITester(asana_api_key="your_asana_api_key_here")
    # ... rest of code
```

## Getting Your Asana API Key

1. Go to https://app.asana.com/0/my-apps
2. Click "Create New App" or select an existing app
3. Copy your "Personal Access Token" or "API Key"
4. Use it in one of the methods above

## Verify It's Set

Run this to check:
```bash
python -c "import os; print('API Key set:', bool(os.getenv('ASANA_API_KEY')))"
```

## Security Note

- **Never commit API keys to git**
- Add `config.py` to `.gitignore` if you store the key there
- Use environment variables for production/CI environments
- Rotate keys regularly

