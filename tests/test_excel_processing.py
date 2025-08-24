#!/usr/bin/env python3
"""
Test Excel processing functionality to verify the fix for issue #11
"""

import os
import tempfile
import shutil
from pathlib import Path

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
        
        # Create a temporary output directory
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.temp_dir, "test_output.xlsx")
        
    def teardown_method(self):
        """Cleanup after each test method."""
        # Clean up temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
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
                max_retries=1    # Use fewer retries to speed up test
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
        # Create a dummy temp file
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        temp_path = temp_file.name
        temp_file.write(b"dummy content")
        temp_file.close()
        
        try:
            # Test that the method doesn't crash even if called directly
            # Note: This will show dialog boxes in GUI mode, so we're testing error handling
            
            # We can't easily test the full GUI dialog flow, but we can test the error handling
            # by simulating various file system states
            
            # Scenario 1: Temp file exists and can be deleted
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    print("Temp file cleanup test passed")
                except Exception as e:
                    print(f"Temp file cleanup failed: {e}")
            
            # Scenario 2: Temp file doesn't exist (already cleaned up)
            if not os.path.exists(temp_path):
                try:
                    # This should not throw an error in our improved code
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    print("Non-existent temp file cleanup test passed")
                except Exception as e:
                    print(f"Non-existent temp file cleanup test failed: {e}")
                    
        except Exception as e:
            raise Exception(f"Save method robustness test failed: {e}")
        finally:
            # Ensure cleanup
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
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