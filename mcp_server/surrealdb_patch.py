"""
Patch file for adding SurrealDB support to the Graphiti MCP server.

This file contains the changes needed to support SurrealDB in the MCP server.
To apply these changes, you'll need to modify the graphiti_mcp_server.py file.
"""

# Step 1: Add DatabaseType import
# Add this import at the top of the file with the other imports:
from graphiti_core.database.db_factory import DatabaseType

# Step 2: Create a DatabaseConfig class
# Add this class after the Neo4jConfig class:
class DatabaseConfig(BaseModel):
    """Configuration for database connection."""
    
    # Database type (neo4j or surrealdb)
    db_type: str = 'neo4j'
    
    # Generic database configuration
    uri: str | None = None
    user: str | None = None
    password: str | None = None
    namespace: str | None = None
    database: str | None = None
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create database configuration from environment variables."""
        return cls(
            db_type=os.environ.get('DATABASE_TYPE', 'neo4j').lower(),
            uri=os.environ.get('DATABASE_URI'),
            user=os.environ.get('DATABASE_USER'),
            password=os.environ.get('DATABASE_PASSWORD'),
            namespace=os.environ.get('DATABASE_NAMESPACE', 'graphiti'),
            database=os.environ.get('DATABASE_DB', 'graphiti'),
        )
    
    def get_db_type(self) -> DatabaseType:
        """Get the database type as a DatabaseType enum."""
        if self.db_type.lower() == 'surrealdb':
            return DatabaseType.SURREALDB
        return DatabaseType.NEO4J

# Step 3: Update GraphitiConfig class
# Modify the GraphitiConfig class to include the database config:
class GraphitiConfig(BaseModel):
    """Configuration for Graphiti client.

    Centralizes all configuration parameters for the Graphiti client.
    """

    llm: GraphitiLLMConfig = Field(default_factory=GraphitiLLMConfig)
    embedder: GraphitiEmbedderConfig = Field(default_factory=GraphitiEmbedderConfig)
    neo4j: Neo4jConfig = Field(default_factory=Neo4jConfig)  # Keep for backward compatibility
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    group_id: str | None = None
    use_custom_entities: bool = False
    destroy_graph: bool = False

    @classmethod
    def from_env(cls) -> 'GraphitiConfig':
        """Create a configuration instance from environment variables."""
        group_id = os.environ.get('GROUP_ID')
        use_custom_entities = os.environ.get('USE_CUSTOM_ENTITIES', '').lower() == 'true'
        destroy_graph = os.environ.get('DESTROY_GRAPH', '').lower() == 'true'

        return cls(
            llm=GraphitiLLMConfig.from_env(),
            embedder=GraphitiEmbedderConfig.from_env(),
            neo4j=Neo4jConfig.from_env(),
            database=DatabaseConfig.from_env(),
            group_id=group_id,
            use_custom_entities=use_custom_entities,
            destroy_graph=destroy_graph,
        )

# Step 4: Update initialize_graphiti function
# Replace the initialize_graphiti function with this version:
async def initialize_graphiti():
    """Initialize the Graphiti client with the configured settings."""
    global graphiti_client, config

    try:
        # Create LLM client if possible
        llm_client = config.llm.create_client()
        if not llm_client and config.use_custom_entities:
            # If custom entities are enabled, we must have an LLM client
            raise ValueError('OPENAI_API_KEY must be set when custom entities are enabled')

        # Get database type
        db_type = config.database.get_db_type()
        
        # Validate database configuration based on type
        if db_type == DatabaseType.SURREALDB:
            # Validate SurrealDB configuration
            if not config.database.uri or not config.database.user or not config.database.password:
                raise ValueError('DATABASE_URI, DATABASE_USER, and DATABASE_PASSWORD must be set for SurrealDB')
            
            # Use SurrealDB configuration
            db_uri = config.database.uri
            db_user = config.database.user
            db_password = config.database.password
            
            logger.info(f'Using SurrealDB at {db_uri}')
            logger.info(f'Using namespace: {config.database.namespace}')
            logger.info(f'Using database: {config.database.database}')
        else:
            # Validate Neo4j configuration (for backward compatibility)
            if not config.neo4j.uri or not config.neo4j.user or not config.neo4j.password:
                raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set for Neo4j')
            
            # Use Neo4j configuration
            db_uri = config.neo4j.uri
            db_user = config.neo4j.user
            db_password = config.neo4j.password
            
            logger.info(f'Using Neo4j at {db_uri}')

        embedder_client = config.embedder.create_client()
        cross_encoder_client = config.llm.create_cross_encoder_client()

        # Initialize Graphiti client with the appropriate database configuration
        graphiti_client = Graphiti(
            uri=db_uri,
            user=db_user,
            password=db_password,
            llm_client=llm_client,
            embedder=embedder_client,
            cross_encoder=cross_encoder_client,
            db_type=db_type,
            namespace=config.database.namespace if db_type == DatabaseType.SURREALDB else None,
            database=config.database.database if db_type == DatabaseType.SURREALDB else None,
        )

        # Destroy graph if requested
        if config.destroy_graph:
            logger.info('Destroying graph...')
            await clear_data(graphiti_client.driver)

        # Initialize the graph database with Graphiti's indices
        await graphiti_client.build_indices_and_constraints()
        logger.info('Graphiti client initialized successfully')

        # Log configuration details for transparency
        if llm_client:
            logger.info(f'Using OpenAI model: {config.llm.model}')
            logger.info(f'Using temperature: {config.llm.temperature}')
        else:
            logger.info('No LLM client configured - entity extraction will be limited')

        logger.info(f'Using group_id: {config.group_id}')
        logger.info(
            f'Custom entity extraction: {"enabled" if config.use_custom_entities else "disabled"}'
        )

    except Exception as e:
        logger.error(f'Failed to initialize Graphiti: {str(e)}')
        raise
