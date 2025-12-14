"""
Comprehensive API Test Suite
Tests ALL endpoints with ALL HTTP methods and status codes
"""
import json
import requests
import os
import psycopg2
import ast
import re
from api_comparison import APIComparator
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class ComprehensiveAPITester(APIComparator):
    """Comprehensive tester that discovers and tests all endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_connection = None
        self.all_endpoints = []
        self.test_gids = {}
        self.created_resources = []  # Track created resources for cleanup
    
    def connect_database(self, connection_string: str = None):
        """Connect to database to get test GIDs"""
        if connection_string is None:
            try:
                from config import DATABASE_URL
                connection_string = DATABASE_URL
            except ImportError:
                connection_string = "postgresql://anshuanshu:anshu1406@localhost:5432/asana"
        
        try:
            self.db_connection = psycopg2.connect(connection_string)
            print("✅ Connected to database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    
    def get_gids_from_db(self, table: str, limit: int = 5) -> List[str]:
        """Get GIDs from database for testing"""
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(f"SELECT gid FROM {table} LIMIT %s", (limit,))
            gids = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return gids
        except Exception as e:
            print(f"Error getting GIDs from {table}: {e}")
            return []
    
    def discover_endpoints(self, endpoints_dir: str = "endpoints") -> List[Dict[str, Any]]:
        """Discover all endpoints by parsing endpoint files"""
        endpoints = []
        endpoints_path = Path(endpoints_dir)
        
        if not endpoints_path.exists():
            print(f"❌ Endpoints directory not found: {endpoints_dir}")
            return endpoints
        
        print(f"\n🔍 Discovering endpoints from {endpoints_dir}...")
        
        for file_path in endpoints_path.glob("*.py"):
            if file_path.name == "__init__.py":
                continue
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Find all @router decorators
                router_pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
                matches = re.findall(router_pattern, content, re.IGNORECASE)
                
                for method, endpoint_path in matches:
                    endpoints.append({
                        "file": file_path.name,
                        "method": method.upper(),
                        "endpoint": endpoint_path,
                        "full_path": f"/api/1.0{endpoint_path}"
                    })
            
            except Exception as e:
                print(f"⚠️  Error parsing {file_path.name}: {e}")
        
        print(f"✅ Discovered {len(endpoints)} endpoints")
        return endpoints
    
    def get_test_data_for_endpoint(self, endpoint: Dict[str, Any]) -> Tuple[Dict, Dict]:
        """Generate test data for an endpoint based on its method and path"""
        method = endpoint["method"]
        path = endpoint["endpoint"]
        params = {}
        data = None
        
        # Get GIDs from database
        if not self.test_gids:
            self._load_test_gids()
        
        # Handle different endpoint patterns
        if method == "GET":
            # List endpoints - add pagination
            if not re.search(r'\{[^}]+\}', path):
                params = {"limit": 5}
            
            # Endpoints with GID in path - extract and use real GID
            gid_match = re.search(r'\{(\w+)_gid\}', path)
            if gid_match:
                gid_type = gid_match.group(1)
                gid = self._get_gid_for_type(gid_type)
                if gid:
                    path = path.replace(f"{{{gid_type}_gid}}", gid)
            
            # Filter endpoints
            if "workspace" in path or "workspaces" in path:
                workspace_gid = self._get_gid_for_type("workspace")
                if workspace_gid:
                    params["workspace"] = workspace_gid
            
            if "team" in path:
                team_gid = self._get_gid_for_type("team")
                if team_gid:
                    params["team"] = team_gid
        
        elif method == "POST":
            # Create operations - generate minimal data
            data = self._generate_create_data(path)
        
        elif method == "PUT":
            # Update operations - need existing GID
            gid_match = re.search(r'\{(\w+)_gid\}', path)
            if gid_match:
                gid_type = gid_match.group(1)
                gid = self._get_gid_for_type(gid_type)
                if gid:
                    path = path.replace(f"{{{gid_type}_gid}}", gid)
                    data = self._generate_update_data(path)
        
        elif method == "DELETE":
            # Delete operations - need existing GID
            gid_match = re.search(r'\{(\w+)_gid\}', path)
            if gid_match:
                gid_type = gid_match.group(1)
                gid = self._get_gid_for_type(gid_type)
                if gid:
                    path = path.replace(f"{{{gid_type}_gid}}", gid)
        
        return {"endpoint": path, "params": params, "data": data}, endpoint
    
    def _load_test_gids(self):
        """Load GIDs from database for all resource types"""
        if not self.db_connection:
            self.connect_database()
        
        resource_tables = {
            "workspace": "workspaces",
            "user": "users",
            "team": "teams",
            "project": "projects",
            "task": "tasks",
            "goal": "goals",
            "portfolio": "portfolios",
            "tag": "tags",
            "section": "sections",
            "story": "stories",
            "status_update": "status_updates",
            "project_status": "project_statuses",
            "project_brief": "project_briefs",
            "webhook": "webhooks",
            "job": "jobs",
            "custom_field": "custom_fields",
            "rate": "rates",
            "task_template": "task_templates",
            "time_tracking_entry": "time_tracking_entries",
            "budget": "budgets",
            "allocation": "allocations",
            "attachment": "attachments",
            "access_request": "access_requests",
            "project_membership": "project_memberships",
            "portfolio_membership": "portfolio_memberships",
        }
        
        for resource_type, table_name in resource_tables.items():
            gids = self.get_gids_from_db(table_name, 3)
            if gids:
                self.test_gids[resource_type] = gids
    
    def _get_gid_for_type(self, resource_type: str) -> Optional[str]:
        """Get a GID for a resource type"""
        # Handle plural/singular
        singular = resource_type.rstrip('s')
        if singular in self.test_gids:
            return self.test_gids[singular][0] if self.test_gids[singular] else None
        if resource_type in self.test_gids:
            return self.test_gids[resource_type][0] if self.test_gids[resource_type] else None
        return None
    
    def _generate_create_data(self, path: str) -> Dict:
        """Generate minimal data for create operations"""
        data = {"data": {}}
        
        if "project" in path:
            data["data"] = {"name": "Test Project", "workspace": self._get_gid_for_type("workspace")}
        elif "task" in path:
            data["data"] = {"name": "Test Task", "workspace": self._get_gid_for_type("workspace")}
        elif "goal" in path:
            data["data"] = {"name": "Test Goal", "workspace": self._get_gid_for_type("workspace")}
        elif "portfolio" in path:
            data["data"] = {"name": "Test Portfolio", "workspace": self._get_gid_for_type("workspace")}
        elif "tag" in path:
            data["data"] = {"name": "Test Tag", "workspace": self._get_gid_for_type("workspace")}
        elif "team" in path:
            data["data"] = {"name": "Test Team", "organization": self._get_gid_for_type("workspace")}
        elif "section" in path:
            data["data"] = {"name": "Test Section"}
        elif "story" in path:
            data["data"] = {"text": "Test story"}
        elif "webhook" in path:
            data["data"] = {"resource": self._get_gid_for_type("project"), "target": "https://example.com/webhook"}
        else:
            data["data"] = {"name": "Test Resource"}
        
        return data
    
    def _generate_update_data(self, path: str) -> Dict:
        """Generate minimal data for update operations"""
        return {"data": {"name": "Updated Name"}}
    
    def test_all_endpoints(self, skip_destructive: bool = False, test_error_cases: bool = True):
        """Test all discovered endpoints"""
        if not self.all_endpoints:
            self.all_endpoints = self.discover_endpoints()
        
        print(f"\n{'='*70}")
        print(f"Testing {len(self.all_endpoints)} endpoints")
        print(f"{'='*70}\n")
        
        test_results = []
        tested_count = 0
        
        for i, endpoint in enumerate(self.all_endpoints, 1):
            method = endpoint["method"]
            original_path = endpoint["endpoint"]
            
            # Skip destructive operations if requested
            if skip_destructive and method in ["DELETE"]:
                print(f"[{i}/{len(self.all_endpoints)}] ⏭️  Skipping {method} {original_path} (destructive)")
                continue
            
            try:
                # Get test data
                test_config, endpoint_info = self.get_test_data_for_endpoint(endpoint)
                test_path = test_config["endpoint"]
                params = test_config.get("params", {})
                data = test_config.get("data")
                
                print(f"[{i}/{len(self.all_endpoints)}] Testing {method} {test_path}")
                tested_count += 1
                
                # Test the endpoint
                result = self.test_endpoint(
                    method=method,
                    endpoint=test_path,
                    params=params if params else None,
                    data=data,
                    skip_asana=not self.asana_api_key
                )
                
                test_results.append(result)
                
                # Test error cases (404, 400) for GET endpoints
                if test_error_cases and method == "GET" and "{" in original_path:
                    self._test_error_cases(method, test_path, endpoint_info)
            
            except Exception as e:
                print(f"❌ Error testing {method} {original_path}: {str(e)}")
                test_results.append({
                    "endpoint": original_path,
                    "method": method,
                    "error": str(e),
                    "match": False,
                    "status_match": False
                })
                continue
        
        print(f"\n✅ Tested {tested_count} endpoints out of {len(self.all_endpoints)} total")
        return test_results
    
    def _test_error_cases(self, method: str, endpoint: str, endpoint_info: Dict):
        """Test error cases (404, 400, etc.)"""
        # Test 404 - invalid GID
        if "{" in endpoint_info["endpoint"]:
            invalid_gid = "00000000-0000-0000-0000-000000000000"
            test_path = endpoint_info["endpoint"].replace(
                re.search(r'\{[^}]+\}', endpoint_info["endpoint"]).group(0),
                invalid_gid
            )
            
            print(f"  → Testing 404 case: {method} {test_path}")
            local_status, local_response = self.make_request(
                method, test_path, self.local_base_url
            )
            
            if self.asana_api_key:
                asana_status, asana_response = self.make_request(
                    method, test_path, self.asana_base_url,
                    headers=self.asana_headers
                )
                
                # Compare status codes
                status_match = local_status == asana_status
                if not status_match:
                    print(f"    ❌ Status mismatch: Local={local_status}, Asana={asana_status}")
                    self.test_results.append({
                        "endpoint": test_path,
                        "method": method,
                        "test_type": "error_404",
                        "local_status": local_status,
                        "asana_status": asana_status,
                        "status_match": False,
                        "match": False
                    })
                else:
                    print(f"    ✅ Status codes match: {local_status}")
                    self.test_results.append({
                        "endpoint": test_path,
                        "method": method,
                        "test_type": "error_404",
                        "local_status": local_status,
                        "asana_status": asana_status,
                        "status_match": True,
                        "match": True
                    })
            else:
                # Just verify local returns 404
                if local_status == 404:
                    print(f"    ✅ Local returns correct 404")
                else:
                    print(f"    ⚠️  Local returned {local_status}, expected 404")
    
    def test_status_code_matching(self):
        """Test that status codes match for same scenarios"""
        print(f"\n{'='*70}")
        print("Testing Status Code Matching")
        print(f"{'='*70}\n")
        
        scenarios = [
            # Success cases
            {"method": "GET", "endpoint": "/workspaces", "expected": 200},
            {"method": "GET", "endpoint": "/users/me", "expected": 200},
            
            # Error cases
            {"method": "GET", "endpoint": "/projects/00000000-0000-0000-0000-000000000000", "expected": 404},
            {"method": "GET", "endpoint": "/tasks/invalid-gid", "expected": 404},
        ]
        
        for scenario in scenarios:
            print(f"Testing: {scenario['method']} {scenario['endpoint']} (expected: {scenario['expected']})")
            
            local_status, local_response = self.make_request(
                scenario["method"], scenario["endpoint"], self.local_base_url
            )
            
            if self.asana_api_key:
                asana_status, asana_response = self.make_request(
                    scenario["method"], scenario["endpoint"], self.asana_base_url,
                    headers=self.asana_headers
                )
                
                if local_status == asana_status == scenario["expected"]:
                    print(f"  ✅ Status codes match: {local_status}")
                else:
                    print(f"  ❌ Status mismatch: Local={local_status}, Asana={asana_status}, Expected={scenario['expected']}")
            else:
                if local_status == scenario["expected"]:
                    print(f"  ✅ Local status correct: {local_status}")
                else:
                    print(f"  ❌ Local status incorrect: {local_status}, Expected={scenario['expected']}")


def main():
    """Main comprehensive test runner"""
    print("="*70)
    print("COMPREHENSIVE API COMPARISON TEST SUITE")
    print("="*70)
    
    # Get API key
    try:
        from config import ASANA_API_KEY as config_key
        asana_api_key = config_key if config_key else os.getenv("ASANA_API_KEY")
    except ImportError:
        asana_api_key = os.getenv("ASANA_API_KEY")
    
    if not asana_api_key:
        print("\n⚠️  ASANA_API_KEY not found.")
        print("   Testing local API only (structure validation)")
        print()
    
    # Initialize tester
    tester = ComprehensiveAPITester(asana_api_key=asana_api_key)
    
    # Test status code matching
    tester.test_status_code_matching()
    
    # Test all endpoints (set skip_destructive=False to test DELETE/PUT)
    results = tester.test_all_endpoints(skip_destructive=False, test_error_cases=True)
    
    # Generate reports
    print("\n" + "="*70)
    print("Generating Reports...")
    print("="*70)
    
    report = tester.generate_report("comprehensive_api_comparison_report.json")
    tester.generate_ai_prompt("comprehensive_ai_fix_prompt.txt")
    
    # Calculate status code matches
    status_matches = sum(1 for r in report['results'] if r.get('status_match', False))
    status_total = sum(1 for r in report['results'] if 'status_match' in r)
    
    # Print summary
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*70)
    print(f"Total Endpoints Discovered: {len(tester.all_endpoints)}")
    print(f"Total Tests Executed: {report['summary']['total_tests']}")
    print(f"✅ Response Matches: {report['summary']['matches']}")
    print(f"❌ Response Differences: {report['summary']['differences']}")
    if status_total > 0:
        print(f"✅ Status Code Matches: {status_matches}/{status_total}")
        print(f"❌ Status Code Mismatches: {status_total - status_matches}")
    
    if report['summary']['differences'] > 0 or (status_total - status_matches) > 0:
        print(f"\n⚠️  Review 'comprehensive_ai_fix_prompt.txt' for details")
    
    print("="*70)
    
    # Close database
    if tester.db_connection:
        tester.db_connection.close()


if __name__ == "__main__":
    main()

