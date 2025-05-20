"""
Neo4j adapter implementation for the GraphDBInterface.
"""
from typing import Any, Dict, List, Optional

from neo4j import AsyncDriver, AsyncSession
from neo4j.exceptions import DriverError, ClientError
from neo4j.graph import Graph

# Handle different neo4j driver versions
try:
    # Try newest version first
    from neo4j.async_driver import AsyncResult, AsyncGraphDatabase
except ImportError:
    try:
        # Try older versions
        from neo4j.work import Result as AsyncResult
        from neo4j import AsyncGraphDatabase
    except ImportError:
        # As a last resort, create a compatibility layer
        from neo4j import AsyncGraphDatabase
        # Create a compatible AsyncResult type alias
        from neo4j import Result
        AsyncResult = Result  # Create an alias for compatibility

from graphiti_core.database.db_interface import GraphDBInterface


class Neo4jAdapter(GraphDBInterface[AsyncSession, AsyncResult]):
    """Neo4j implementation of the GraphDBInterface."""

    def __init__(self):
        """Initialize the Neo4j adapter."""
        self.driver: Optional[AsyncDriver] = None

    async def connect(self, uri: str, user: str, password: str) -> None:
        """Connect to the Neo4j database.

        Args:
            uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
        """
        try:
            self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
            # Test the connection by starting a session
            async with self.driver.session() as session:
                await session.run("RETURN 1")
        except DriverError as e:
            raise ConnectionError(f"Failed to connect to Neo4j: {str(e)}")

    async def close(self) -> None:
        """Close the Neo4j connection."""
        if self.driver:
            await self.driver.close()
            self.driver = None

    async def get_driver(self) -> AsyncDriver:
        """Get the Neo4j driver instance.

        Returns:
            Neo4j driver instance

        Raises:
            ConnectionError: If the driver is not initialized
        """
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")
        return self.driver

    async def get_session(self) -> AsyncSession:
        """Create a new Neo4j session.

        Returns:
            Neo4j session

        Raises:
            ConnectionError: If the driver is not initialized
        """
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")
        return self.driver.session()

    async def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> AsyncResult:
        """Execute a Cypher query against Neo4j.

        Args:
            query: Cypher query
            parameters: Query parameters

        Returns:
            Neo4j query result

        Raises:
            ConnectionError: If the driver is not initialized
            Exception: If the query execution fails
        """
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")

        params = parameters or {}
        try:
            async with self.driver.session() as session:
                return await session.run(query, params)
        except Exception as e:
            raise Exception(f"Error executing Neo4j query: {str(e)}")

    async def build_indices(self, delete_existing: bool = False) -> None:
        """Build Neo4j indices and constraints.

        Args:
            delete_existing: Whether to delete existing indices and constraints
        """
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")

        async with self.driver.session() as session:
            if delete_existing:
                # Drop all constraints and indices
                await session.run("CALL apoc.schema.assert({}, {}, true)")

            # Create constraints and indices
            # Node constraints
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Episode) REQUIRE n.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Message) REQUIRE n.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Message) REQUIRE n.timestamp IS NOT NULL"
            )
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Episode) REQUIRE n.created_at IS NOT NULL"
            )

            # Create indices
            await session.run("CREATE INDEX IF NOT EXISTS FOR (n:Episode) ON (n.created_at)")
            await session.run("CREATE INDEX IF NOT EXISTS FOR (n:Message) ON (n.timestamp)")
            await session.run("CREATE INDEX IF NOT EXISTS FOR (n:Message) ON (n.role)")
            await session.run("CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.type)")
            await session.run("CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.name)")

    async def clear_all_data(self) -> None:
        """Clear all data from the Neo4j database."""
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")

        async with self.driver.session() as session:
            await session.run("MATCH (n) DETACH DELETE n")

    async def get_episodes(self) -> List[Dict[str, Any]]:
        """Get all episodes from Neo4j.

        Returns:
            List of episodes
        """
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")

        episodes = []
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (e:Episode)
                RETURN e
                ORDER BY e.created_at DESC
                """
            )
            records = await result.values()
            for record in records:
                if record and record[0]:
                    episode_node = record[0]
                    episodes.append(dict(episode_node))
        return episodes

    async def get_one_episode(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """Get a single episode by ID from Neo4j.

        Args:
            episode_id: Episode ID

        Returns:
            Episode data or None if not found
        """
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")

        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (e:Episode {id: $episode_id})
                RETURN e
                """,
                {"episode_id": episode_id}
            )
            records = await result.values()
            if records and records[0] and records[0][0]:
                episode_node = records[0][0]
                return dict(episode_node)
        return None
