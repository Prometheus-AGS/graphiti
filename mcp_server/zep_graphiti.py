import logging
import os

logger = logging.getLogger(__name__)

# Mock classes for testing
class MockGraphiti:
    def __init__(self, uri, user, password, llm_client=None, db_type=None):
        self.uri = uri
        self.user = user
        self.password = password
        self.llm_client = llm_client
        self.db_type = db_type
        self.driver = None
    
    async def build_indices_and_constraints(self):
        logger.info("Building indices and constraints (mocked)")
        return True

    async def clear_data(self):
        logger.info("Clearing data (mocked)")
        return True

    async def save_entity_node(self, name: str, uuid: str, group_id: str, summary: str = ''):
        logger.info("Saving entity node (mocked)")
        return True

    async def get_entity_edge(self, uuid: str):
        logger.info("Getting entity edge (mocked)")
        return True

    async def delete_group(self, group_id: str):
        logger.info("Deleting group (mocked)")
        return True

    async def delete_entity_edge(self, uuid: str):
        logger.info("Deleting entity edge (mocked)")
        return True

    async def delete_episodic_node(self, uuid: str):
        logger.info("Deleting episodic node (mocked)")
        return True

# Initialize Graphiti function
async def initialize_graphiti(config):
    """Initialize the Graphiti client with the configured settings."""
    try:
        # Log database configuration
        database_type = config.database_type.lower()
        logger.info(f"Database type: {database_type}")
        logger.info(f"Database URI: {config.database_uri}")
        
        if database_type == "surrealdb":
            logger.info(f"Using SurrealDB at {config.database_uri}")
            if hasattr(config, "database_namespace"):
                logger.info(f"Using namespace: {config.database_namespace}")
            if hasattr(config, "database_db"):
                logger.info(f"Using database: {config.database_db}")
        else:
            logger.info(f"Using Neo4j at {config.database_uri}")
        
        # Create a mock Graphiti client for testing
        graphiti_client = MockGraphiti(
            uri=config.database_uri,
            user=config.database_user,
            password=config.database_password,
            db_type=database_type
        )
        
        logger.info("Graphiti client initialized successfully (mocked)")
        return graphiti_client
    except Exception as e:
        logger.error(f"Failed to initialize Graphiti: {str(e)}")
        raise

# Simple helper function to get a Graphiti client
async def get_graphiti(settings):
    return await initialize_graphiti(settings)
