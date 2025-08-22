"""
Link Checker Agent using Azure AI Foundry

Verifies that every URL cited in the answer is reachable and relevant to the content.
"""

import logging
import re
import requests
import os
from typing import Tuple, List
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from utils.resource_manager import FoundryAgentSession

# Load environment variables from .env file
load_dotenv(override=True)


class LinkChecker:
    """
    Azure AI Foundry agent responsible for validating URLs cited in answers.
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
            
            self.logger.info("LinkChecker Azure AI Foundry client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure AI Foundry client: {e}")
            raise
        
        # Also keep a session for direct URL checking
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QuestionnaireAgent-LinkChecker/1.0'
        })
    
    def validate_links(self, answer: str) -> Tuple[bool, str]:
        """
        Validate all URLs cited in the answer using Azure AI Foundry with Bing grounding.
        
        Args:
            answer: The candidate answer containing URLs to validate
            
        Returns:
            Tuple of (all_valid: bool, feedback: str)
        """
        try:
            self.logger.info("Validating URLs in answer with Azure AI Foundry...")
            
            # Extract URLs from the answer
            urls = self._extract_urls(answer)
            
            if not urls:
                self.logger.info("No URLs found in answer")
                return True, "No URLs to validate"
            
            self.logger.info(f"Found {len(urls)} URLs to validate")
            
            # Use context manager for automatic resource cleanup
            with FoundryAgentSession(self.project_client,
                                   model=self.model_deployment,
                                   name="link-checker",
                                   instructions="""You are a URL validator and relevance checker.
                
                Your task is to validate URLs by:
                1. Checking if each URL is reachable and accessible
                2. Verifying that the URL content is relevant to the context
                3. Using web search to verify the credibility of sources
                
                Respond with 'VALID' if all URLs pass validation, or 'INVALID' followed by specific issues for each problematic URL.
                Use web search and grounding to verify URL accessibility and relevance.""") as (agent, thread):
                
                # Create validation prompt
                urls_list = "\n".join([f"- {url}" for url in urls])
                validation_prompt = f"""Please validate these URLs found in an answer:
                
                URLs to validate:
                {urls_list}
                
                Context (the answer containing these URLs):
                {answer[:1000]}...
                
                Please check:
                1. Are all URLs reachable and accessible?
                2. Are the URLs relevant to the content context?
                3. Do the URLs lead to credible, authoritative sources?
                
                Respond with either 'VALID' or 'INVALID: [specific issues with each problematic URL]'"""
                
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
                            self.logger.info(f"All {len(urls)} URLs passed validation")
                            return True, f"All {len(urls)} URLs are reachable and relevant"
                        else:
                            # Extract feedback from INVALID response
                            feedback = validation_result_copy.replace('INVALID:', '').replace('INVALID', '').strip()
                            if not feedback:
                                feedback = "URL validation failed"
                            self.logger.warning(f"URL validation failed: {feedback}")
                            return False, feedback
                    else:
                        self.logger.error("No validation result found in agent response")
                        return False, "URL validation failed: No response from validation agent"
                
                else:
                    self.logger.error(f"URL validation agent failed with status: {run.status}")
                    return False, f"URL validation failed: Agent status {run.status}"
                    
        except Exception as e:
            self.logger.error(f"Unexpected error validating URLs with Azure AI Foundry: {e}", exc_info=True)
            return False, f"URL validation error: {str(e)}"
    
    def _extract_urls(self, text: str) -> List[str]:
        """
        Extract all URLs from the text.
        
        Args:
            text: Text to extract URLs from
            
        Returns:
            List of unique URLs found in the text
        """
        # Find markdown links [text](url)
        markdown_urls = re.findall(r'\[.*?\]\((https?://[^\)]+)\)', text)
        
        # Find plain URLs
        plain_urls = re.findall(r'https?://[^\s\)]+', text)
        
        # Combine and deduplicate
        all_urls = list(set(markdown_urls + plain_urls))
        
        # Clean up URLs (remove trailing punctuation)
        cleaned_urls = []
        for url in all_urls:
            # Remove trailing punctuation that's not part of URL
            url = re.sub(r'[.,;!?]+$', '', url)
            cleaned_urls.append(url)
        
        return list(set(cleaned_urls))  # Remove duplicates again after cleaning
    
    # Note: Azure AI Foundry agents handle URL validation automatically with Bing grounding
