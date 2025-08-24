#!/usr/bin/env python3
"""
Test for UI question box clearing functionality during Excel import.
"""

import os
import sys
import unittest
import tkinter as tk
from unittest.mock import Mock, patch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from question_answerer import QuestionnaireAgentUI

class TestUIQuestionClearing(unittest.TestCase):
    """Test UI question box clearing during Excel import."""
    
    def test_question_box_cleared_on_excel_import_start(self):
        """Test that question box is cleared when Excel import starts."""
        # Create the application in non-headless mode to test UI components
        # But mock the tkinter components to avoid display requirements
        with patch.dict(os.environ, {'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com'}), \
             patch('tkinter.Tk'), \
             patch('tkinter.ttk.Notebook'), \
             patch('tkinter.scrolledtext.ScrolledText'), \
             patch('azure.ai.projects.AIProjectClient'), \
             patch('azure.identity.DefaultAzureCredential'):
            
            # Create mock text widgets
            mock_question_text = Mock()
            mock_reasoning_text = Mock()
            
            # Create app with UI components
            app = QuestionnaireAgentUI(headless_mode=False, max_retries=1)
            
            # Manually assign our mock text widgets
            app.question_text = mock_question_text
            app.reasoning_text = mock_reasoning_text
            app.notebook = Mock()
            
            # Mock the file dialogs to simulate user selection
            with patch('tkinter.filedialog.askopenfilename', return_value='input.xlsx'), \
                 patch('tkinter.filedialog.asksaveasfilename', return_value='output.xlsx'), \
                 patch('threading.Thread') as mock_thread:
                
                # Call the import Excel method
                app.on_import_excel_clicked()
                
                # Verify that reasoning text was cleared (use tk.END)
                mock_reasoning_text.delete.assert_called_with(1.0, tk.END)
                
                # Verify that question text was cleared (this is the fix we're testing)
                mock_question_text.delete.assert_called_with(1.0, tk.END)
                
                # Verify that notebook switched to reasoning tab
                app.notebook.select.assert_called_with(2)
                
                # Verify that Excel processing thread was started
                mock_thread.assert_called_once()

if __name__ == '__main__':
    unittest.main()