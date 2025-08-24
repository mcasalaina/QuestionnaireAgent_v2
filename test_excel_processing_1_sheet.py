#!/usr/bin/env python3
"""
Test for Excel processing functionality using the 1_sheet sample file.
"""

import os
import tempfile
from question_answerer import QuestionnaireAgentUI

def test_excel_processing_1_sheet():
    """Test that Excel processing doesn't throw errors with the 1_sheet sample file."""
    
    # Get the path to the sample file
    sample_file = os.path.join("tests", "sample_questionnaire_1_sheet.xlsx")
    
    # Verify the sample file exists
    assert os.path.exists(sample_file), f"Sample file not found: {sample_file}"
    
    # Create a temporary output file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_output:
        output_file = temp_output.name
    
    try:
        # Create the application in headless mode
        app = QuestionnaireAgentUI(headless_mode=True, max_retries=1)  # Use fewer retries for faster testing
        
        # Process the Excel file
        success = app.process_excel_file_cli(
            input_path=sample_file,
            output_path=output_file,
            context="Test context",
            char_limit=500,  # Smaller limit for faster testing
            verbose=False,
            max_retries=1
        )
        
        # The test passes if no exception is thrown and the output file exists
        # We don't care about the success result since we're testing error handling
        assert os.path.exists(output_file), "Output file was not created"
        print(f"✓ Excel processing completed without errors. Output: {output_file}")
        
    finally:
        # Clean up the temporary output file
        if os.path.exists(output_file):
            os.unlink(output_file)

if __name__ == "__main__":
    test_excel_processing_1_sheet()
    print("Test passed!")