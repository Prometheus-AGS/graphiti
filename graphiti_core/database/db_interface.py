"""
Abstract interface for graph database adapters.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Set, Tuple, TypeVar

# Type variables for database-specific session and result types
SessionType = TypeVar('SessionType')
ResultType = TypeVar('ResultType')

class GraphDBInterface(Generic[SessionType, ResultType], ABC):
    """Interface for graph database adapters.
    
    This interface defines the operations that all graph database adapters must implement.
    It is parameterized with types for the session and result objects specific to each database.
    """
    
    @abstractmethod
    async def connect(self, uri: str, user: str, password: str) -> None:
        """Connect to the database.

        Args:
            uri: Connection URI
            user: Username
            password: Password
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the database connection."""
        pass
    
    @abstractmethod
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> ResultType:
        """Execute a query against the database.

        Args:
            query: Query string in the database's query language
            parameters: Query parameters

        Returns:
            Database-specific query result
        """
        pass
    
    @abstractmethod
    async def get_driver(self) -> Any:
        """Get the database driver instance.

        Returns:
            Database driver instance
        """
        pass
    
    @abstractmethod
    async def get_session(self) -> SessionType:
        """Create a new database session.

        Returns:
            Database-specific session object
        """
        pass
    
    @abstractmethod
    async def build_indices(self, delete_existing: bool = False) -> None:
        """Build database indices.

        Args:
            delete_existing: Whether to delete existing indices
        """
        pass
    
    @abstractmethod
    async def clear_all_data(self) -> None:
        """Clear all data from the database."""
        pass
    
    @abstractmethod
    async def get_episodes(self) -> List[Dict[str, Any]]:
        """Get all episodes.

        Returns:
            List of episodes
        """
        pass
    
    @abstractmethod
    async def get_one_episode(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """Get a single episode by ID.

        Args:
            episode_id: Episode ID

        Returns:
            Episode data or None if not found
        """
        pass
