#!/usr/bin/env python3
"""
Test runner script for Metrika application high-priority tests
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_tests(test_type="high_priority", coverage=True, verbose=True):
    """
    Run tests with specified configuration
    
    Args:
        test_type (str): Type of tests to run ('high_priority', 'all', 'unit', 'integration')
        coverage (bool): Whether to run with coverage reporting
        verbose (bool): Whether to run in verbose mode
    """
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🧪 METRIKA APPLICATION TEST RUNNER")
    print("=" * 50)
    print(f"📁 Project root: {project_root}")
    print(f"🔍 Test type: {test_type}")
    print(f"📊 Coverage: {'Enabled' if coverage else 'Disabled'}")
    print(f"🔊 Verbose: {'Enabled' if verbose else 'Disabled'}")
    print("-" * 50)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test selection
    if test_type == "high_priority":
        cmd.extend([
            "test/test_data_loading.py",
            "test/test_csv_conversion.py", 
            "test/test_visualization.py",
            "test/test_streamlit_app_integration.py",
            "test/test_utils.py"
        ])
    elif test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "all":
        cmd.extend(["test/"])
    
    # Add coverage options
    if coverage:
        cmd.extend([
            "--cov=.",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])
    
    # Add verbose option
    if verbose:
        cmd.append("-v")
    
    # Add other options
    cmd.extend([
        "--tb=short",
        "--disable-warnings"
    ])
    
    print(f"🚀 Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        # Run the tests
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        print("-" * 50)
        if result.returncode == 0:
            print("✅ ALL TESTS PASSED!")
            print("🎉 Test execution completed successfully")
        else:
            print("❌ SOME TESTS FAILED!")
            print(f"Exit code: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ ERROR RUNNING TESTS: {str(e)}")
        return False

def run_specific_test_file(test_file):
    """
    Run a specific test file
    
    Args:
        test_file (str): Path to the test file to run
    """
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"🧪 Running specific test file: {test_file}")
    print("=" * 50)
    
    cmd = [
        "python", "-m", "pytest",
        test_file,
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def run_coverage_report():
    """Generate and display coverage report"""
    print("📊 GENERATING COVERAGE REPORT")
    print("=" * 50)
    
    cmd = [
        "python", "-m", "pytest",
        "--cov=.",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "test/",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode == 0:
            print("✅ Coverage report generated successfully")
            print("📁 HTML report available in: htmlcov/index.html")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ ERROR GENERATING COVERAGE: {str(e)}")
        return False

def main():
    """Main function to handle command line arguments and run tests"""
    parser = argparse.ArgumentParser(description="Metrika Application Test Runner")
    parser.add_argument(
        "--type", 
        choices=["high_priority", "all", "unit", "integration"],
        default="high_priority",
        help="Type of tests to run (default: high_priority)"
    )
    parser.add_argument(
        "--file",
        help="Run a specific test file"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run in quiet mode (less verbose)"
    )
    parser.add_argument(
        "--coverage-only",
        action="store_true",
        help="Generate coverage report only"
    )
    
    args = parser.parse_args()
    
    if args.coverage_only:
        success = run_coverage_report()
    elif args.file:
        success = run_specific_test_file(args.file)
    else:
        success = run_tests(
            test_type=args.type,
            coverage=not args.no_coverage,
            verbose=not args.quiet
        )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 