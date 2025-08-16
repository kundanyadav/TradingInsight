#!/usr/bin/env python3
"""
Test runner for TradingInsight application.
Runs all tests and provides a comprehensive report.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_tests():
    """Run all tests and return results."""
    print("🚀 Starting TradingInsight Test Suite")
    print("=" * 50)
    
    # Change to the TradingInsight directory
    os.chdir(Path(__file__).parent)
    
    # Run tests with pytest
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--cov=services",
            "--cov=ui",
            "--cov=models",
            "--cov=config",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ], capture_output=True, text=True)
        
        print("📊 Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Test Warnings/Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_unit_tests():
    """Run only unit tests."""
    print("🧪 Running Unit Tests")
    print("-" * 30)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_data_models.py",
            "tests/test_services.py",
            "-v",
            "-m", "unit"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running unit tests: {e}")
        return False


def run_integration_tests():
    """Run only integration tests."""
    print("🔗 Running Integration Tests")
    print("-" * 30)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_mcp_integration.py",
            "-v",
            "-m", "integration"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        return False


def run_ui_tests():
    """Run UI component tests."""
    print("🎨 Running UI Component Tests")
    print("-" * 30)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_ui_components.py",
            "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running UI tests: {e}")
        return False


def check_test_coverage():
    """Check test coverage."""
    print("📈 Checking Test Coverage")
    print("-" * 30)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/",
            "--cov=services",
            "--cov=ui", 
            "--cov=models",
            "--cov=config",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error checking coverage: {e}")
        return False


def main():
    """Main test runner."""
    print("🧪 TradingInsight Test Suite")
    print("=" * 50)
    
    # Check if pytest is installed
    try:
        import pytest
        print("✅ Pytest is available")
    except ImportError:
        print("❌ Pytest is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
    
    # Run different test suites
    test_results = {}
    
    print("\n1. Running Unit Tests...")
    test_results['unit'] = run_unit_tests()
    
    print("\n2. Running Integration Tests...")
    test_results['integration'] = run_integration_tests()
    
    print("\n3. Running UI Component Tests...")
    test_results['ui'] = run_ui_tests()
    
    print("\n4. Running Full Test Suite...")
    test_results['full'] = run_tests()
    
    print("\n5. Checking Test Coverage...")
    test_results['coverage'] = check_test_coverage()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_type, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_type.title()} Tests: {status}")
    
    all_passed = all(test_results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ TradingInsight application is ready for production!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("Please check the test output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 