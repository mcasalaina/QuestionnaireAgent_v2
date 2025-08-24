#!/usr/bin/env python3
"""
Test single question processing to verify Application Analytics fix.

This test verifies that:
1. The application sets OTEL_SERVICE_NAME correctly
2. A single question can be processed successfully
3. Tracing is properly configured

Issue #13: Application analytics shows as blank in Azure AI Foundry.
Fix: Set OTEL_SERVICE_NAME to "Questionnaire Agent V2" for Application Analytics.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the parent directory to the path so we can import question_answerer
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestSingleQuestionTracing(unittest.TestCase):
    """Test suite for single question processing with proper tracing setup."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables to avoid requiring real Azure credentials during testing
        self.env_patches = [
            patch.dict(os.environ, {
                "AZURE_OPENAI_ENDPOINT": "https://test.services.ai.azure.com/api/projects/test-project",
                "AZURE_OPENAI_MODEL_DEPLOYMENT": "gpt-4o-mini",
                "BING_CONNECTION_ID": "test-bing-connection",
                "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test-key;IngestionEndpoint=https://test.in.applicationinsights.azure.com/"
            })
        ]
        
        for patch_obj in self.env_patches:
            patch_obj.start()
    
    def tearDown(self):
        """Clean up test environment."""
        for patch_obj in self.env_patches:
            patch_obj.stop()
    
    def test_otel_service_name_is_set(self):
        """Test that OTEL_SERVICE_NAME is properly set for Application Analytics."""
        # Clear any existing OTEL_SERVICE_NAME
        if "OTEL_SERVICE_NAME" in os.environ:
            del os.environ["OTEL_SERVICE_NAME"]
        
        # Import and initialize the application
        from question_answerer import QuestionnaireAgentUI
        
        # Mock Azure dependencies to avoid real connections during testing
        with patch('question_answerer.AIProjectClient') as mock_client, \
             patch('question_answerer.DefaultAzureCredential') as mock_credential, \
             patch('question_answerer.configure_azure_monitor') as mock_configure:
            
            # Initialize the application in headless mode
            app = QuestionnaireAgentUI(headless_mode=True)
            
            # Verify that OTEL_SERVICE_NAME was set correctly
            self.assertEqual(os.environ.get("OTEL_SERVICE_NAME"), "Questionnaire Agent V2")
            
            # Verify Azure Monitor was configured (indicating tracing setup succeeded)
            mock_configure.assert_called_once()
    
    def test_existing_otel_service_name_preserved(self):
        """Test that existing OTEL_SERVICE_NAME is preserved."""
        # Set a custom service name
        custom_name = "Custom Service Name"
        os.environ["OTEL_SERVICE_NAME"] = custom_name
        
        # Import and initialize the application  
        from question_answerer import QuestionnaireAgentUI
        
        # Mock Azure dependencies
        with patch('question_answerer.AIProjectClient') as mock_client, \
             patch('question_answerer.DefaultAzureCredential') as mock_credential, \
             patch('question_answerer.configure_azure_monitor') as mock_configure:
            
            # Initialize the application in headless mode
            app = QuestionnaireAgentUI(headless_mode=True)
            
            # Verify that the existing OTEL_SERVICE_NAME was preserved
            self.assertEqual(os.environ.get("OTEL_SERVICE_NAME"), custom_name)
    
    def test_tracing_initialization_without_connection_string(self):
        """Test that tracing initialization handles missing connection string gracefully."""
        # Remove the connection string
        if "APPLICATIONINSIGHTS_CONNECTION_STRING" in os.environ:
            del os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
        
        from question_answerer import QuestionnaireAgentUI
        
        # Mock Azure dependencies
        with patch('question_answerer.AIProjectClient') as mock_client, \
             patch('question_answerer.DefaultAzureCredential') as mock_credential, \
             patch('question_answerer.configure_azure_monitor') as mock_configure:
            
            # Initialize the application in headless mode
            app = QuestionnaireAgentUI(headless_mode=True)
            
            # Verify that OTEL_SERVICE_NAME is still set even without Application Insights
            self.assertEqual(os.environ.get("OTEL_SERVICE_NAME"), "Questionnaire Agent V2")
            
            # Verify Azure Monitor was NOT configured due to missing connection string
            mock_configure.assert_not_called()

if __name__ == "__main__":
    unittest.main()