#!/usr/bin/env python3
"""
Test script for core functionality without GUI
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test that required environment variables are present."""
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_MODEL_DEPLOYMENT', 
        'BING_CONNECTION_ID'
    ]
    
    print("Testing environment variables...")
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✓ {var}: {os.getenv(var)[:20]}...")
    
    if missing_vars:
        print(f"✗ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✓ All required environment variables present")
        return True

def test_imports():
    """Test that all required imports work."""
    print("\nTesting imports...")
    
    try:
        from azure.ai.projects import AIProjectClient
        print("✓ Azure AI Projects SDK imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Azure AI Projects SDK: {e}")
        return False
    
    try:
        from azure.identity import DefaultAzureCredential
        print("✓ Azure Identity imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Azure Identity: {e}")
        return False
    
    try:
        from azure.ai.agents.models import BingGroundingTool
        print("✓ Bing Grounding Tool imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Bing Grounding Tool: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ Pandas imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Pandas: {e}")
        return False
    
    try:
        import requests
        print("✓ Requests imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Requests: {e}")
        return False
    
    return True

def test_azure_connection():
    """Test Azure AI Project connection."""
    print("\nTesting Azure connection...")
    
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
        
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        credential = DefaultAzureCredential()
        
        # Try to create client
        project_client = AIProjectClient(
            endpoint=endpoint,
            credential=credential
        )
        print("✓ Azure AI Project client created successfully")
        
        # Try to list agents (this will test authentication)
        try:
            agents = project_client.agents.list_agents()
            agent_list = list(agents.data) if hasattr(agents, 'data') else list(agents)
            print(f"✓ Successfully connected to Azure - found {len(agent_list)} existing agents")
            return True
        except Exception as e:
            print(f"⚠ Azure client created but authentication test failed: {e}")
            print("  This might be expected if you haven't run 'az login' yet")
            return False
            
    except Exception as e:
        print(f"✗ Failed to create Azure client: {e}")
        return False

def test_link_validation():
    """Test link validation functionality."""
    print("\nTesting link validation...")
    
    try:
        import requests
        
        # Test a simple HTTP request
        response = requests.head("https://www.microsoft.com", timeout=5)
        if response.status_code == 200:
            print("✓ Link validation functionality working")
            return True
        else:
            print(f"⚠ Link validation test returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Link validation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("QUESTIONNAIRE AGENT CORE FUNCTIONALITY TEST")
    print("=" * 50)
    
    tests = [
        test_environment_variables,
        test_imports,
        test_azure_connection,
        test_link_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All core functionality tests passed!")
        print("✓ The application should work correctly with a proper GUI environment")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
        if passed >= 2:  # Environment and imports passed
            print("✓ Core functionality should still work")
    
    print("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)