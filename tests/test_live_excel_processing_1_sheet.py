#!/usr/bin/env python3
"""
Test for Excel processing functionality using the 1_sheet sample file (LIVE VERSION).

This test uses the live Azure OpenAI service and requires valid Azure credentials.
For testing without Azure credentials, use test_mock_excel_processing_1_sheet.py instead.
"""

import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from question_answerer import QuestionnaireAgentUI

def test_excel_processing_1_sheet():
    """Test that Excel processing doesn't throw errors with the 1_sheet sample file."""
    
    # Get the path to the sample file
    sample_file = os.path.join("tests", "sample_questionnaire_1_sheet.xlsx")
    
    # Verify the sample file exists
    assert os.path.exists(sample_file), f"Sample file not found: {sample_file}"
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output file in the output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"test_excel_processing_1_sheet_output_{timestamp}.xlsx")
    
    try:
        # Create the application in headless mode
        app = QuestionnaireAgentUI(headless_mode=True, max_retries=1)  # Use fewer retries for faster testing
        
        # Process the Excel file
        success = app.process_excel_file_cli(
            input_path=sample_file,
            output_path=output_file,
            context="Microsoft Azure",
            char_limit=500,  # Smaller limit for faster testing
            verbose=True,  # Enable verbose output to see reasoning
            max_retries=10
        )
        
        # The test passes if no exception is thrown and the output file exists
        # We don't care about the success result since we're testing error handling
        assert os.path.exists(output_file), "Output file was not created"
        print(f"✓ Excel processing completed without errors. Output saved to: {output_file}")
        
    except Exception as e:
        # Clean up the output file if there was an error
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise e

if __name__ == "__main__":
    test_excel_processing_1_sheet()
    print("Test passed!")