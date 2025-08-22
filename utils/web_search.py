"""
Azure AI Foundry agents with Bing grounding for web search.
"""

import logging
import os
from typing import List, Dict, Optional
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import BingGroundingTool
from azure.identity import DefaultAzureCredential
from .resource_manager import FoundryAgentSession


class AzureAIFoundrySearcher:
    """
    Azure AI Foundry agent with Bing grounding for web search.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Get Azure AI Foundry configuration from environment
        self.project_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        
        if not self.project_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
        
        # Use DefaultAzureCredential for AIProjectClient (it expects token-based auth)
        credential = DefaultAzureCredential()
        
        # Initialize Azure AI Foundry client
        try:
            self.client = AIProjectClient(
                endpoint=self.project_endpoint,
                credential=credential
            )
            self.logger.info("Azure AI Foundry client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure AI Foundry client: {e}")
            raise
        
        # Setup Bing grounding tool
        bing_connection_id = os.getenv('BING_CONNECTION_ID', 'bing_grounding')
        self.bing_tool = BingGroundingTool(
            connection_id=bing_connection_id
        )
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web using Azure AI Foundry agent with Bing grounding.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with 'title', 'url', and 'snippet' keys
        """
        try:
            self.logger.info(f"Searching with Azure AI Foundry Bing grounding: {query}")
            
            # Configure agent for search with Bing grounding
            agent_config = {
                'tools': self.bing_tool.definitions,
                'tool_resources': self.bing_tool.resources
            }
            
            # Use context manager for automatic resource cleanup
            with FoundryAgentSession(self.client,
                                   model="gpt-4o",
                                   name="search-agent",
                                   instructions=f"Search for information about: {query}. Provide detailed, factual information with sources.",
                                   agent_config=agent_config) as (agent, thread):
                
                # Add the search query as a message
                message = self.client.agents.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=f"Please search for and provide detailed information about: {query}"
                )
                
                # Create and process run (this polls automatically)
                run = self.client.agents.runs.create_and_process(
                    thread_id=thread.id,
                    agent_id=agent.id
                )
                
                if run.status == 'completed':
                    # Get the messages
                    messages = self.client.agents.messages.list(thread_id=thread.id)
                    
                    results = []
                    for msg in messages:
                        if msg.role == 'assistant' and msg.content:
                            for content in msg.content:
                                if hasattr(content, 'text'):
                                    # Extract search results from the response
                                    text_content = content.text.value
                                    
                                    # Parse the grounded response for URLs and content
                                    import re
                                    urls = re.findall(r'https?://[^\s\)]+', text_content)
                                    
                                    # Create structured results
                                    if urls:
                                        for i, url in enumerate(urls[:max_results]):
                                            results.append({
                                                'title': f'Bing Search Result {i+1}',
                                                'url': url,
                                                'snippet': text_content[:500] + '...' if len(text_content) > 500 else text_content
                                            })
                                    else:
                                        # If no URLs found, still return the content
                                        results.append({
                                            'title': 'Azure AI Foundry Response',
                                            'url': '',
                                            'snippet': text_content[:500] + '...' if len(text_content) > 500 else text_content
                                        })
                    
                    self.logger.info(f"Found {len(results)} results from Azure AI Foundry")
                    return results[:max_results]
                
                else:
                    self.logger.error(f"Agent run failed with status: {run.status}")
                    return self._fallback_search(query)
                    
        except Exception as e:
            self.logger.error(f"Unexpected error in Azure AI Foundry search for query '{query}': {e}", exc_info=True)
            return self._fallback_search(query)
    
    def _fallback_search(self, query: str) -> List[Dict[str, str]]:
        """
        Fallback search method when Azure AI Foundry is not available.
        """
        return [{
            'title': f'Search: {query}',
            'url': '',
            'snippet': f'Search results for: {query}. (Azure AI Foundry with Bing grounding not available - check configuration)'
        }]
    
    def get_page_content(self, url: str) -> Optional[str]:
        """
        Fetch the content of a web page using Azure AI Foundry capabilities.
        
        Args:
            url: URL to fetch
            
        Returns:
            Page content as string, or None if failed
        """
        try:
            if not url or not url.startswith(('http://', 'https://')):
                return None
            
            # Configure agent for content fetching with Bing grounding
            agent_config = {
                'tools': self.bing_tool.definitions,
                'tool_resources': self.bing_tool.resources
            }
            
            # Use context manager for automatic resource cleanup
            with FoundryAgentSession(self.client,
                                   model="gpt-4o",
                                   name="content-fetcher",
                                   instructions=f"Fetch and summarize the content from this URL: {url}",
                                   agent_config=agent_config) as (agent, thread):
                
                message = self.client.agents.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=f"Please fetch and provide a summary of the content from: {url}"
                )
                
                # Create and process run (this polls automatically)
                run = self.client.agents.runs.create_and_process(
                    thread_id=thread.id,
                    agent_id=agent.id
                )
                
                if run.status == 'completed':
                    messages = self.client.agents.messages.list(thread_id=thread.id)
                    
                    for msg in messages:
                        if msg.role == 'assistant' and msg.content:
                            for content in msg.content:
                                if hasattr(content, 'text'):
                                    return content.text.value[:5000]  # Limit content size
                
                return None
                
        except Exception as e:
            self.logger.error(f"Unexpected error fetching content from {url}: {e}", exc_info=True)
            return None


# Backward compatibility alias
WebSearcher = AzureAIFoundrySearcher
