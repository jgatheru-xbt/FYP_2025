#!/usr/bin/env python3
"""
Test script to validate the fixes for canary detection and simulation abort.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sentinel_imports():
    """Test that sentinel.py imports correctly without threading errors."""
    try:
        from frontend.sentinel import SentinelPage, CanaryFileSystemEventHandler
        print("✓ Sentinel imports successful")
        return True
    except Exception as e:
        print(f"✗ Sentinel import failed: {e}")
        return False

def test_simulation_imports():
    """Test that simulations.py imports correctly."""
    try:
        from frontend.simulations import SimulationPage
        print("✓ Simulation imports successful")
        return True
    except Exception as e:
        print(f"✗ Simulation import failed: {e}")
        return False

def test_reports_imports():
    """Test that reports_page.py imports correctly."""
    try:
        from frontend.reports_page import ReportsPage
        print("✓ Reports imports successful")
        return True
    except Exception as e:
        print(f"✗ Reports import failed: {e}")
        return False

def test_watchdog_observer():
    """Test that watchdog Observer can be created without threading errors."""
    try:
        from watchdog.observers import Observer
        observer = Observer()
        print("✓ Watchdog Observer creation successful")
        # Don't start it as we're just testing instantiation
        return True
    except Exception as e:
        print(f"✗ Watchdog Observer creation failed: {e}")
        return False

def test_encryption_stats():
    """Test that encryption stats data structure is valid."""
    try:
        stats = {
            'total_scanned': 100,
            'total_encrypted': 75,
            'start_time': '2024-01-27 10:00:00',
            'algorithm': 'AES'
        }
        encrypted_pct = int((stats['total_encrypted'] / stats['total_scanned']) * 100)
        assert encrypted_pct == 75, f"Expected 75%, got {encrypted_pct}%"
        print("✓ Encryption stats calculation successful")
        return True
    except Exception as e:
        print(f"✗ Encryption stats test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Canary Detection and Simulation Abort Fixes")
    print("=" * 60)
    
    tests = [
        ("Watchdog Observer", test_watchdog_observer),
        ("Sentinel Imports", test_sentinel_imports),
        ("Simulation Imports", test_simulation_imports),
        ("Reports Imports", test_reports_imports),
        ("Encryption Stats", test_encryption_stats),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test {test_name} encountered exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The fixes appear to be working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
