"""
Mock test for Azure-related questions using question_answerer.py with mock mode.

This test runs Azure questions through the mock question answerer system
and verifies that it returns meaningful results. It uses mock mode and does not
require Azure credentials to function.
"""

import unittest
import sys
import os

# Add the parent directory to Python path to import question_answerer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_answerer import QuestionnaireAgentUI


class TestMockAzureQuestion(unittest.TestCase):
    """Test Azure questions with mock mode."""
    
    def setUp(self):
        """Set up test environment."""
        self.agent = QuestionnaireAgentUI(headless_mode=True, mock_mode=True)
        
    def test_mock_azure_question(self):
        """Test a mock Azure Storage question."""
        # Test question about Azure Storage
        question = "What are the different types of Azure Storage accounts and their use cases?"
        context = "Microsoft Azure AI"
        char_limit = 3000  # Increased from 2000 to allow for longer answers
        max_retries = 3
        
        # Call the mock question answering method
        success, answer, links = self.agent.process_single_question_cli(
            question, context, char_limit, verbose=True, max_retries=max_retries
        )
        
        # Verify we got a successful result
        self.assertTrue(success, "Mock question processing should succeed")
        self.assertIsNotNone(answer, "Should receive an answer from mock Azure question")
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
        
        # Verify links (should contain microsoft.com)
        self.assertIsInstance(links, list, "Links should be a list")
        self.assertGreater(len(links), 0, "Links should not be empty in mock mode")
        
        # Check that at least one link contains microsoft.com
        microsoft_link_found = False
        for link in links:
            if "microsoft.com" in link.lower():
                microsoft_link_found = True
                break
        
        self.assertTrue(microsoft_link_found, "Links should include microsoft.com")
        
        print(f"\n✓ Successfully processed mock Azure question: {question}")
        print(f"✓ Answer length: {len(answer)} characters")
        print(f"✓ Number of links: {len(links)}")
        if answer:
            print(f"✓ Answer preview: {answer[:100]}...")
        
    def test_mock_video_ai_question(self):
        """Test a mock video AI question."""
        question = "Does your service offer video generative AI?"
        context = "Microsoft Azure AI"
        char_limit = 2000
        max_retries = 1
        
        # Call the mock question answering method
        success, answer, links = self.agent.process_single_question_cli(
            question, context, char_limit, verbose=True, max_retries=max_retries
        )
        
        # Verify we got a successful result
        self.assertTrue(success, "Mock question processing should succeed")
        self.assertIsNotNone(answer, "Should receive an answer from mock question")
        self.assertIsInstance(answer, str, "Answer should be a string")
        self.assertGreater(len(answer), 30, "Answer should have reasonable length")
        
        # Check that answer mentions relevant concepts
        relevant_keywords = ['video', 'ai', 'artificial intelligence', 'services']
        answer_lower = answer.lower()
        
        keyword_found = False
        for keyword in relevant_keywords:
            if keyword in answer_lower:
                keyword_found = True
                break
        
        self.assertTrue(keyword_found, "Answer should mention relevant concepts")
        
        # Verify links
        self.assertIsInstance(links, list, "Links should be a list")
        self.assertGreater(len(links), 0, "Links should not be empty in mock mode")
        
        print(f"\n✓ Successfully processed mock video AI question: {question}")
        print(f"✓ Answer length: {len(answer)} characters")
        print(f"✓ Number of links: {len(links)}")
        
    def test_mock_mode_always_succeeds(self):
        """Test that mock mode always returns successful results."""
        questions = [
            "What is cloud computing?",
            "How does machine learning work?",
            "What are the benefits of using AI?",
        ]
        
        for question in questions:
            with self.subTest(question=question):
                success, answer, links = self.agent.process_single_question_cli(
                    question, "Technology", 1000, verbose=False, max_retries=1
                )
                
                self.assertTrue(success, f"Mock mode should always succeed for: {question}")
                self.assertIsInstance(answer, str, "Answer should be a string")
                self.assertGreater(len(answer), 10, "Answer should have reasonable length")
                self.assertIsInstance(links, list, "Links should be a list")
                self.assertGreater(len(links), 0, "Links should not be empty")


if __name__ == '__main__':
    # Set up test environment
    print("Running mock Azure question test...")
    print("Note: This test uses mock mode and does NOT require Azure credentials.")
    
    unittest.main(verbosity=2)