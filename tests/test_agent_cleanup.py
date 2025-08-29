"""
Test module for agent cleanup functionality in QuestionnaireAgentUI.

Tests that agents are properly cleaned up when the application closes,
leveraging the existing FoundryAgentSession infrastructure.
"""

import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os

# Add the parent directory to the Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Azure dependencies before importing
mock_azure_modules = {
    'azure': MagicMock(),
    'azure.monitor': MagicMock(),
    'azure.monitor.opentelemetry': MagicMock(),
    'azure.ai': MagicMock(),
    'azure.ai.projects': MagicMock(),
    'azure.identity': MagicMock(),
    'azure.ai.agents': MagicMock(),
    'azure.ai.agents.models': MagicMock(),
    'opentelemetry': MagicMock(),
    'opentelemetry.trace': MagicMock(),
    'pandas': MagicMock(),
    'tkinter': MagicMock(),
    'tkinter.ttk': MagicMock(),
    'tkinter.scrolledtext': MagicMock(),
    'tkinter.messagebox': MagicMock(),
    'tkinter.filedialog': MagicMock(),
}

with patch.dict('sys.modules', mock_azure_modules):
    from question_answerer import QuestionnaireAgentUI
    from utils.resource_manager import FoundryAgentSession


class TestAgentCleanup(unittest.TestCase):
    """Test suite for agent cleanup functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock client for FoundryAgentSession
        self.mock_client = MagicMock()
        
        # Configure mock agent and thread responses
        self.mock_agent = MagicMock()
        self.mock_agent.id = "test-agent-123"
        self.mock_thread = MagicMock()
        self.mock_thread.id = "test-thread-456"
        
        self.mock_client.agents.create_agent.return_value = self.mock_agent
        self.mock_client.agents.threads.create.return_value = self.mock_thread
        
    @patch.dict('sys.modules', mock_azure_modules)
    @patch('question_answerer.signal.signal')
    @patch('question_answerer.atexit.register')
    def test_cleanup_handlers_registration(self, mock_atexit_register, mock_signal_signal):
        """Test that cleanup handlers are properly registered during initialization."""
        with patch('question_answerer.QuestionnaireAgentUI.init_azure_client'):
            # Test in headless mode to avoid GUI complications
            app = QuestionnaireAgentUI(headless_mode=True, mock_mode=True)
            
            # Verify atexit handler was registered
            mock_atexit_register.assert_called_once_with(app.cleanup_agents)
            
            # Verify signal handlers were registered (2 calls: SIGINT and SIGTERM)
            self.assertEqual(mock_signal_signal.call_count, 2)
        
    def test_cleanup_agents_mock_mode(self):
        """Test that cleanup_agents gracefully handles mock mode."""
        with patch('question_answerer.QuestionnaireAgentUI.init_azure_client'):
            app = QuestionnaireAgentUI(headless_mode=True, mock_mode=True)
            
            # Set up mock agent IDs as if agents were created
            app.question_answerer_id = "mock_question_answerer"
            app.answer_checker_id = "mock_answer_checker"
            app.link_checker_id = "mock_link_checker"
            
            # Should not raise any errors
            app.cleanup_agents()
            
            # In mock mode, cleanup should be a no-op
            self.assertIsNone(app.question_answerer_session)
            self.assertIsNone(app.answer_checker_session)
            self.assertIsNone(app.link_checker_session)
        
    def test_cleanup_agents_with_sessions(self):
        """Test that cleanup_agents properly calls __exit__ on active sessions."""
        with patch('question_answerer.QuestionnaireAgentUI.init_azure_client'):
            app = QuestionnaireAgentUI(headless_mode=True, mock_mode=True)
            
            # Create mock sessions
            mock_qa_session = MagicMock()
            mock_ac_session = MagicMock()
            mock_lc_session = MagicMock()
            
            # Assign mock sessions
            app.question_answerer_session = mock_qa_session
            app.answer_checker_session = mock_ac_session
            app.link_checker_session = mock_lc_session
            
            # Set mock mode to False to test actual cleanup logic
            app.mock_mode = False
            
            # Call cleanup
            app.cleanup_agents()
            
            # Verify __exit__ was called on all sessions
            mock_qa_session.__exit__.assert_called_once_with(None, None, None)
            mock_ac_session.__exit__.assert_called_once_with(None, None, None)
            mock_lc_session.__exit__.assert_called_once_with(None, None, None)
            
            # Verify sessions were set to None
            self.assertIsNone(app.question_answerer_session)
            self.assertIsNone(app.answer_checker_session)
            self.assertIsNone(app.link_checker_session)
            
            # Verify agent IDs were reset
            self.assertIsNone(app.question_answerer_id)
            self.assertIsNone(app.answer_checker_id)
            self.assertIsNone(app.link_checker_id)
        
    def test_cleanup_agents_handles_session_errors(self):
        """Test that cleanup_agents handles errors during session cleanup gracefully."""
        with patch('question_answerer.QuestionnaireAgentUI.init_azure_client'):
            app = QuestionnaireAgentUI(headless_mode=True, mock_mode=True)
            
            # Create mock sessions that raise errors
            mock_qa_session = MagicMock()
            mock_qa_session.__exit__.side_effect = Exception("Cleanup failed")
            
            mock_ac_session = MagicMock()
            mock_lc_session = MagicMock()
            
            # Assign mock sessions
            app.question_answerer_session = mock_qa_session
            app.answer_checker_session = mock_ac_session
            app.link_checker_session = mock_lc_session
            
            # Set mock mode to False to test actual cleanup logic
            app.mock_mode = False
            
            # Call cleanup - should not raise exception even though one session fails
            app.cleanup_agents()
            
            # Verify all sessions had cleanup attempted
            mock_qa_session.__exit__.assert_called_once_with(None, None, None)
            mock_ac_session.__exit__.assert_called_once_with(None, None, None)
            mock_lc_session.__exit__.assert_called_once_with(None, None, None)
            
            # Verify all sessions were set to None despite the error
            self.assertIsNone(app.question_answerer_session)
            self.assertIsNone(app.answer_checker_session)
            self.assertIsNone(app.link_checker_session)
        
    def test_cleanup_agents_no_sessions(self):
        """Test that cleanup_agents handles the case where no sessions exist."""
        with patch('question_answerer.QuestionnaireAgentUI.init_azure_client'):
            app = QuestionnaireAgentUI(headless_mode=True, mock_mode=False)
            
            # Ensure no sessions exist
            self.assertIsNone(app.question_answerer_session)
            self.assertIsNone(app.answer_checker_session)
            self.assertIsNone(app.link_checker_session)
            
            # Should not raise any errors
            app.cleanup_agents()
        
    def test_destructor_calls_cleanup(self):
        """Test that the __del__ method calls cleanup_agents."""
        with patch('question_answerer.QuestionnaireAgentUI.init_azure_client'):
            app = QuestionnaireAgentUI(headless_mode=True, mock_mode=True)
            
            # Mock the cleanup_agents method
            app.cleanup_agents = MagicMock()
            
            # Call the destructor
            app.__del__()
            
            # Verify cleanup was called
            app.cleanup_agents.assert_called_once()
        
    @patch.dict('sys.modules', mock_azure_modules)
    @patch('question_answerer.sys.exit')
    def test_signal_handler_cleanup(self, mock_sys_exit):
        """Test that signal handlers call cleanup before exit."""
        with patch('question_answerer.QuestionnaireAgentUI.init_azure_client'):
            app = QuestionnaireAgentUI(headless_mode=True, mock_mode=True)
            
            # Mock the cleanup_agents method
            app.cleanup_agents = MagicMock()
            
            # Call the signal handler
            app._signal_handler(2, None)  # SIGINT
            
            # Verify cleanup was called
            app.cleanup_agents.assert_called_once()
            
            # Verify sys.exit was called
            mock_sys_exit.assert_called_once_with(0)
        
    @patch.dict('sys.modules', mock_azure_modules)
    @patch('question_answerer.FoundryAgentSession')
    def test_create_agents_uses_foundry_sessions(self, mock_foundry_session_class):
        """Test that create_agents uses FoundryAgentSession for agent management."""
        # This test verifies the integration without requiring Azure dependencies
        with patch('question_answerer.QuestionnaireAgentUI.init_azure_client'):
            app = QuestionnaireAgentUI(headless_mode=True, mock_mode=False)
            
            # Mock project client
            app.project_client = self.mock_client
            
            # Mock environment variables
            with patch.dict('os.environ', {
                'AZURE_OPENAI_MODEL_DEPLOYMENT': 'gpt-4o-mini',
                'BING_CONNECTION_ID': 'test-bing-connection'
            }):
                # Mock the connection retrieval
                mock_connection = MagicMock()
                mock_connection.id = 'connection-123'
                app.project_client.connections.get.return_value = mock_connection
                
                # Mock FoundryAgentSession instances
                mock_sessions = []
                for i in range(3):
                    mock_session = MagicMock()
                    mock_session.get_agent_id.return_value = f'agent-{i+1}'
                    mock_session.__enter__.return_value = (MagicMock(), MagicMock())
                    mock_sessions.append(mock_session)
                
                mock_foundry_session_class.side_effect = mock_sessions
                
                # Call create_agents
                app.create_agents()
                
                # Verify FoundryAgentSession was called 3 times (one for each agent)
                self.assertEqual(mock_foundry_session_class.call_count, 3)
                
                # Verify sessions were stored
                self.assertEqual(app.question_answerer_session, mock_sessions[0])
                self.assertEqual(app.answer_checker_session, mock_sessions[1])
                self.assertEqual(app.link_checker_session, mock_sessions[2])
                
                # Verify agent IDs were set
                self.assertEqual(app.question_answerer_id, 'agent-1')
                self.assertEqual(app.answer_checker_id, 'agent-2')
                self.assertEqual(app.link_checker_id, 'agent-3')


if __name__ == '__main__':
    unittest.main()