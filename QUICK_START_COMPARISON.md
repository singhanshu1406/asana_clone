# Quick Start: API Comparison Testing

## Step 1: Install Dependencies
```bash
pip install -r requirements_comparison.txt
```

## Step 2: Set Asana API Key (Optional)
If you want to compare with real Asana API:
```bash
export ASANA_API_KEY="your_asana_api_key_here"
```

If you don't have an API key, the script will still test your local API structure.

## Step 3: Run the Tests
```bash
python test_api_comparison.py
```

This will:
- Connect to your database
- Fetch real GIDs from your tables
- Test endpoints using those GIDs
- Compare responses with Asana API (if API key provided)
- Generate reports

## Step 4: Analyze Results
```bash
python auto_fix_helper.py
```

This will:
- Analyze the comparison report
- Identify specific differences
- Generate fix suggestions
- Create `fix_request.txt` for AI assistance

## Step 5: Get AI Help
1. Review `ai_fix_prompt.txt` or `fix_request.txt`
2. Provide it to Cursor AI with:
   ```
   Please review the differences in fix_request.txt and fix the code 
   to match Asana's API responses.
   ```

## Output Files

- `api_comparison_report.json` - Full detailed report
- `ai_fix_prompt.txt` - Detailed prompt for AI
- `fix_request.txt` - Actionable fix instructions

## What Gets Compared?

✅ **Compared:**
- Response structure (fields present)
- Field types (string, int, bool, etc.)
- Field values (normalized, ignoring GIDs/timestamps)
- HTTP status codes
- Error message formats

❌ **Ignored:**
- GIDs (always different)
- Timestamps (created_at, updated_at)
- Internal IDs
- Auto-generated values

## Example Output

```
Testing: GET /projects/abc-123
Local API Status: 200
Asana API Status: 200
✅ Responses match!

Testing: GET /tasks/xyz-789
Local API Status: 200
Asana API Status: 200
❌ DIFFERENCES FOUND!
  Missing fields: ['assignee.name', 'custom_fields']
  Extra fields: ['internal_id']
```

## Troubleshooting

**Database connection error:**
- Check your database is running
- Verify connection string in `test_api_comparison.py`

**Asana API errors:**
- Verify API key is correct
- Check rate limits (add delays if needed)
- Some endpoints may require workspace access

**No differences found:**
- Great! Your API matches Asana's structure
- Re-run tests periodically as you add features

