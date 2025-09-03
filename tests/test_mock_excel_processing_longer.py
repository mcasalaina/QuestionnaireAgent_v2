#!/usr/bin/env python3
"""
Test for Excel processing functionality using the longer sample file with mock mode.
"""

import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from question_answerer import QuestionnaireAgentUI

def test_mock_excel_processing_longer():
    """Test that Excel processing doesn't throw errors with the longer sample file using mock mode."""
    
    # Get the path to the sample file
    sample_file = os.path.join("tests", "sample_questionnaire_longer.xlsx")
    
    # Verify the sample file exists
    assert os.path.exists(sample_file), f"Sample file not found: {sample_file}"
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output file in the output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"test_mock_excel_processing_longer_output_{timestamp}.xlsx")
    
    try:
        # Create the application in headless mode with mock enabled
        app = QuestionnaireAgentUI(headless_mode=True, max_retries=1, mock_mode=True)  # Use fewer retries and enable mock mode
        
        # Process the Excel file
        success = app.process_excel_file_cli(
            input_path=sample_file,
            output_path=output_file,
            context="Microsoft Azure",
            char_limit=500,  # Smaller limit for faster testing
            verbose=True,  # Enable verbose output to see reasoning
            max_retries=3
        )
        
        # The test passes if no exception is thrown and the method succeeds
        # Mock mode should always succeed
        assert success, "Mock Excel processing should succeed"
        assert os.path.exists(output_file), "Output file was not created"
        print(f"✓ Mock Excel processing completed successfully. Output saved to: {output_file}")
        
    except Exception as e:
        # Clean up the output file if there was an error
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise e

if __name__ == "__main__":
    test_mock_excel_processing_longer()
    print("Mock test passed!")