# Database Adapters for Graphiti

This package implements a strategy pattern with an adapter pattern through interfaces to provide a consistent API for different graph database backends.

## Architecture

- `db_interface.py`: Defines the abstract interface that all database adapters must implement
- `neo4j_adapter.py`: Implements the interface for Neo4j
- `surrealdb_adapter.py`: Implements the interface for SurrealDB
- `db_factory.py`: Factory class to create database adapter instances

## Usage

### Basic Usage

```python
from graphiti_core.database.db_factory import DatabaseFactory, DatabaseType
from graphiti_core import Graphiti

# Create a Graphiti instance with Neo4j
graphiti_neo4j = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    db_type=DatabaseType.NEO4J
)

# Create a Graphiti instance with SurrealDB
graphiti_surrealdb = Graphiti(
    uri="ws://localhost:8001/rpc",  # Note: Port 8001 is mapped to 8000 in Docker
    user="root",
    password="root",
    db_type=DatabaseType.SURREALDB
)
```

### Environment Variables

When using Docker Compose, you can configure the database using environment variables:

```
# For Neo4j
DATABASE_TYPE=neo4j
DATABASE_URI=bolt://neo4j:7687    # Inside Docker network
# or
DATABASE_URI=bolt://localhost:7687  # From your local machine

# For SurrealDB
DATABASE_TYPE=surrealdb  
DATABASE_URI=ws://surrealdb:8000/rpc    # Inside Docker network
# or
DATABASE_URI=ws://localhost:8001/rpc    # From your local machine
DATABASE_USER=root
DATABASE_PASSWORD=root
```

## Docker Compose Configuration

### Neo4j (Default)
```bash
# Start with Neo4j
docker-compose up -d
```

### SurrealDB
```bash
# Start with SurrealDB
docker-compose -f docker-compose-surrealdb.yml up -d
```

The SurrealDB configuration uses the following command in the Docker Compose file:

```yaml
command: start --username ${DATABASE_USER:-root} --password ${DATABASE_PASSWORD:-root} memory
```

## Implementation Details

### Neo4j Adapter

The Neo4j adapter uses the official Neo4j Python driver to connect to a Neo4j database. It implements all operations using Cypher queries.

### SurrealDB Adapter

The SurrealDB adapter uses the official SurrealDB Python client to connect to a SurrealDB instance. It implements all operations using SurrealQL.

Key differences from Neo4j:
- SurrealDB uses WebSocket connections instead of Bolt protocol
- Query language is SurrealQL instead of Cypher
- Different index and constraint mechanisms
- Different transaction models

## Port Configuration

When using SurrealDB with the Docker Compose configuration:
1. SurrealDB runs on port 8000 inside the container
2. Port 8001 on your local machine is mapped to port 8000 in the container
3. When accessing from within Docker, use `ws://surrealdb:8000/rpc`
4. When accessing from your local machine, use `ws://localhost:8001/rpc`

## Adding a New Database Adapter

To add support for a new graph database:

1. Create a new adapter class that implements the `GraphDBInterface`
2. Add the new database type to the `DatabaseType` enum in `db_factory.py`
3. Update the `DatabaseFactory.create_db_adapter()` method to return an instance of your new adapter
4. Add any new dependencies to `pyproject.toml`

Example:

```python
from graphiti_core.database.db_interface import GraphDBInterface

class MyNewDatabaseAdapter(GraphDBInterface):
    # Implement all required methods
    ...

# Then in db_factory.py:
class DatabaseType(str, Enum):
    NEO4J = "neo4j"
    SURREALDB = "surrealdb"
    MY_NEW_DB = "mynewdb"

class DatabaseFactory:
    @staticmethod
    def create_db_adapter(db_type: DatabaseType) -> GraphDBInterface[Any, Any]:
        if db_type == DatabaseType.NEO4J:
            return Neo4jAdapter()
        elif db_type == DatabaseType.SURREALDB:
            return SurrealDBAdapter()
        elif db_type == DatabaseType.MY_NEW_DB:
            return MyNewDatabaseAdapter()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
