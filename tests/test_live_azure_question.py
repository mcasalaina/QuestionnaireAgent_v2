"""
Live test for Azure-related questions using question_answerer.py with no mocks.

This test runs actual Azure questions through the question answerer system
and verifies that it returns meaningful results. It does not mock any components
and requires valid Azure credentials to function.
"""

import unittest
import sys
import os

# Add the parent directory to Python path to import question_answerer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_answerer import QuestionnaireAgentUI


class TestLiveAzureQuestion(unittest.TestCase):
    """Test live Azure questions without mocks."""
    
    def setUp(self):
        """Set up test environment."""
        self.agent = QuestionnaireAgentUI(headless_mode=True)
        
    def test_live_azure_question(self):
        """Test a live question about Azure Storage."""
        # Test question about Azure Storage
        question = "What are the different types of Azure Storage accounts and their use cases?"
        context = "Microsoft Azure AI"
        char_limit = 3000  # Increased from 2000 to allow for longer answers
        max_retries = 3
        
        # Call the actual question answering method with correct parameters
        try:
            success, answer, links = self.agent.process_single_question_cli(
                question, context, char_limit, verbose=True, max_retries=max_retries
            )
            
            # Verify we got a successful result
            self.assertTrue(success, "Question processing should succeed")
            self.assertIsNotNone(answer, "Should receive an answer from Azure question")
            self.assertIsInstance(answer, str, "Answer should be a string")
            self.assertGreater(len(answer), 50, "Answer should be substantial (>50 chars)")
            
            # Check that answer mentions Azure Storage concepts
            azure_keywords = ['azure', 'storage']
            answer_lower = answer.lower()
            
            keyword_found = False
            for keyword in azure_keywords:
                if keyword in answer_lower:
                    keyword_found = True
                    break
            
            self.assertTrue(keyword_found, "Answer should mention Azure Storage concepts")
            
            # Verify links (may be empty, but should be a list)
            self.assertIsInstance(links, list, "Links should be a list")
            
            print(f"\n✓ Successfully processed Azure question: {question}")
            print(f"✓ Answer length: {len(answer)} characters")
            print(f"✓ Number of links: {len(links)}")
            if answer:
                print(f"✓ Answer preview: {answer[:100]}...")
            
        except Exception as e:
            # If the test fails due to configuration issues, provide helpful message
            if "AZURE_OPENAI_ENDPOINT" in str(e) or "az login" in str(e):
                self.skipTest(f"Azure configuration required: {e}")
            else:
                # Re-raise other exceptions as actual test failures
                raise


if __name__ == '__main__':
    # Set up test environment
    print("Running live Azure question test...")
    print("Note: This test requires valid Azure credentials and network access.")
    
    unittest.main(verbosity=2)