#!/usr/bin/env python3
"""
Unit tests for FoundryAgentSession resource cleanup guarantees.

Tests cover cleanup behavior in both successful and failure scenarios:
1. Successful context manager execution with proper cleanup
2. Exception during context manager execution with guaranteed cleanup
3. Exception during agent creation with partial cleanup
4. Exception during thread creation with agent cleanup
5. Exception during __exit__ execution doesn't suppress original errors
6. Cleanup method robustness with exception handling

Using unittest.mock to patch AIProjectClient.agents.* and .threads.* methods.
Simulates successful runs AND exceptions thrown after agent/thread creation.
Asserts that delete_agent and threads.delete are called exactly once in all cases.
"""

import unittest
import sys
import os
from unittest.mock import Mock
import pytest

# Add the parent directory to the path so we can import from utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.resource_manager import FoundryAgentSession


class TestFoundryAgentSessionCleanup(unittest.TestCase):
    """Test suite for FoundryAgentSession resource cleanup guarantees."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock AIProjectClient
        self.mock_client = Mock()
        
        # Mock agent and thread objects with IDs
        self.mock_agent = Mock()
        self.mock_agent.id = "test-agent-123"
        
        self.mock_thread = Mock()
        self.mock_thread.id = "test-thread-456"
        
        # Configure mock client methods
        self.mock_client.agents.create_agent.return_value = self.mock_agent
        self.mock_client.agents.threads.create.return_value = self.mock_thread
        self.mock_client.agents.delete_agent = Mock()
        self.mock_client.agents.threads.delete = Mock()
        
        # Test configuration
        self.test_config = {
            'model': 'gpt-4o-mini',
            'name': 'test-agent',
            'instructions': 'Test instructions'
        }

    def test_successful_context_manager_cleanup(self):
        """Test 1: Successful context manager execution with proper cleanup."""
        # Arrange
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Act
        with session as (agent, thread):
            # Verify resources were created
            self.assertEqual(agent, self.mock_agent)
            self.assertEqual(thread, self.mock_thread)
            self.assertEqual(session.agent_id, "test-agent-123")
            self.assertEqual(session.thread_id, "test-thread-456")
        
        # Assert
        # Verify agent and thread creation were called
        self.mock_client.agents.create_agent.assert_called_once()
        self.mock_client.agents.threads.create.assert_called_once()
        
        # Verify cleanup methods were called exactly once
        self.mock_client.agents.delete_agent.assert_called_once_with("test-agent-123")
        self.mock_client.agents.threads.delete.assert_called_once_with("test-thread-456")

    def test_exception_during_context_guarantees_cleanup(self):
        """Test 2: Exception during context manager execution with guaranteed cleanup."""
        # Arrange
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Test exception in context"):
            with session as (agent, thread):
                # Verify resources were created
                self.assertEqual(agent, self.mock_agent)
                self.assertEqual(thread, self.mock_thread)
                # Simulate an exception during context execution
                raise ValueError("Test exception in context")
        
        # Assert cleanup still occurred
        self.mock_client.agents.delete_agent.assert_called_once_with("test-agent-123")
        self.mock_client.agents.threads.delete.assert_called_once_with("test-thread-456")

    def test_exception_during_agent_creation_partial_cleanup(self):
        """Test 3: Exception during agent creation with no cleanup needed."""
        # Arrange
        self.mock_client.agents.create_agent.side_effect = RuntimeError("Agent creation failed")
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Agent creation failed"):
            with session as (agent, thread):
                pass  # Should not reach here
        
        # Assert no cleanup is called since nothing was created
        self.mock_client.agents.delete_agent.assert_not_called()
        self.mock_client.agents.threads.delete.assert_not_called()

    def test_exception_during_thread_creation_agent_cleanup(self):
        """Test 4: Exception during thread creation with agent cleanup."""
        # Arrange
        self.mock_client.agents.threads.create.side_effect = RuntimeError("Thread creation failed")
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Thread creation failed"):
            with session as (agent, thread):
                pass  # Should not reach here
        
        # Assert agent cleanup is called, but not thread cleanup
        self.mock_client.agents.delete_agent.assert_called_once_with("test-agent-123")
        self.mock_client.agents.threads.delete.assert_not_called()

    def test_cleanup_exception_handling_agent_delete_fails(self):
        """Test 5: Cleanup robustness when agent deletion fails."""
        # Arrange
        self.mock_client.agents.delete_agent.side_effect = Exception("Agent deletion failed")
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Act - no exception should be raised from cleanup failures
        with session as (agent, thread):
            pass
        
        # Assert both cleanup methods were attempted
        self.mock_client.agents.delete_agent.assert_called_once_with("test-agent-123")
        self.mock_client.agents.threads.delete.assert_called_once_with("test-thread-456")

    def test_cleanup_exception_handling_thread_delete_fails(self):
        """Test 6: Cleanup robustness when thread deletion fails."""
        # Arrange
        self.mock_client.agents.threads.delete.side_effect = Exception("Thread deletion failed")
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Act - no exception should be raised from cleanup failures
        with session as (agent, thread):
            pass
        
        # Assert both cleanup methods were attempted
        self.mock_client.agents.delete_agent.assert_called_once_with("test-agent-123")
        self.mock_client.agents.threads.delete.assert_called_once_with("test-thread-456")

    def test_cleanup_exception_handling_both_deletes_fail(self):
        """Test 7: Cleanup robustness when both deletions fail."""
        # Arrange
        self.mock_client.agents.delete_agent.side_effect = Exception("Agent deletion failed")
        self.mock_client.agents.threads.delete.side_effect = Exception("Thread deletion failed")
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Act - no exception should be raised from cleanup failures
        with session as (agent, thread):
            pass
        
        # Assert both cleanup methods were attempted
        self.mock_client.agents.delete_agent.assert_called_once_with("test-agent-123")
        self.mock_client.agents.threads.delete.assert_called_once_with("test-thread-456")

    def test_context_exception_not_suppressed_by_cleanup_failure(self):
        """Test 8: Original context exception not suppressed by cleanup failures."""
        # Arrange
        self.mock_client.agents.delete_agent.side_effect = Exception("Agent deletion failed")
        self.mock_client.agents.threads.delete.side_effect = Exception("Thread deletion failed")
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Act & Assert - original exception should be raised, not cleanup exceptions
        with pytest.raises(ValueError, match="Original context exception"):
            with session as (agent, thread):
                raise ValueError("Original context exception")
        
        # Assert cleanup was still attempted
        self.mock_client.agents.delete_agent.assert_called_once_with("test-agent-123")
        self.mock_client.agents.threads.delete.assert_called_once_with("test-thread-456")

    def test_agent_response_formats_object_with_id(self):
        """Test 9: Handles agent response as object with .id attribute."""
        # This is the default case already tested, but explicitly verifying
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        with session as (agent, thread):
            self.assertEqual(session.agent_id, "test-agent-123")
            self.assertEqual(session.thread_id, "test-thread-456")

    def test_agent_response_formats_dict_with_id(self):
        """Test 10: Handles agent response as dictionary with 'id' key."""
        # Arrange
        self.mock_client.agents.create_agent.return_value = {"id": "dict-agent-789"}
        self.mock_client.agents.threads.create.return_value = {"id": "dict-thread-012"}
        
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Act
        with session as (agent, thread):
            self.assertEqual(session.agent_id, "dict-agent-789")
            self.assertEqual(session.thread_id, "dict-thread-012")
        
        # Assert cleanup uses the extracted IDs
        self.mock_client.agents.delete_agent.assert_called_once_with("dict-agent-789")
        self.mock_client.agents.threads.delete.assert_called_once_with("dict-thread-012")

    def test_agent_response_formats_direct_id_string(self):
        """Test 11: Handles agent response as direct ID string."""
        # Arrange
        self.mock_client.agents.create_agent.return_value = "string-agent-345"
        self.mock_client.agents.threads.create.return_value = "string-thread-678"
        
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Act
        with session as (agent, thread):
            self.assertEqual(session.agent_id, "string-agent-345")
            self.assertEqual(session.thread_id, "string-thread-678")
        
        # Assert cleanup uses the IDs directly
        self.mock_client.agents.delete_agent.assert_called_once_with("string-agent-345")
        self.mock_client.agents.threads.delete.assert_called_once_with("string-thread-678")

    def test_configuration_parameters_passed_correctly(self):
        """Test 12: Configuration parameters are passed correctly to create methods."""
        # Arrange
        agent_config = {"temperature": 0.7, "max_tokens": 1000}
        thread_config = {"metadata": {"test": "value"}}
        
        session = FoundryAgentSession(
            self.mock_client,
            model="custom-model",
            name="custom-agent",
            instructions="Custom instructions",
            agent_config=agent_config,
            thread_config=thread_config
        )
        
        # Act
        with session as (agent, thread):
            pass
        
        # Assert agent creation called with correct parameters
        expected_agent_config = {
            'model': 'custom-model',
            'name': 'custom-agent',
            'instructions': 'Custom instructions',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        self.mock_client.agents.create_agent.assert_called_once_with(**expected_agent_config)
        
        # Assert thread creation called with correct parameters
        self.mock_client.agents.threads.create.assert_called_once_with(**thread_config)

    def test_none_values_filtered_from_agent_config(self):
        """Test 13: None values are filtered from agent configuration."""
        # Arrange
        session = FoundryAgentSession(
            self.mock_client,
            model=None,  # Should be filtered out
            name="test-agent",
            instructions=None,  # Should be filtered out
            agent_config={"custom_param": "value"}
        )
        
        # Act
        with session as (agent, thread):
            pass
        
        # Assert only non-None values are passed
        expected_config = {
            'name': 'test-agent',
            'custom_param': 'value'
        }
        self.mock_client.agents.create_agent.assert_called_once_with(**expected_config)

    def test_partial_failure_cleanup_sequence(self):
        """Test 14: Partial failure during creation triggers appropriate cleanup."""
        # Arrange - Agent creation succeeds, thread creation fails
        self.mock_client.agents.threads.create.side_effect = [
            RuntimeError("Thread creation failed")
        ]
        
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Thread creation failed"):
            with session as (agent, thread):
                pass
        
        # Assert agent was created and then cleaned up, thread was never created
        self.mock_client.agents.create_agent.assert_called_once()
        self.mock_client.agents.threads.create.assert_called_once()
        self.mock_client.agents.delete_agent.assert_called_once_with("test-agent-123")
        self.mock_client.agents.threads.delete.assert_not_called()

    def test_get_id_methods(self):
        """Test 15: Get ID methods return correct values."""
        # Arrange
        session = FoundryAgentSession(
            self.mock_client,
            model=self.test_config['model'],
            name=self.test_config['name'],
            instructions=self.test_config['instructions']
        )
        
        # Before context manager
        self.assertIsNone(session.get_agent_id())
        self.assertIsNone(session.get_thread_id())
        
        # During context manager
        with session as (agent, thread):
            self.assertEqual(session.get_agent_id(), "test-agent-123")
            self.assertEqual(session.get_thread_id(), "test-thread-456")
        
        # After context manager (IDs are still available for debugging)
        self.assertEqual(session.get_agent_id(), "test-agent-123")
        self.assertEqual(session.get_thread_id(), "test-thread-456")


if __name__ == '__main__':
    unittest.main()
