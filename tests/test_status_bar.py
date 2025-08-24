#!/usr/bin/env python3
"""
Test module for status bar functionality in the Questionnaire Agent UI.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk

# Add the parent directory to the path so we can import question_answerer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_answerer import QuestionnaireAgentUI


class TestStatusBar(unittest.TestCase):
    """Test status bar functionality."""
    
    def setUp(self):
        """Setup for each test method."""
        # Mock environment variables to prevent Azure connection issues
        self.env_patcher = patch.dict(os.environ, {
            'AZURE_OPENAI_ENDPOINT': 'https://test.services.ai.azure.com/api/projects/test',
            'AZURE_OPENAI_MODEL_DEPLOYMENT': 'gpt-4o-mini'
        })
        self.env_patcher.start()
        
        # Mock Azure client to prevent actual connections
        self.azure_client_patcher = patch('question_answerer.AIProjectClient')
        self.mock_azure_client = self.azure_client_patcher.start()
        
        # Mock tkinter root to avoid display issues
        self.root_patcher = patch('tkinter.Tk')
        self.mock_root = self.root_patcher.start()
        self.mock_root_instance = MagicMock()
        self.mock_root.return_value = self.mock_root_instance
        
        # Create app instance
        self.app = QuestionnaireAgentUI(headless_mode=False)
        
    def tearDown(self):
        """Cleanup after each test method."""
        self.env_patcher.stop()
        self.azure_client_patcher.stop()
        self.root_patcher.stop()
        
    def test_status_bar_initialization(self):
        """Test that status bar variables are initialized correctly."""
        # Check that status variables exist
        self.assertTrue(hasattr(self.app, 'status_working'))
        self.assertTrue(hasattr(self.app, 'status_agent'))
        self.assertTrue(hasattr(self.app, 'status_time'))
        self.assertTrue(hasattr(self.app, 'status_excel_input'))
        self.assertTrue(hasattr(self.app, 'status_excel_output'))
        self.assertTrue(hasattr(self.app, 'status_excel_question'))
        
        # Check initial values
        self.assertEqual(self.app.status_working.get(), "Idle")
        self.assertEqual(self.app.status_agent.get(), "")
        self.assertEqual(self.app.status_time.get(), "00:00")
        
    def test_start_working(self):
        """Test starting working mode."""
        self.app.start_working("Test Agent")
        
        self.assertEqual(self.app.status_working.get(), "Working")
        self.assertEqual(self.app.status_agent.get(), "Test Agent")
        self.assertIsNotNone(self.app.start_time)
        
    def test_stop_working(self):
        """Test stopping working mode."""
        # First start working
        self.app.start_working("Test Agent")
        
        # Then stop
        self.app.stop_working()
        
        self.assertEqual(self.app.status_working.get(), "Idle")
        self.assertEqual(self.app.status_agent.get(), "")
        self.assertEqual(self.app.status_time.get(), "00:00")
        self.assertIsNone(self.app.start_time)
        
    def test_update_agent(self):
        """Test updating the current agent."""
        self.app.update_agent("Answer Checker")
        self.assertEqual(self.app.status_agent.get(), "Answer Checker")
        
        self.app.update_agent("Link Checker")
        self.assertEqual(self.app.status_agent.get(), "Link Checker")
        
    def test_excel_mode(self):
        """Test Excel mode functionality."""
        # Show Excel mode
        self.app.show_excel_mode("/test/input.xlsx", "/test/output.xlsx")
        
        self.assertEqual(self.app.status_excel_input.get(), "input.xlsx")
        self.assertEqual(self.app.status_excel_output.get(), "output.xlsx")
        
        # Update question number
        self.app.update_excel_question(5, 20)
        self.assertEqual(self.app.status_excel_question.get(), "5/20")
        
        # Test without total
        self.app.update_excel_question(3)
        self.assertEqual(self.app.status_excel_question.get(), "3")
        
        # Hide Excel mode
        self.app.hide_excel_mode()
        self.assertEqual(self.app.status_excel_input.get(), "")
        self.assertEqual(self.app.status_excel_output.get(), "")
        self.assertEqual(self.app.status_excel_question.get(), "")
        
    def test_headless_mode_doesnt_break(self):
        """Test that headless mode doesn't break with status bar calls."""
        # Create headless instance
        headless_app = QuestionnaireAgentUI(headless_mode=True)
        
        # These should not raise exceptions
        headless_app.start_working("Test Agent")
        headless_app.update_agent("Answer Checker")
        headless_app.show_excel_mode("/test/input.xlsx", "/test/output.xlsx")
        headless_app.update_excel_question(1, 5)
        headless_app.hide_excel_mode()
        headless_app.stop_working()


if __name__ == '__main__':
    unittest.main()