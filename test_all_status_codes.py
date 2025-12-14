"""
Test Status Code Matching
Ensures all status codes match between local and Asana APIs
"""
import os
from comprehensive_api_test import ComprehensiveAPITester


def test_all_status_scenarios():
    """Test all possible status code scenarios"""
    print("="*70)
    print("STATUS CODE MATCHING TEST")
    print("="*70)
    
    # Get API key
    try:
        from config import ASANA_API_KEY as config_key
        asana_api_key = config_key if config_key else os.getenv("ASANA_API_KEY")
    except ImportError:
        asana_api_key = os.getenv("ASANA_API_KEY")
    
    tester = ComprehensiveAPITester(asana_api_key=asana_api_key)
    tester.connect_database()
    tester._load_test_gids()
    
    # Test scenarios for different status codes
    scenarios = []
    
    # 200 - Success cases
    if tester.test_gids.get("workspace"):
        scenarios.append({
            "method": "GET",
            "endpoint": f"/workspaces/{tester.test_gids['workspace'][0]}",
            "expected_status": 200,
            "description": "GET existing workspace"
        })
    
    if tester.test_gids.get("project"):
        scenarios.append({
            "method": "GET",
            "endpoint": f"/projects/{tester.test_gids['project'][0]}",
            "expected_status": 200,
            "description": "GET existing project"
        })
    
    # 404 - Not found cases
    scenarios.extend([
        {
            "method": "GET",
            "endpoint": "/projects/00000000-0000-0000-0000-000000000000",
            "expected_status": 404,
            "description": "GET non-existent project"
        },
        {
            "method": "GET",
            "endpoint": "/tasks/invalid-gid-format",
            "expected_status": 404,
            "description": "GET with invalid GID format"
        },
        {
            "method": "PUT",
            "endpoint": "/projects/00000000-0000-0000-0000-000000000000",
            "expected_status": 404,
            "description": "PUT non-existent project",
            "data": {"data": {"name": "Test"}}
        },
        {
            "method": "DELETE",
            "endpoint": "/projects/00000000-0000-0000-0000-000000000000",
            "expected_status": 404,
            "description": "DELETE non-existent project"
        }
    ])
    
    # 400 - Bad request cases
    scenarios.extend([
        {
            "method": "POST",
            "endpoint": "/projects",
            "expected_status": 400,
            "description": "POST project with invalid data",
            "data": {"data": {}}  # Missing required fields
        }
    ])
    
    # Test all scenarios
    print(f"\nTesting {len(scenarios)} status code scenarios...\n")
    
    results = {
        "total": len(scenarios),
        "matches": 0,
        "mismatches": 0,
        "details": []
    }
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"[{i}/{len(scenarios)}] {scenario['description']}")
        print(f"  {scenario['method']} {scenario['endpoint']}")
        
        # Test local API
        local_status, local_response = tester.make_request(
            scenario["method"],
            scenario["endpoint"],
            tester.local_base_url,
            params=scenario.get("params"),
            data=scenario.get("data")
        )
        
        # Test Asana API if key available
        if asana_api_key:
            asana_status, asana_response = tester.make_request(
                scenario["method"],
                scenario["endpoint"],
                tester.asana_base_url,
                headers=tester.asana_headers,
                params=scenario.get("params"),
                data=scenario.get("data")
            )
            
            status_match = local_status == asana_status
            expected_match = local_status == scenario["expected_status"] and asana_status == scenario["expected_status"]
            
            if status_match and expected_match:
                print(f"  ✅ Status codes match: {local_status} (as expected)")
                results["matches"] += 1
            elif status_match:
                print(f"  ⚠️  Status codes match: {local_status} (but expected {scenario['expected_status']})")
                results["mismatches"] += 1
            else:
                print(f"  ❌ Status mismatch: Local={local_status}, Asana={asana_status}, Expected={scenario['expected_status']}")
                results["mismatches"] += 1
            
            results["details"].append({
                "scenario": scenario["description"],
                "endpoint": scenario["endpoint"],
                "method": scenario["method"],
                "local_status": local_status,
                "asana_status": asana_status,
                "expected_status": scenario["expected_status"],
                "status_match": status_match,
                "expected_match": expected_match
            })
        else:
            # Just check local matches expected
            if local_status == scenario["expected_status"]:
                print(f"  ✅ Local status correct: {local_status}")
                results["matches"] += 1
            else:
                print(f"  ⚠️  Local status: {local_status}, Expected: {scenario['expected_status']}")
                results["mismatches"] += 1
            
            results["details"].append({
                "scenario": scenario["description"],
                "endpoint": scenario["endpoint"],
                "method": scenario["method"],
                "local_status": local_status,
                "expected_status": scenario["expected_status"],
                "expected_match": local_status == scenario["expected_status"]
            })
        
        print()
    
    # Print summary
    print("="*70)
    print("STATUS CODE TEST SUMMARY")
    print("="*70)
    print(f"Total Scenarios: {results['total']}")
    print(f"✅ Matches: {results['matches']}")
    print(f"❌ Mismatches: {results['mismatches']}")
    print("="*70)
    
    # Save detailed report
    import json
    with open("status_code_test_report.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: status_code_test_report.json")
    
    if tester.db_connection:
        tester.db_connection.close()
    
    return results


if __name__ == "__main__":
    test_all_status_scenarios()

