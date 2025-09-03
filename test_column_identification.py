#!/usr/bin/env python3
"""
Test to reproduce the column identification issues described in the issue.
"""

import pandas as pd
import sys
import os

# Add the parent directory to the path so we can import the main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from question_answerer import QuestionnaireAgentUI

def test_mock_column_identification():
    """Test that mock column identification works correctly."""
    print("Testing mock column identification...")
    
    # Create test app in mock mode
    app = QuestionnaireAgentUI(headless_mode=True, mock_mode=True)
    
    # Test case 1: Standard columns with "Response" column
    print("\n=== Test Case 1: DataFrame with 'Question' and 'Response' columns ===")
    df1 = pd.DataFrame({
        'Question': ['What is AI?', 'How does ML work?'],
        'Response': [None, None],
        'Status': ['Pending', 'Pending']
    })
    
    question_col, answer_col, docs_col = app.identify_columns_mock(df1)
    print(f"Identified columns: Question='{question_col}', Answer='{answer_col}', Docs='{docs_col}'")
    
    # Should identify 'Response' as answer column, not 'Status'
    assert answer_col == 'Response', f"Expected 'Response' but got '{answer_col}'"
    assert question_col == 'Question', f"Expected 'Question' but got '{question_col}'"
    
    # Test case 2: Alternative column names
    print("\n=== Test Case 2: DataFrame with 'Questions' and 'Answers' columns ===")
    df2 = pd.DataFrame({
        'Questions': ['What is cloud computing?', 'What is Azure?'],
        'Answers': [None, None],
        'Documentation': [None, None]
    })
    
    question_col, answer_col, docs_col = app.identify_columns_mock(df2)
    print(f"Identified columns: Question='{question_col}', Answer='{answer_col}', Docs='{docs_col}'")
    
    # Should identify 'Answers' as answer column
    assert answer_col == 'Answers', f"Expected 'Answers' but got '{answer_col}'"
    assert question_col == 'Questions', f"Expected 'Questions' but got '{question_col}'"
    assert docs_col == 'Documentation', f"Expected 'Documentation' but got '{docs_col}'"
    
    # Test case 3: Check priority - Response should be preferred over other terms
    print("\n=== Test Case 3: DataFrame with multiple answer-like columns ===")
    df3 = pd.DataFrame({
        'Question': ['What is the answer?'],
        'Status': ['Pending'],
        'Reply': [None],
        'Response': [None]  # This should be preferred
    })
    
    question_col, answer_col, docs_col = app.identify_columns_mock(df3)
    print(f"Identified columns: Question='{question_col}', Answer='{answer_col}', Docs='{docs_col}'")
    
    # Should prefer 'Response' over 'Reply' or 'Status'
    assert answer_col == 'Response', f"Expected 'Response' but got '{answer_col}' - Response should be preferred"
    
    print("\n✓ All mock column identification tests passed!")

def test_cli_vs_non_cli_methods():
    """Test that there's no duplicate implementation."""
    print("\n=== Testing for duplicate implementations ===")
    
    app = QuestionnaireAgentUI(headless_mode=True, mock_mode=True)
    
    # Check if both methods exist
    has_cli_method = hasattr(app, 'identify_columns_with_llm_cli')
    has_non_cli_method = hasattr(app, 'identify_columns_with_llm')
    
    print(f"Has CLI method: {has_cli_method}")
    print(f"Has non-CLI method: {has_non_cli_method}")
    
    if has_non_cli_method:
        print("WARNING: Found duplicate identify_columns_with_llm method that should be removed")
        
        # Check if the non-CLI method is actually used
        with open('question_answerer.py', 'r') as f:
            content = f.read()
            
        # Look for calls to the non-CLI method (excluding the method definition itself)
        lines = content.split('\n')
        calls_to_non_cli = []
        for i, line in enumerate(lines):
            if 'identify_columns_with_llm(' in line and 'def identify_columns_with_llm(' not in line:
                calls_to_non_cli.append((i+1, line.strip()))
        
        print(f"Found {len(calls_to_non_cli)} calls to non-CLI method:")
        for line_num, line in calls_to_non_cli:
            print(f"  Line {line_num}: {line}")

if __name__ == "__main__":
    try:
        test_mock_column_identification()
        test_cli_vs_non_cli_methods()
        print("\n🎉 All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)