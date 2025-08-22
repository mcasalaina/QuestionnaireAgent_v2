"""
Resource manager for Foundry agent sessions.

This module provides a context manager for safely creating and cleaning up
Foundry agent and thread resources.
"""

import logging
from contextlib import suppress
from typing import Optional, Tuple, Any

logger = logging.getLogger(__name__)


class FoundryAgentSession:
    """
    Context manager for managing Foundry agent and thread resources.
    
    This class implements the context manager protocol to safely create
    and clean up Foundry agent and thread resources. It ensures that
    resources are always cleaned up, even if exceptions occur during
    the session.
    
    The __enter__ method creates an agent and a thread, returning both
    IDs (or full objects). The __exit__ method always attempts to delete
    the agent and thread, swallowing/logging any deletion errors so they
    don't mask the original exception.
    
    Example:
        Basic usage with resource cleanup:
        
        >>> with FoundryAgentSession(client) as (agent, thread):
        ...     # Use agent and thread for operations
        ...     result = agent.run_task(thread.id, "some task")
        ...     # Resources are automatically cleaned up
        
        Even if an exception occurs, resources are cleaned up:
        
        >>> try:
        ...     with FoundryAgentSession(client) as (agent, thread):
        ...         # Some operation that might fail
        ...         raise ValueError("Something went wrong")
        ... except ValueError:
        ...     # Agent and thread are still cleaned up
        ...     pass
    """
    
    def __init__(self, client: Any, model: str = None, name: str = None, 
                 instructions: str = None, agent_config: Optional[dict] = None, 
                 thread_config: Optional[dict] = None):
        """
        Initialize the FoundryAgentSession.
        
        Args:
            client: The Azure AI Foundry project client instance
            model: Model deployment name
            name: Agent name
            instructions: Agent instructions
            agent_config: Optional configuration dictionary for agent creation
            thread_config: Optional configuration dictionary for thread creation
        """
        self.client = client
        self.model = model
        self.name = name
        self.instructions = instructions
        self.agent_config = agent_config or {}
        self.thread_config = thread_config or {}
        self.agent = None
        self.thread = None
        self.agent_id = None
        self.thread_id = None
    
    def __enter__(self) -> Tuple[Any, Any]:
        """
        Enter the context manager and create agent and thread resources.
        
        Returns:
            Tuple[Any, Any]: A tuple containing (agent, thread) objects/IDs
            
        Raises:
            Exception: If agent or thread creation fails
        """
        try:
            # Create the agent using Azure AI Foundry client
            logger.info("Creating Foundry agent...")
            
            # Prepare agent configuration
            agent_config = {
                'model': self.model,
                'name': self.name,
                'instructions': self.instructions,
                **self.agent_config
            }
            
            # Remove None values
            agent_config = {k: v for k, v in agent_config.items() if v is not None}
            
            self.agent = self.client.agents.create_agent(**agent_config)
            
            # Extract agent ID (handle both object and dict responses)
            if hasattr(self.agent, 'id'):
                self.agent_id = self.agent.id
            elif isinstance(self.agent, dict) and 'id' in self.agent:
                self.agent_id = self.agent['id']
            else:
                self.agent_id = self.agent
                
            logger.info(f"Created agent with ID: {self.agent_id}")
            
            # Create the thread
            logger.info("Creating Foundry thread...")
            self.thread = self.client.agents.threads.create(**self.thread_config)
            
            # Extract thread ID (handle both object and dict responses)
            if hasattr(self.thread, 'id'):
                self.thread_id = self.thread.id
            elif isinstance(self.thread, dict) and 'id' in self.thread:
                self.thread_id = self.thread['id']
            else:
                self.thread_id = self.thread
                
            logger.info(f"Created thread with ID: {self.thread_id}")
            
            return self.agent, self.thread
            
        except Exception as e:
            logger.error(f"Failed to create agent or thread: {e}")
            # Clean up any resources that were created before the failure
            self._cleanup_resources()
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager and clean up resources.
        
        This method always attempts to delete the agent and thread,
        swallowing/logging any deletion errors so they don't mask
        the original exception.
        
        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
            
        Returns:
            None: Does not suppress exceptions from the with block
        """
        self._cleanup_resources()
        
        # Don't suppress the original exception
        return False
    
    def _cleanup_resources(self):
        """
        Clean up agent and thread resources with robust error handling.
        
        Uses contextlib.suppress and nested try/except blocks to ensure
        that cleanup errors don't mask the original exception.
        """
        # Clean up thread first (as it may depend on the agent)
        if self.thread_id:
            with suppress(Exception):
                try:
                    logger.info(f"Deleting thread with ID: {self.thread_id}")
                    self.client.agents.threads.delete(self.thread_id)
                    logger.info(f"Successfully deleted thread: {self.thread_id}")
                except Exception as e:
                    logger.warning(f"Failed to delete thread {self.thread_id}: {e}")
                    # Continue with agent cleanup even if thread deletion fails
        
        # Clean up agent
        if self.agent_id:
            with suppress(Exception):
                try:
                    logger.info(f"Deleting agent with ID: {self.agent_id}")
                    self.client.agents.delete_agent(self.agent_id)
                    logger.info(f"Successfully deleted agent: {self.agent_id}")
                except Exception as e:
                    logger.warning(f"Failed to delete agent {self.agent_id}: {e}")
                    # Log but don't re-raise to avoid masking original exception
    
    def get_agent_id(self) -> Optional[str]:
        """Get the agent ID if available."""
        return self.agent_id
    
    def get_thread_id(self) -> Optional[str]:
        """Get the thread ID if available."""
        return self.thread_id
