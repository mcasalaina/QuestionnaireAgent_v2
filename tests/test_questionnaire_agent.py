#!/usr/bin/env python3
"""
Unit tests for QuestionnaireAgent using pytest and unittest.mock.

Tests cover:
1. Happy path - all agents succeed
2. Fail-fast on exception - QuestionAnswerer raises RuntimeError
3. Retry limit on rejection - AnswerChecker rejects first attempt, accepts second
4. MAX_ATTEMPTS constant verification
"""

from unittest.mock import Mock
from main import QuestionnaireAgent


class TestQuestionnaireAgent:
    """Test suite for QuestionnaireAgent class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = QuestionnaireAgent()

    def test_happy_path_all_agents_succeed(self):
        """Test 1: Happy path - mocks return valid responses, all agents called once."""
        # Arrange
        test_question = "What are the key features of Azure AI Foundry for building enterprise AI applications?"
        expected_answer = "Azure AI Foundry provides a comprehensive platform for enterprise AI development with features including model catalog access, prompt flow orchestration, AI safety tools, content filtering, responsible AI monitoring, and integrated development environments for building, testing, and deploying AI applications at scale."
        
        # Mock all three agents
        mock_question_answerer = Mock()
        mock_answer_checker = Mock()
        mock_link_checker = Mock()
        
        # Configure mock responses
        mock_question_answerer.generate_answer.return_value = expected_answer
        mock_answer_checker.validate_answer.return_value = (True, "Answer looks good")
        mock_link_checker.validate_links.return_value = (True, "All links are valid")
        
        # Replace agent instances with mocks
        self.agent.question_answerer = mock_question_answerer
        self.agent.answer_checker = mock_answer_checker
        self.agent.link_checker = mock_link_checker
        
        # Act
        success, result = self.agent.answer_question(test_question)
        
        # Assert
        assert success is True
        assert result == expected_answer
        
        # Verify each mock was called exactly once
        mock_question_answerer.generate_answer.assert_called_once_with(test_question)
        mock_answer_checker.validate_answer.assert_called_once_with(test_question, expected_answer)
        mock_link_checker.validate_links.assert_called_once_with(expected_answer)

    def test_fail_fast_on_exception(self):
        """Test 2: Fail-fast on exception - QuestionAnswerer raises RuntimeError."""
        # Arrange
        test_question = "How does Azure AI Foundry integrate with existing MLOps workflows and CI/CD pipelines?"
        expected_error = "Azure AI service connection failed"
        
        # Mock question answerer to raise RuntimeError
        mock_question_answerer = Mock()
        mock_question_answerer.generate_answer.side_effect = RuntimeError(expected_error)
        
        # Mock other agents (they shouldn't be called)
        mock_answer_checker = Mock()
        mock_link_checker = Mock()
        
        # Replace agent instances with mocks
        self.agent.question_answerer = mock_question_answerer
        self.agent.answer_checker = mock_answer_checker
        self.agent.link_checker = mock_link_checker
        
        # Act
        success, result = self.agent.answer_question(test_question)
        
        # Assert
        assert success is False
        assert expected_error in result
        
        # Verify question answerer was called once (no retry on exception)
        mock_question_answerer.generate_answer.assert_called_once_with(test_question)
        
        # Verify other agents were not called
        mock_answer_checker.validate_answer.assert_not_called()
        mock_link_checker.validate_links.assert_not_called()

    def test_retry_limit_on_rejection(self):
        """Test 3: Retry limit - AnswerChecker rejects first attempt, accepts second."""
        # Arrange
        test_question = "What are the pricing models and cost optimization strategies for Azure AI Foundry deployments?"
        first_answer = "Azure AI Foundry has various pricing options."
        second_answer = "Azure AI Foundry offers multiple pricing models including pay-per-use consumption for API calls, dedicated instance pricing for consistent workloads, and reserved capacity options. Cost optimization strategies include using prompt flow for efficient orchestration, implementing content filtering to reduce unnecessary API calls, leveraging model fine-tuning to improve efficiency, and utilizing Azure Cost Management tools for monitoring and budgeting AI service usage."
        
        # Mock question answerer to return different answers on consecutive calls
        mock_question_answerer = Mock()
        mock_question_answerer.generate_answer.side_effect = [first_answer, second_answer]
        
        # Mock answer checker to reject first, accept second
        mock_answer_checker = Mock()
        mock_answer_checker.validate_answer.side_effect = [
            (False, "Answer is too vague"),  # First call - reject
            (True, "Answer looks good")      # Second call - accept
        ]
        
        # Mock link checker to always accept
        mock_link_checker = Mock()
        mock_link_checker.validate_links.return_value = (True, "All links are valid")
        
        # Replace agent instances with mocks
        self.agent.question_answerer = mock_question_answerer
        self.agent.answer_checker = mock_answer_checker
        self.agent.link_checker = mock_link_checker
        
        # Act
        success, result = self.agent.answer_question(test_question)
        
        # Assert
        assert success is True
        assert result == second_answer
        
        # Verify question answerer was called exactly twice
        assert mock_question_answerer.generate_answer.call_count == 2
        mock_question_answerer.generate_answer.assert_any_call(test_question)
        
        # Verify answer checker was called exactly twice
        assert mock_answer_checker.validate_answer.call_count == 2
        mock_answer_checker.validate_answer.assert_any_call(test_question, first_answer)
        mock_answer_checker.validate_answer.assert_any_call(test_question, second_answer)
        
        # Verify link checker was called exactly once (only for successful answer)
        mock_link_checker.validate_links.assert_called_once_with(second_answer)

    def test_max_attempts_constant(self):
        """Test 4: Verify MAX_ATTEMPTS constant equals 10."""
        # Assert
        assert QuestionnaireAgent.MAX_ATTEMPTS == 10
