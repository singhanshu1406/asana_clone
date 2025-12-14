"""
Auto-fix Helper
Reads the comparison report and provides actionable fixes
"""
import json
import os
from typing import Dict, List, Any


def analyze_differences(report_file: str = "api_comparison_report.json") -> Dict[str, Any]:
    """Analyze differences and generate fix suggestions"""
    
    if not os.path.exists(report_file):
        print(f"❌ Report file not found: {report_file}")
        print("   Run the comparison script first: python test_api_comparison.py")
        return {}
    
    with open(report_file, 'r') as f:
        report = json.load(f)
    
    analysis = {
        "total_tests": report["summary"]["total_tests"],
        "matches": report["summary"]["matches"],
        "differences": report["summary"]["differences"],
        "issues": []
    }
    
    for result in report["results"]:
        if not result.get("match", True) and result.get("comparison"):
            comp = result["comparison"]
            issue = {
                "endpoint": result["endpoint"],
                "method": result["method"],
                "missing_fields": comp.get("missing_fields", []),
                "extra_fields": comp.get("extra_fields", []),
                "value_differences": bool(comp.get("differences")),
                "suggestions": []
            }
            
            # Generate suggestions
            if issue["missing_fields"]:
                issue["suggestions"].append(
                    f"Add missing fields to response: {', '.join(issue['missing_fields'])}"
                )
            
            if issue["extra_fields"]:
                issue["suggestions"].append(
                    f"Remove or hide extra fields: {', '.join(issue['extra_fields'])}"
                )
            
            if issue["value_differences"]:
                issue["suggestions"].append(
                    "Check field types and values - they may need to match Asana's format"
                )
            
            analysis["issues"].append(issue)
    
    return analysis


def print_analysis(analysis: Dict[str, Any]):
    """Print formatted analysis"""
    print("\n" + "="*70)
    print("API COMPARISON ANALYSIS")
    print("="*70)
    print(f"Total Tests: {analysis['total_tests']}")
    print(f"✅ Matches: {analysis['matches']}")
    print(f"❌ Issues Found: {analysis['differences']}")
    print("="*70)
    
    if not analysis["issues"]:
        print("\n🎉 All tests passed! Your API matches Asana's API.")
        return
    
    print(f"\n📋 Found {len(analysis['issues'])} endpoints with differences:\n")
    
    for i, issue in enumerate(analysis["issues"], 1):
        print(f"{i}. {issue['method']} {issue['endpoint']}")
        print(f"   Status: Local={issue.get('local_status', 'N/A')}, Asana={issue.get('asana_status', 'N/A')}")
        
        if issue["missing_fields"]:
            print(f"   ⚠️  Missing Fields: {', '.join(issue['missing_fields'][:5])}")
            if len(issue['missing_fields']) > 5:
                print(f"      ... and {len(issue['missing_fields']) - 5} more")
        
        if issue["extra_fields"]:
            print(f"   ⚠️  Extra Fields: {', '.join(issue['extra_fields'][:5])}")
            if len(issue['extra_fields']) > 5:
                print(f"      ... and {len(issue['extra_fields']) - 5} more")
        
        if issue["value_differences"]:
            print(f"   ⚠️  Value Differences: Yes")
        
        if issue["suggestions"]:
            print(f"   💡 Suggestions:")
            for suggestion in issue["suggestions"]:
                print(f"      - {suggestion}")
        
        print()


def generate_fix_prompt(analysis: Dict[str, Any], output_file: str = "fix_request.txt"):
    """Generate a detailed fix request for AI"""
    
    if not analysis["issues"]:
        return
    
    prompt = """# API Fix Request

The following endpoints need to be fixed to match Asana's API responses.

Please review each endpoint and update the code accordingly.

"""
    
    for issue in analysis["issues"]:
        prompt += f"""
## {issue['method']} {issue['endpoint']}

"""
        
        if issue["missing_fields"]:
            prompt += f"### Missing Fields\n"
            prompt += f"The following fields are present in Asana's API but missing in your API:\n\n"
            for field in issue["missing_fields"]:
                prompt += f"- `{field}`\n"
            prompt += "\n**Action Required:** Add these fields to your response schema and endpoint code.\n\n"
        
        if issue["extra_fields"]:
            prompt += f"### Extra Fields\n"
            prompt += f"The following fields are in your API but not in Asana's API:\n\n"
            for field in issue["extra_fields"]:
                prompt += f"- `{field}`\n"
            prompt += "\n**Action Required:** Remove these fields or mark them as optional/hidden.\n\n"
        
        if issue["value_differences"]:
            prompt += f"### Value Differences\n"
            prompt += f"Field values or types don't match Asana's API.\n\n"
            prompt += "**Action Required:** Review the detailed differences in `api_comparison_report.json` and update field types/values.\n\n"
        
        prompt += "---\n\n"
    
    prompt += """
## General Instructions

1. Review the endpoint code in `endpoints/` directory
2. Update response schemas in `schemas/` directory if needed
3. Ensure all fields match Asana's API structure
4. Test the endpoint after making changes
5. Re-run the comparison script to verify fixes

## Files to Review

- `endpoints/{endpoint_name}.py` - Endpoint implementation
- `schemas/{schema_name}.py` - Response schemas
- `models/{model_name}.py` - Database models (if schema changes needed)
"""
    
    with open(output_file, 'w') as f:
        f.write(prompt)
    
    print(f"\n✅ Fix request generated: {output_file}")
    print(f"   Provide this file to the AI to get code fixes.")


def main():
    """Main function"""
    print("Analyzing API comparison results...")
    
    analysis = analyze_differences()
    
    if not analysis:
        return
    
    print_analysis(analysis)
    
    if analysis["issues"]:
        generate_fix_prompt(analysis)
        print("\n💡 Next Steps:")
        print("   1. Review the analysis above")
        print("   2. Check 'fix_request.txt' for detailed fix instructions")
        print("   3. Provide 'fix_request.txt' to the AI to get code fixes")
        print("   4. Or manually fix the issues in the endpoint files")


if __name__ == "__main__":
    main()

