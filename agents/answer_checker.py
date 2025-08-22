"""
Answer Checker Agent using Azure AI Foundry

Validates the factual correctness, completeness, and consistency of candidate answers.
"""

import logging
import os
from typing import Tuple
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from utils.resource_manager import FoundryAgentSession

# Load environment variables from .env file
load_dotenv(override=True)


class AnswerChecker:
    """
    Azure AI Foundry agent responsible for validating candidate answers using Bing grounding.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Azure AI Foundry client
        project_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.model_deployment = os.getenv('AZURE_OPENAI_MODEL_DEPLOYMENT', 'gpt-4.1')
        
        if not project_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
        
        # Use DefaultAzureCredential for AIProjectClient (it expects token-based auth)
        credential = DefaultAzureCredential()
        
        try:
            self.project_client = AIProjectClient(
                endpoint=project_endpoint,
                credential=credential
            )
            
            self.logger.info("AnswerChecker Azure AI Foundry client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure AI Foundry client: {e}")
            raise
    
    def validate_answer(self, question: str, answer: str) -> Tuple[bool, str]:
        """
        Validate the quality and accuracy of a candidate answer using Azure AI Foundry.
        
        Args:
            question: The original question
            answer: The candidate answer to validate
            
        Returns:
            Tuple of (is_valid: bool, feedback: str)
        """
        try:
            self.logger.info("Validating candidate answer with Azure AI Foundry...")
            
            # Use context manager for automatic resource cleanup
            with FoundryAgentSession(self.project_client,
                                   model=self.model_deployment,
                                   name="answer-checker",
                                   instructions="""You are an expert fact-checker and answer validator for a questionnaire system.
                
                Your task is to validate a candidate answer to a question by:
                1. Checking factual accuracy using web search and grounding
                2. Verifying completeness and relevance to the question
                3. Ensuring proper source citations are present
                4. Identifying any inconsistencies or errors
                5. CRITICAL: Ensuring the answer uses ONLY third person (never "you", "your", "yours")
                6. CRITICAL: Ensuring the answer contains NO follow-up questions or offers for more information
                
                The answer must be written as objective documentation, not as a conversation.
                
                Respond with 'VALID' if the answer passes all checks, or 'INVALID' followed by specific reasons for rejection.
                Use web search to verify facts and claims made in the answer.""") as (agent, thread):
                
                # Create validation prompt
                validation_prompt = f"""Please validate this answer to the given question:
                
                QUESTION: {question}
                
                ANSWER: {answer}
                
                Please check:
                1. Factual accuracy (use web search to verify claims)
                2. Completeness and relevance to the question
                3. Presence of proper source citations
                4. Overall quality and consistency
                5. CRITICAL: Does the answer use ONLY third person? (Flag any use of "you", "your", "yours")
                6. CRITICAL: Does the answer contain NO follow-up questions or offers? (Flag phrases like "Would you like...", "Do you need...", "Let me know...")
                
                The answer must be written as objective documentation, not conversational.
                
                Respond with either 'VALID' or 'INVALID: [specific reasons]'"""
                
                message = self.project_client.agents.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=validation_prompt
                )
                
                # Create and process run (this polls automatically)
                run = self.project_client.agents.runs.create_and_process(
                    thread_id=thread.id,
                    agent_id=agent.id
                )
                
                if run.status == 'completed':
                    # Get the validation response
                    messages = self.project_client.agents.messages.list(thread_id=thread.id)
                    
                    validation_result = None
                    for msg in messages:
                        if msg.role == 'assistant' and msg.content:
                            for content in msg.content:
                                if hasattr(content, 'text'):
                                    validation_result = content.text.value
                                    break
                            if validation_result:
                                break
                    
                    # Copy validation result before exiting the context manager
                    validation_result_copy = validation_result
                    
                    if validation_result_copy:
                        # Parse the validation result
                        if validation_result_copy.strip().upper().startswith('VALID'):
                            self.logger.info("Answer validation passed")
                            return True, "Answer validation passed"
                        else:
                            # Extract feedback from INVALID response
                            feedback = validation_result_copy.replace('INVALID:', '').replace('INVALID', '').strip()
                            if not feedback:
                                feedback = "Answer validation failed"
                            self.logger.warning(f"Answer validation failed: {feedback}")
                            return False, feedback
                    else:
                        self.logger.error("No validation result found in agent response")
                        return False, "Validation failed: No response from validation agent"
                
                else:
                    self.logger.error(f"Validation agent failed with status: {run.status}")
                    return False, f"Validation failed: Agent status {run.status}"
                    
        except Exception as e:
            self.logger.error(f"Unexpected error validating answer with Azure AI Foundry: {e}", exc_info=True)
            return False, f"Validation error: {str(e)}"
    
    # Note: Azure AI Foundry agents handle answer validation automatically with Bing grounding
