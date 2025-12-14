"""
API Comparison Script
Compares local Asana API responses with real Asana API responses
"""
import json
import requests
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from deepdiff import DeepDiff
import sys


class APIComparator:
    """Compare local API with Asana API"""
    
    def __init__(self, local_base_url: str = "http://localhost:8000/api/1.0", 
                 asana_base_url: str = "https://app.asana.com/api/1.0",
                 asana_api_key: Optional[str] = None):
        self.local_base_url = local_base_url
        self.asana_base_url = asana_base_url
        self.asana_api_key = asana_api_key or os.getenv("ASANA_API_KEY")
        
        if not self.asana_api_key:
            print("Warning: ASANA_API_KEY not set. Asana API calls will fail.")
        
        self.asana_headers = {
            "Authorization": f"Bearer {self.asana_api_key}",
            "Content-Type": "application/json"
        }
        
        self.differences = []
        self.test_results = []
    
    def normalize_response(self, response_data: Dict[str, Any], 
                          ignore_fields: List[str] = None) -> Dict[str, Any]:
        """
        Normalize response by removing fields that will always differ
        (GIDs, timestamps, IDs, etc.)
        """
        if ignore_fields is None:
            ignore_fields = ['gid', 'id', 'created_at', 'updated_at', 
                           'modified_at', 'created_by', 'modified_by']
        
        if isinstance(response_data, dict):
            normalized = {}
            for key, value in response_data.items():
                if key in ignore_fields:
                    continue
                elif isinstance(value, dict):
                    normalized[key] = self.normalize_response(value, ignore_fields)
                elif isinstance(value, list):
                    normalized[key] = [
                        self.normalize_response(item, ignore_fields) 
                        if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    normalized[key] = value
            return normalized
        elif isinstance(response_data, list):
            return [
                self.normalize_response(item, ignore_fields) 
                if isinstance(item, dict) else item
                for item in response_data
            ]
        return response_data
    
    def make_request(self, method: str, endpoint: str, 
                    base_url: str, headers: Dict = None,
                    params: Dict = None, data: Dict = None) -> Tuple[int, Dict]:
        """Make HTTP request and return status code and response"""
        url = f"{base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, params=params, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, params=params, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, params=params, timeout=10)
            else:
                return 405, {"error": "Method not allowed"}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw": response.text}
            
            return response.status_code, response_data
        except requests.exceptions.RequestException as e:
            return 0, {"error": str(e)}
    
    def compare_responses(self, local_response: Dict, asana_response: Dict,
                         endpoint: str) -> Dict[str, Any]:
        """Compare two responses and return differences"""
        # Normalize both responses
        local_normalized = self.normalize_response(local_response)
        asana_normalized = self.normalize_response(asana_response)
        
        # Use DeepDiff to find differences
        diff = DeepDiff(
            asana_normalized,
            local_normalized,
            ignore_order=True,
            verbose_level=2
        )
        
        # Also check structure (field presence)
        local_keys = set(self._get_all_keys(local_normalized))
        asana_keys = set(self._get_all_keys(asana_normalized))
        
        missing_in_local = asana_keys - local_keys
        extra_in_local = local_keys - asana_keys
        
        return {
            "endpoint": endpoint,
            "differences": diff.to_dict() if diff else {},
            "missing_fields": list(missing_in_local),
            "extra_fields": list(extra_in_local),
            "local_response": local_response,
            "asana_response": asana_response,
            "local_normalized": local_normalized,
            "asana_normalized": asana_normalized
        }
    
    def compare_status_codes(self, local_status: int, asana_status: int, 
                            endpoint: str) -> Dict[str, Any]:
        """Compare status codes and return match result"""
        match = local_status == asana_status
        return {
            "endpoint": endpoint,
            "local_status": local_status,
            "asana_status": asana_status,
            "match": match,
            "status_match": match
        }
    
    def _get_all_keys(self, obj: Any, prefix: str = "") -> List[str]:
        """Get all keys from nested dictionary"""
        keys = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.append(full_key)
                if isinstance(value, (dict, list)):
                    keys.extend(self._get_all_keys(value, full_key))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                keys.extend(self._get_all_keys(item, f"{prefix}[{i}]"))
        return keys
    
    def test_endpoint(self, method: str, endpoint: str, 
                     params: Dict = None, data: Dict = None,
                     skip_asana: bool = False) -> Dict[str, Any]:
        """Test a single endpoint"""
        print(f"\n{'='*70}")
        print(f"Testing: {method} {endpoint}")
        print(f"{'='*70}")
        
        # Make request to local API
        local_status, local_response = self.make_request(
            method, endpoint, self.local_base_url, params=params, data=data
        )
        
        print(f"Local API Status: {local_status}")
        
        # Make request to Asana API (if not skipped)
        asana_status = None
        asana_response = None
        
        if not skip_asana and self.asana_api_key:
            asana_status, asana_response = self.make_request(
                method, endpoint, self.asana_base_url,
                headers=self.asana_headers, params=params, data=data
            )
            print(f"Asana API Status: {asana_status}")
        else:
            print("Skipping Asana API call")
            return {
                "endpoint": endpoint,
                "method": method,
                "local_status": local_status,
                "local_response": local_response,
                "skipped": True
            }
        
        # Compare status codes first
        status_comparison = self.compare_status_codes(local_status, asana_status, endpoint)
        
        # Compare responses if both succeeded
        comparison = None
        if local_status == 200 and asana_status == 200:
            if "data" in local_response and "data" in asana_response:
                comparison = self.compare_responses(
                    local_response["data"], 
                    asana_response["data"],
                    endpoint
                )
            else:
                comparison = self.compare_responses(
                    local_response,
                    asana_response,
                    endpoint
                )
            
            if comparison["differences"] or comparison["missing_fields"] or comparison["extra_fields"]:
                print(f"❌ DIFFERENCES FOUND!")
                if comparison["missing_fields"]:
                    print(f"  Missing fields: {comparison['missing_fields']}")
                if comparison["extra_fields"]:
                    print(f"  Extra fields: {comparison['extra_fields']}")
                if comparison["differences"]:
                    print(f"  Value differences: {len(comparison['differences'])} types")
            else:
                print(f"✅ Responses match!")
        elif local_status != asana_status:
            print(f"⚠️  Status code mismatch: Local={local_status}, Asana={asana_status}")
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "local_status": local_status,
            "asana_status": asana_status,
            "status_match": status_comparison["match"],
            "local_response": local_response,
            "asana_response": asana_response,
            "comparison": comparison,
            "status_comparison": status_comparison,
            "match": (
                status_comparison["match"] and 
                (comparison is None or (
                    not comparison["differences"] and 
                    not comparison["missing_fields"] and 
                    not comparison["extra_fields"]
                ))
            )
        }
        
        self.test_results.append(result)
        return result
    
    def generate_report(self, output_file: str = "api_comparison_report.json"):
        """Generate a detailed comparison report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.test_results),
                "matches": sum(1 for r in self.test_results if r.get("match", False)),
                "differences": sum(1 for r in self.test_results if not r.get("match", True))
            },
            "results": self.test_results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n{'='*70}")
        print(f"Report generated: {output_file}")
        print(f"Total tests: {report['summary']['total_tests']}")
        print(f"Matches: {report['summary']['matches']}")
        print(f"Differences: {report['summary']['differences']}")
        print(f"{'='*70}")
        
        return report
    
    def generate_ai_prompt(self, output_file: str = "ai_fix_prompt.txt"):
        """Generate a prompt for AI to fix differences"""
        differences_found = [r for r in self.test_results 
                           if r.get("comparison") and not r.get("match", True)]
        
        if not differences_found:
            print("No differences found. No AI prompt needed.")
            return
        
        prompt = f"""# API Comparison Differences - Fix Request

The following endpoints have differences between the local API and Asana API.
Please analyze and fix the code to match Asana's API responses.

## Differences Found: {len(differences_found)}

"""
        
        for result in differences_found:
            comparison = result.get("comparison", {})
            prompt += f"""
### Endpoint: {result['method']} {result['endpoint']}

**Status Codes:**
- Local: {result['local_status']}
- Asana: {result['asana_status']}

"""
            
            if comparison.get("missing_fields"):
                prompt += f"**Missing Fields in Local API:**\n"
                for field in comparison["missing_fields"]:
                    prompt += f"  - {field}\n"
                prompt += "\n"
            
            if comparison.get("extra_fields"):
                prompt += f"**Extra Fields in Local API:**\n"
                for field in comparison["extra_fields"]:
                    prompt += f"  - {field}\n"
                prompt += "\n"
            
            if comparison.get("differences"):
                prompt += f"**Value Differences:**\n"
                diff_summary = json.dumps(comparison["differences"], indent=2, default=str)
                prompt += f"```json\n{diff_summary}\n```\n\n"
            
            # Add response samples
            prompt += f"**Asana Response Sample:**\n"
            asana_sample = json.dumps(comparison.get("asana_normalized", {}), indent=2, default=str)
            prompt += f"```json\n{asana_sample[:500]}...\n```\n\n"
            
            prompt += f"**Local Response Sample:**\n"
            local_sample = json.dumps(comparison.get("local_normalized", {}), indent=2, default=str)
            prompt += f"```json\n{local_sample[:500]}...\n```\n\n"
            prompt += "---\n\n"
        
        prompt += """
## Action Required

Please:
1. Review each difference
2. Update the endpoint code to match Asana's response structure
3. Ensure all fields are present with correct types
4. Verify nested objects match Asana's format
"""
        
        with open(output_file, 'w') as f:
            f.write(prompt)
        
        print(f"\nAI Fix Prompt generated: {output_file}")
        print(f"Review the file and provide it to the AI for code fixes.")


def main():
    """Main test runner"""
    comparator = APIComparator()
    
    # Test endpoints (you can expand this list)
    test_cases = [
        # GET endpoints
        {"method": "GET", "endpoint": "/workspaces", "params": {"limit": 5}},
        {"method": "GET", "endpoint": "/users/me"},
        {"method": "GET", "endpoint": "/projects", "params": {"limit": 5}},
        {"method": "GET", "endpoint": "/tasks", "params": {"limit": 5}},
        {"method": "GET", "endpoint": "/teams", "params": {"limit": 5}},
        {"method": "GET", "endpoint": "/goals", "params": {"limit": 5}},
        {"method": "GET", "endpoint": "/portfolios", "params": {"limit": 5}},
        {"method": "GET", "endpoint": "/tags", "params": {"limit": 5}},
        
        # Note: For endpoints with GIDs, you'll need to use actual GIDs from your database
        # Example: {"method": "GET", "endpoint": "/projects/{project_gid}"}
    ]
    
    print("Starting API Comparison Tests...")
    print(f"Local API: {comparator.local_base_url}")
    print(f"Asana API: {comparator.asana_base_url}")
    
    for test_case in test_cases:
        try:
            comparator.test_endpoint(**test_case)
        except Exception as e:
            print(f"Error testing {test_case['endpoint']}: {str(e)}")
            continue
    
    # Generate reports
    comparator.generate_report()
    comparator.generate_ai_prompt()
    
    print("\n✅ Testing complete!")


if __name__ == "__main__":
    main()

