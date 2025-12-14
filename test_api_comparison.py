"""
Enhanced API Comparison Test Suite
Tests specific endpoints with actual GIDs from the database
"""
import json
import requests
import os
import psycopg2
from api_comparison import APIComparator
from typing import Dict, List, Optional

# Try to import config, fallback to environment variables
try:
    from config import ASANA_API_KEY, DATABASE_URL
except ImportError:
    ASANA_API_KEY = os.getenv("ASANA_API_KEY")
    DATABASE_URL = "postgresql://anshuanshu:anshu1406@localhost:5432/asana"


class EnhancedAPITester(APIComparator):
    """Extended tester that can use database GIDs"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_connection = None
        self.test_gids = {}
    
    def connect_database(self, connection_string: str = None):
        """Connect to database to get test GIDs"""
        if connection_string is None:
            # Try to use DATABASE_URL from config, fallback to default
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
    
    def test_with_real_gids(self):
        """Test endpoints using real GIDs from database"""
        if not self.db_connection:
            self.connect_database()
        
        # Get GIDs for various resources
        print("\n📊 Fetching test GIDs from database...")
        
        test_cases = []
        
        # Test GET by GID endpoints
        project_gids = self.get_gids_from_db("projects", 3)
        for gid in project_gids:
            test_cases.append({
                "method": "GET",
                "endpoint": f"/projects/{gid}",
                "description": f"Get project by GID: {gid}"
            })
        
        task_gids = self.get_gids_from_db("tasks", 3)
        for gid in task_gids:
            test_cases.append({
                "method": "GET",
                "endpoint": f"/tasks/{gid}",
                "description": f"Get task by GID: {gid}"
            })
        
        portfolio_gids = self.get_gids_from_db("portfolios", 2)
        for gid in portfolio_gids:
            test_cases.append({
                "method": "GET",
                "endpoint": f"/portfolios/{gid}",
                "description": f"Get portfolio by GID: {gid}"
            })
        
        goal_gids = self.get_gids_from_db("goals", 2)
        for gid in goal_gids:
            test_cases.append({
                "method": "GET",
                "endpoint": f"/goals/{gid}",
                "description": f"Get goal by GID: {gid}"
            })
        
        team_gids = self.get_gids_from_db("teams", 2)
        for gid in team_gids:
            test_cases.append({
                "method": "GET",
                "endpoint": f"/teams/{gid}",
                "description": f"Get team by GID: {gid}"
            })
        
        workspace_gids = self.get_gids_from_db("workspaces", 2)
        for gid in workspace_gids:
            test_cases.append({
                "method": "GET",
                "endpoint": f"/workspaces/{gid}",
                "description": f"Get workspace by GID: {gid}"
            })
        
        job_gids = self.get_gids_from_db("jobs", 2)
        for gid in job_gids:
            test_cases.append({
                "method": "GET",
                "endpoint": f"/jobs/{gid}",
                "description": f"Get job by GID: {gid}"
            })
        
        # Test list endpoints with filters
        if workspace_gids:
            test_cases.append({
                "method": "GET",
                "endpoint": "/projects",
                "params": {"workspace": workspace_gids[0], "limit": 5},
                "description": f"Get projects filtered by workspace: {workspace_gids[0]}"
            })
            
            test_cases.append({
                "method": "GET",
                "endpoint": "/tasks",
                "params": {"workspace": workspace_gids[0], "limit": 5},
                "description": f"Get tasks filtered by workspace: {workspace_gids[0]}"
            })
        
        if team_gids:
            test_cases.append({
                "method": "GET",
                "endpoint": "/projects",
                "params": {"team": team_gids[0], "limit": 5},
                "description": f"Get projects filtered by team: {team_gids[0]}"
            })
        
        if portfolio_gids:
            test_cases.append({
                "method": "GET",
                "endpoint": f"/portfolios/{portfolio_gids[0]}/portfolio_memberships",
                "description": f"Get portfolio memberships for portfolio: {portfolio_gids[0]}"
            })
        
        print(f"📝 Generated {len(test_cases)} test cases\n")
        
        # Run tests
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {test_case.get('description', test_case['endpoint'])}")
            try:
                self.test_endpoint(
                    method=test_case["method"],
                    endpoint=test_case["endpoint"],
                    params=test_case.get("params"),
                    data=test_case.get("data"),
                    skip_asana=not self.asana_api_key  # Skip if no API key
                )
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                continue
        
        # Close database connection
        if self.db_connection:
            self.db_connection.close()
    
    def test_list_endpoints(self):
        """Test list endpoints (GET without GID)"""
        list_endpoints = [
            {"method": "GET", "endpoint": "/workspaces", "params": {"limit": 5}},
            {"method": "GET", "endpoint": "/users", "params": {"limit": 5}},
            {"method": "GET", "endpoint": "/teams", "params": {"limit": 5}},
            {"method": "GET", "endpoint": "/projects", "params": {"limit": 5}},
            {"method": "GET", "endpoint": "/tasks", "params": {"limit": 5}},
            {"method": "GET", "endpoint": "/goals", "params": {"limit": 5}},
            {"method": "GET", "endpoint": "/portfolios", "params": {"limit": 5}},
            {"method": "GET", "endpoint": "/tags", "params": {"limit": 5}},
        ]
        
        print("\n📋 Testing list endpoints...")
        for test_case in list_endpoints:
            try:
                self.test_endpoint(**test_case)
            except Exception as e:
                print(f"❌ Error testing {test_case['endpoint']}: {str(e)}")


def main():
    """Main test runner"""
    print("="*70)
    print("API Comparison Test Suite")
    print("="*70)
    
    # Get API key from config or environment
    try:
        from config import ASANA_API_KEY as config_key
        asana_api_key = config_key if config_key else os.getenv("ASANA_API_KEY")
    except ImportError:
        asana_api_key = os.getenv("ASANA_API_KEY")
    
    if not asana_api_key:
        print("\n⚠️  ASANA_API_KEY not found.")
        print("   The script will only test your local API structure.")
        print("   Set the key in config.py or export ASANA_API_KEY environment variable")
        print()
    
    # Initialize tester
    tester = EnhancedAPITester(asana_api_key=asana_api_key)
    
    # Test list endpoints first
    tester.test_list_endpoints()
    
    # Test endpoints with real GIDs
    tester.test_with_real_gids()
    
    # Generate reports
    print("\n" + "="*70)
    print("Generating Reports...")
    print("="*70)
    
    report = tester.generate_report("api_comparison_report.json")
    tester.generate_ai_prompt("ai_fix_prompt.txt")
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"✅ Matches: {report['summary']['matches']}")
    print(f"❌ Differences: {report['summary']['differences']}")
    
    if report['summary']['differences'] > 0:
        print(f"\n⚠️  Review 'ai_fix_prompt.txt' for details on differences")
        print("   You can provide this file to the AI to fix the code")
    
    print("="*70)


if __name__ == "__main__":
    main()

