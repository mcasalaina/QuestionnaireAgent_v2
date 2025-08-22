"""
Question Answerer Agent using Azure AI Foundry with Bing grounding

Searches the web for evidence and synthesizes a candidate answer to a given question.
"""

import logging
import os
from typing import Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from utils.resource_manager import FoundryAgentSession

# Load environment variables from .env file
load_dotenv(override=True)

# Long instructions for the question answerer agent
LONG_INSTRUCTIONS = """You are a questionnaire answering system that provides factual, comprehensive answers using web search and grounding.

IMPORTANT REQUIREMENTS:
- NEVER use second person pronouns (you, your, yours) - always write in third person
- NEVER ask follow-up questions or offer additional information (e.g., "Would you like more information?", "Do you need help with...?", "Let me know if...") 
- Provide only the direct answer to the question asked
- Write as if answering for documentation or reference purposes

Your task is to:
1. Search for relevant, authoritative information about the question
2. Synthesize a comprehensive, factual answer in third person
3. Include proper source citations with URLs
4. Ensure the answer is well-structured and informative
5. End the response when the question is fully answered - no calls to action

Always use web search to ground answers in current, factual information.
Provide URLs for all sources referenced."""


class QuestionAnswerer:
    """
    Azure AI Foundry agent responsible for generating candidate answers using Bing grounding.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Azure AI Foundry client
        project_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.model_deployment = os.getenv('AZURE_OPENAI_MODEL_DEPLOYMENT', 'gpt-4o-mini')
        
        if not project_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
        
        # Use DefaultAzureCredential for AIProjectClient (it expects token-based auth)
        credential = DefaultAzureCredential()
        
        try:
            self.project_client = AIProjectClient(
                endpoint=project_endpoint,
                credential=credential
            )
            
            self.logger.info("QuestionAnswerer Azure AI Foundry client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure AI Foundry client: {e}")
            raise
    
    def generate_answer(self, question: str) -> Optional[str]:
        """
        Generate a candidate answer using Azure AI Foundry agent with Bing grounding.
        
        Args:
            question: The natural language question to answer
            
        Returns:
            Generated answer string, or None if failed
        """
        try:
            self.logger.info(f"Generating answer for: {question}")
            
            # Use context manager for automatic resource cleanup
            with FoundryAgentSession(self.project_client,
                                   model=self.model_deployment,
                                   name="question-answerer",
                                   instructions=LONG_INSTRUCTIONS) as (agent, thread):
                
                # Add message to the thread
                message = self.project_client.agents.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=f"Please provide a comprehensive answer to this question: {question}"
                )
                
                # Create and process run (this polls automatically)
                run = self.project_client.agents.runs.create_and_process(
                    thread_id=thread.id,
                    agent_id=agent.id
                )
                
                if run.status == 'completed':
                    # Get the response messages
                    messages = self.project_client.agents.messages.list(thread_id=thread.id)
                    
                    answer = None
                    for msg in messages:
                        if msg.role == 'assistant' and msg.content:
                            for content in msg.content:
                                if hasattr(content, 'text'):
                                    answer = content.text.value
                                    break
                            if answer:
                                break
                    
                    if answer:
                        self.logger.info("Successfully generated candidate answer using Azure AI Foundry")
                        return answer
                    else:
                        self.logger.error("No answer content found in agent response")
                        return None
                
                else:
                    self.logger.error(f"Agent run failed with status: {run.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Unexpected error generating answer with Azure AI Foundry: {e}", exc_info=True)
            return None
    
    # Note: Azure AI Foundry agents handle search, synthesis, and grounding automatically
