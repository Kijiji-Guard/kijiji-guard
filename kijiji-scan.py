#!/usr/bin/env python3
import subprocess
import json
import sys

def run_kijiji_scan(directory="terraform"):
    """
    Kijiji-Guard: Automated NDPA 2023 Compliance Scanner
    """
    print("--- Kijiji-Guard: Protecting Africa's Next Unicorn ---")
    print(f"Scanning directory: {directory} for NDPA violations...\n")
    
    try:
        # Run Checkov with custom policies
        # Note: --external-checks-dir points to our custom Python policies
        command = [
            "checkov",
            "-d", directory,
            "--external-checks-dir", "policies",
            "--check", "CKV_NGR",
            "--output", "json"
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if not result.stdout:
            print("Error: Checkov failed to produce output. Ensure checkov is installed.")
            return

        scan_data = json.loads(result.stdout)
        
        # Checkov returns a list of results if multiple frameworks are scanned, 
        # or a single object if only one framework is scanned.
        if isinstance(scan_data, list):
            results = scan_data[0].get("results", {})
        else:
            results = scan_data.get("results", {})
            
        passed_checks = results.get("passed_checks", [])
        failed_checks = results.get("failed_checks", [])
        
        total_checks = len(passed_checks) + len(failed_checks)
        if total_checks > 0:
            compliance_score = (len(passed_checks) / total_checks) * 100
        else:
            compliance_score = 0
            
        print(f"Compliance Score: {compliance_score:.2f}%")
        print(f"Passed: {len(passed_checks)}")
        print(f"Failed: {len(failed_checks)}")
        
        if failed_checks:
            print("\nViolations Found:")
            for check in failed_checks:
                print(f"- [{check['check_id']}] {check['check_name']}")
                print(f"  Resource: {check['resource']}")
                print(f"  File: {check['file_path']}:{check['file_line_range'][0]}")
                print(f"  NDPA Alignment: {check.get('description', 'N/A')}")
        else:
            print("\nNo NDPA violations found. Your infrastructure is compliant!")
            
    except FileNotFoundError:
        print("Error: 'checkov' command not found. Please install it using 'pip install checkov'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_kijiji_scan()
