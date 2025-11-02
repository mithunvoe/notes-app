"""
Simple test script to verify the API is working.
Run this after starting the services with docker-compose up.
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"


def print_section(title):
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)


def test_health():
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API is healthy")
            print(f"  Status: {data['status']}")
            print(f"  Chroma chunks: {data['chroma']['total_chunks']}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        return False


def test_root():
    print_section("Testing Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Root endpoint working")
            print(f"  Version: {data['version']}")
            return True
        else:
            print(f"✗ Root endpoint failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_documentation():
    print_section("Testing API Documentation")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print(f"✓ Swagger UI available at: {BASE_URL}/docs")
        else:
            print(f"✗ Swagger UI not available")
            
        response = requests.get(f"{BASE_URL}/redoc")
        if response.status_code == 200:
            print(f"✓ ReDoc available at: {BASE_URL}/redoc")
            return True
        else:
            print(f"✗ ReDoc not available")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("\n" + "=" * 50)
    print(" PDF Notes API - Quick Test")
    print("=" * 50)
    
    print("\nMake sure the services are running:")
    print("  docker-compose up")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    results.append(("Documentation", test_documentation()))
    
    # Summary
    print_section("Test Summary")
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! API is ready to use.")
        print("\nNext steps:")
        print("  1. Visit the API docs: http://localhost:8000/docs")
        print("  2. Try uploading a PDF using the /upload endpoint")
        print("  3. Monitor tasks at: http://localhost:5555 (Flower)")
    else:
        print("\n✗ Some tests failed. Please check the logs:")
        print("  docker-compose logs")
        sys.exit(1)


if __name__ == "__main__":
    main()
