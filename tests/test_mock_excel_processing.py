#!/usr/bin/env python3
"""
Test Excel processing functionality using mock mode (no Azure credentials required).
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import the main module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from question_answerer import QuestionnaireAgentUI


class TestMockExcelProcessing:
    """Test Excel processing functionality with mock mode."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Create a test app instance in headless mode with mock enabled
        self.app = QuestionnaireAgentUI(headless_mode=True, max_retries=2, mock_mode=True)
        
        # Sample Excel file path
        self.sample_excel_path = Path(__file__).parent / "sample_questionnaire.xlsx"
        
        # Create output directory if it doesn't exist
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Create timestamped output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = str(self.output_dir / f"test_mock_excel_processing_output_{timestamp}.xlsx")
        
    def teardown_method(self):
        """Cleanup after each test method."""
        # Only clean up the output file if the test failed
        # Otherwise, keep it in the output directory for inspection
        pass
    
    def test_excel_file_exists(self):
        """Verify that the sample Excel file exists."""
        assert self.sample_excel_path.exists(), f"Sample Excel file not found: {self.sample_excel_path}"
    
    def test_mock_excel_processing_cli_no_error(self):
        """Test that Excel processing in CLI mode doesn't throw errors with mock mode."""
        # Skip if sample file doesn't exist
        if not self.sample_excel_path.exists():
            print("Sample Excel file not found, skipping test")
            return
        
        try:
            # Test the CLI Excel processing method with mock mode
            success = self.app.process_excel_file_cli(
                input_path=str(self.sample_excel_path),
                output_path=self.output_path,
                context="Microsoft Azure AI",
                char_limit=500,  # Use shorter limit to speed up test
                verbose=True,
                max_retries=3    # Use fewer retries to speed up test
            )
            
            # The method should complete without throwing an exception
            # Success should be True since we're using mock mode
            print(f"Mock Excel processing completed with success={success}")
            
            # Verify the output file was created
            assert success, "Mock Excel processing should succeed"
            assert os.path.exists(self.output_path), "Output Excel file was not created"
            print(f"Output file created successfully: {self.output_path}")
                
        except Exception as e:
            raise Exception(f"Mock Excel processing threw an unexpected exception: {e}")
    
    def test_mock_single_question(self):
        """Test that a single question works in mock mode."""
        try:
            # Test a single question with mock mode
            success, answer, links = self.app.process_single_question_cli(
                question="What is Azure Storage?",
                context="Microsoft Azure AI",
                char_limit=500,
                verbose=True,
                max_retries=1
            )
            
            # Mock mode should always succeed
            assert success, "Mock question processing should succeed"
            assert answer is not None, "Mock answer should not be None"
            assert isinstance(answer, str), "Mock answer should be a string"
            assert len(answer) > 0, "Mock answer should not be empty"
            assert isinstance(links, list), "Mock links should be a list"
            assert len(links) > 0, "Mock links should contain at least one URL"
            assert "microsoft.com" in links[0].lower(), "Mock links should include microsoft.com"
            
            print(f"✓ Mock question processed successfully")
            print(f"✓ Answer: {answer[:100]}...")
            print(f"✓ Links: {links}")
            
        except Exception as e:
            raise Exception(f"Mock single question processing failed: {e}")


def run_tests():
    """Run all tests manually."""
    test_instance = TestMockExcelProcessing()
    
    print("Running Mock Excel processing tests...")
    
    # Test 1: Check file exists
    try:
        test_instance.setup_method()
        test_instance.test_excel_file_exists()
        print("✓ Test 1 passed: Sample Excel file exists")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
    finally:
        test_instance.teardown_method()
    
    # Test 2: Mock single question
    try:
        test_instance.setup_method()
        test_instance.test_mock_single_question()
        print("✓ Test 2 passed: Mock single question processing")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
    finally:
        test_instance.teardown_method()
    
    # Test 3: Mock Excel processing CLI
    try:
        test_instance.setup_method()
        test_instance.test_mock_excel_processing_cli_no_error()
        print("✓ Test 3 passed: Mock Excel processing CLI completed without exceptions")
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
    finally:
        test_instance.teardown_method()
    
    print("All mock tests completed!")


if __name__ == "__main__":
    # Run the tests
    run_tests()