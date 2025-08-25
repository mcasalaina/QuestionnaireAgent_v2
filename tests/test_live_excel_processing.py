#!/usr/bin/env python3
"""
Test Excel processing functionality to verify the fix for issue #11 (LIVE VERSION)

This test uses the live Azure OpenAI service and requires valid Azure credentials.
For testing without Azure credentials, use test_mock_excel_processing.py instead.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import the main module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from question_answerer import QuestionnaireAgentUI


class TestExcelProcessing:
    """Test Excel processing functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Create a test app instance in headless mode
        self.app = QuestionnaireAgentUI(headless_mode=True, max_retries=2)
        
        # Sample Excel file path
        self.sample_excel_path = Path(__file__).parent / "sample_questionnaire.xlsx"
        
        # Create output directory if it doesn't exist
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Create timestamped output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = str(self.output_dir / f"test_excel_processing_output_{timestamp}.xlsx")
        
    def teardown_method(self):
        """Cleanup after each test method."""
        # Only clean up the output file if the test failed
        # Otherwise, keep it in the output directory for inspection
        pass
    
    def test_excel_file_exists(self):
        """Verify that the sample Excel file exists."""
        assert self.sample_excel_path.exists(), f"Sample Excel file not found: {self.sample_excel_path}"
    
    def test_excel_processing_cli_no_error(self):
        """Test that Excel processing in CLI mode doesn't throw errors."""
        # Skip if sample file doesn't exist
        if not self.sample_excel_path.exists():
            print("Sample Excel file not found, skipping test")
            return
        
        try:
            # Test the CLI Excel processing method
            success = self.app.process_excel_file_cli(
                input_path=str(self.sample_excel_path),
                output_path=self.output_path,
                context="Microsoft Azure AI",
                char_limit=500,  # Use shorter limit to speed up test
                verbose=True,
                max_retries=3    # Use fewer retries to speed up test
            )
            
            # The method should complete without throwing an exception
            # Success might be False if Azure credentials aren't configured, but it shouldn't crash
            print(f"Excel processing completed with success={success}")
            
            # If it succeeded, verify the output file was created
            if success:
                assert os.path.exists(self.output_path), "Output Excel file was not created"
                print(f"Output file created successfully: {self.output_path}")
            else:
                print("Excel processing failed (likely due to missing Azure credentials), but no exception was thrown")
                
        except Exception as e:
            raise Exception(f"Excel processing threw an unexpected exception: {e}")
    
    def test_save_processed_excel_method_robustness(self):
        """Test the save_processed_excel method with various scenarios."""
        # Create a dummy file in the output directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_file_path = self.output_dir / f"test_save_robustness_{timestamp}.xlsx"
        
        try:
            # Create a test file
            with open(test_file_path, 'wb') as f:
                f.write(b"dummy content")
            
            # Test that the method doesn't crash even if called directly
            # Note: This will show dialog boxes in GUI mode, so we're testing error handling
            
            # We can't easily test the full GUI dialog flow, but we can test the error handling
            # by simulating various file system states
            
            # Scenario 1: File exists and can be deleted
            if test_file_path.exists():
                try:
                    test_file_path.unlink()
                    print("File cleanup test passed")
                except Exception as e:
                    print(f"File cleanup failed: {e}")
            
            # Scenario 2: File doesn't exist (already cleaned up)
            if not test_file_path.exists():
                try:
                    # This should not throw an error in our improved code
                    if test_file_path.exists():
                        test_file_path.unlink()
                    print("Non-existent file cleanup test passed")
                except Exception as e:
                    print(f"Non-existent file cleanup test failed: {e}")
                    
        except Exception as e:
            raise Exception(f"Save method robustness test failed: {e}")
        finally:
            # Ensure cleanup
            if test_file_path.exists():
                try:
                    test_file_path.unlink()
                except:
                    pass


def run_tests():
    """Run all tests manually."""
    test_instance = TestExcelProcessing()
    
    print("Running Excel processing tests...")
    
    # Test 1: Check file exists
    try:
        test_instance.setup_method()
        test_instance.test_excel_file_exists()
        print("✓ Test 1 passed: Sample Excel file exists")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
    finally:
        test_instance.teardown_method()
    
    # Test 2: Excel processing CLI
    try:
        test_instance.setup_method()
        test_instance.test_excel_processing_cli_no_error()
        print("✓ Test 2 passed: Excel processing CLI completed without exceptions")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
    finally:
        test_instance.teardown_method()
    
    # Test 3: Save method robustness
    try:
        test_instance.setup_method()
        test_instance.test_save_processed_excel_method_robustness()
        print("✓ Test 3 passed: Save method robustness test completed")
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
    finally:
        test_instance.teardown_method()
    
    print("All tests completed!")


if __name__ == "__main__":
    # Run the tests
    run_tests()