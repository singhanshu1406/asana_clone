# API Comparison Testing

This script compares your local Asana API implementation with the real Asana API to ensure responses match.

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements_comparison.txt
```

2. **Set Asana API Key (optional):**
```bash
export ASANA_API_KEY="your_asana_api_key_here"
```

If you don't set the API key, the script will only test your local API (useful for structure validation).

## Usage

### Basic Comparison
```bash
python api_comparison.py
```

### Enhanced Testing (with database GIDs)
```bash
python test_api_comparison.py
```

The enhanced version:
- Connects to your database
- Fetches real GIDs from your tables
- Tests endpoints using those GIDs
- Compares responses with Asana API

## Output Files

1. **api_comparison_report.json** - Detailed JSON report with all test results
2. **ai_fix_prompt.txt** - Formatted prompt for AI to fix differences

## Understanding the Results

### ✅ Match
- Response structure matches
- All fields present
- Field types match
- Values match (ignoring GIDs/timestamps)

### ❌ Differences
- Missing fields in your API
- Extra fields in your API
- Different field types
- Different values

## Using AI to Fix Differences

1. Run the comparison script
2. Review `ai_fix_prompt.txt`
3. Provide the file to the AI (Cursor) with:
   ```
   Please review the differences in ai_fix_prompt.txt and fix the code 
   to match Asana's API responses.
   ```

## Customization

### Add More Test Cases

Edit `test_api_comparison.py` and add to the `test_cases` list:

```python
test_cases.append({
    "method": "GET",
    "endpoint": "/your_endpoint",
    "params": {"key": "value"},
    "description": "Test description"
})
```

### Ignore Additional Fields

Edit `api_comparison.py` and modify the `normalize_response` method:

```python
ignore_fields = ['gid', 'id', 'created_at', 'your_field_to_ignore']
```

## Notes

- The script normalizes responses by removing GIDs, timestamps, and IDs
- Only structural and semantic differences are reported
- Rate limiting: Asana API has rate limits, so tests may need delays
- Authentication: Asana API requires valid API key for real comparisons

