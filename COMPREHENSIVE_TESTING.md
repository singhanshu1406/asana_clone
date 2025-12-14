# Comprehensive API Testing Guide

## Overview

The comprehensive test suite automatically discovers and tests **ALL 138 endpoints** across all HTTP methods and status codes.

## Test Coverage

### Endpoints Discovered
- **GET**: 71 endpoints
- **POST**: 31 endpoints  
- **PUT**: 14 endpoints
- **DELETE**: 22 endpoints
- **Total**: 138 endpoints

### What Gets Tested

1. **All HTTP Methods**
   - GET (list and by GID)
   - POST (create operations)
   - PUT (update operations)
   - DELETE (delete operations)

2. **All Status Codes**
   - 200 (Success)
   - 404 (Not Found)
   - 400 (Bad Request)
   - 401 (Unauthorized)
   - 403 (Forbidden)
   - 500 (Internal Server Error)

3. **Response Comparison**
   - Field presence
   - Field types
   - Field values (normalized)
   - Nested objects
   - Arrays

4. **Error Cases**
   - Invalid GIDs
   - Missing required fields
   - Invalid data formats
   - Non-existent resources

## Running Tests

### Option 1: Comprehensive Test (All Endpoints)
```bash
python3 comprehensive_api_test.py
```

This will:
- Discover all 138 endpoints
- Test each endpoint
- Compare responses with Asana API
- Test error cases
- Generate comprehensive report

### Option 2: Status Code Testing Only
```bash
python3 test_all_status_codes.py
```

This focuses on:
- Status code matching
- Error scenarios
- Edge cases

### Option 3: Original Test (Selective)
```bash
python3 test_api_comparison.py
```

Tests a curated list of important endpoints.

## Test Results

### Reports Generated

1. **comprehensive_api_comparison_report.json**
   - Full test results
   - All endpoint comparisons
   - Status code matches
   - Response differences

2. **comprehensive_ai_fix_prompt.txt**
   - Formatted for AI assistance
   - Lists all differences
   - Provides fix suggestions

3. **status_code_test_report.json**
   - Status code test results
   - Scenario-by-scenario breakdown

## Understanding Results

### ✅ Match
- Status codes match
- Response structure matches
- All fields present
- Field types match

### ❌ Difference
- Status code mismatch
- Missing fields
- Extra fields
- Type mismatches
- Value differences

## Status Code Matching

The test ensures:
- Same input → Same status code
- 404 for non-existent resources
- 400 for invalid input
- 200 for successful operations
- Proper error handling

## Customization

### Skip Destructive Operations
Edit `comprehensive_api_test.py`:
```python
results = tester.test_all_endpoints(skip_destructive=True)  # Skips DELETE
```

### Test Specific Endpoints
Modify the `discover_endpoints()` method to filter endpoints.

### Add Custom Test Cases
Add to `test_all_status_codes.py` scenarios list.

## Next Steps

1. Run comprehensive test:
   ```bash
   python3 comprehensive_api_test.py
   ```

2. Review results:
   ```bash
   python3 auto_fix_helper.py
   ```

3. Get AI help:
   - Open `comprehensive_ai_fix_prompt.txt`
   - Provide to Cursor AI for fixes

## Performance Notes

- Testing 138 endpoints takes time
- Asana API has rate limits
- Consider running in batches
- Use `skip_destructive=True` for faster testing

## Troubleshooting

**Too many tests?**
- Use `skip_destructive=True` to skip DELETE operations
- Filter endpoints in `discover_endpoints()`

**Rate limiting?**
- Add delays between requests
- Test in smaller batches

**Missing GIDs?**
- Ensure database has test data
- Run `python seed_data.py` first

