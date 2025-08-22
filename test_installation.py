#!/usr/bin/env python3
"""
Test script to verify the questionnaire agent installation and basic functionality.
"""

import sys
import os

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from main import QuestionnaireAgent
        print("✓ Main module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import main module: {e}")
        return False
    
    try:
        from agents.question_answerer import QuestionAnswerer
        print("✓ QuestionAnswerer imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import QuestionAnswerer: {e}")
        return False
    
    try:
        from agents.answer_checker import AnswerChecker
        print("✓ AnswerChecker imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import AnswerChecker: {e}")
        return False
    
    try:
        from agents.link_checker import LinkChecker
        print("✓ LinkChecker imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import LinkChecker: {e}")
        return False
    
    try:
        from utils.web_search import WebSearcher
        print("✓ WebSearcher imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import WebSearcher: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality without making external calls."""
    print("\nTesting basic functionality...")
    
    try:
        from main import QuestionnaireAgent
        agent = QuestionnaireAgent()
        print("✓ QuestionnaireAgent instantiated successfully")
    except Exception as e:
        print(f"✗ Failed to instantiate QuestionnaireAgent: {e}")
        return False
    
    try:
        from utils.web_search import WebSearcher
        searcher = WebSearcher()
        print("✓ WebSearcher instantiated successfully")
    except Exception as e:
        print(f"✗ Failed to instantiate WebSearcher: {e}")
        return False
    
    return True

def test_cli_help():
    """Test that the CLI help works."""
    print("\nTesting CLI help...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "Web-Based Questionnaire Answering Agent" in result.stdout:
            print("✓ CLI help works correctly")
            return True
        else:
            print(f"✗ CLI help failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to test CLI help: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Questionnaire Agent Installation Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_basic_functionality,
        test_cli_help
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The installation appears to be working correctly.")
        print("\nYou can now run the questionnaire agent with:")
        print('python main.py "Why is the sky blue?"')
    else:
        print("✗ Some tests failed. Please check the installation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
