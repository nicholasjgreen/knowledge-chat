# Knowledge Chat

A multi-container Python application that uses Neo4j as a knowledge graph store with a LangChain-powered chatbot interface.

## Architecture

This application consists of three main services orchestrated with Docker Compose:

1. **Neo4j Container** - Graph database for storing knowledge
2. **Chatbot Service** - Python Flask web application with LangChain integration
3. **Data Loader Service** - Python service to populate the knowledge graph

## Features

- 🗄️ Neo4j graph database for structured knowledge storage
- 🤖 Interactive chatbot powered by LangChain
- 🌐 Web-based chat interface
- 📊 Knowledge graph visualization and statistics
- 🔄 Automated data loading on startup
- 🐳 Fully containerized with Docker

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- Optional: OpenAI API key for advanced chatbot features

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nicholasjgreen/knowledge-chat.git
   cd knowledge-chat
   ```

2. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key if you want advanced AI features
   ```

3. **Start all services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the services:**
   - Chatbot Web Interface: http://localhost:8000
   - Neo4j Browser: http://localhost:7474
     - Username: `neo4j`
     - Password: `password123`

## Service Details

### Neo4j Database
- **Ports:** 7474 (HTTP), 7687 (Bolt)
- **Credentials:** neo4j / password123
- **Data:** Persisted in Docker volumes

### Chatbot Service
- **Port:** 8000
- **Framework:** Flask + LangChain
- **Features:**
  - Web-based chat interface
  - Natural language queries
  - Knowledge graph integration
  - OpenAI integration (optional)

### Data Loader Service
- Runs once on startup
- Populates Neo4j with sample knowledge about:
  - Python programming language
  - Web frameworks (Django, Flask, FastAPI)
  - AI/ML libraries (LangChain, PyTorch, TensorFlow)
  - Data science tools (Pandas, NumPy)

## Usage

### Using the Chatbot

1. Open your browser to http://localhost:8000
2. Type questions in the chat interface, such as:
   - "What is Python?"
   - "Tell me about Django"
   - "What frameworks are built with Python?"
   - "What libraries are used for AI development?"

### Querying Neo4j Directly

Access the Neo4j Browser at http://localhost:7474 and run Cypher queries:

```cypher
// View all nodes
MATCH (n) RETURN n LIMIT 25

// Find all frameworks
MATCH (f:Framework) RETURN f

// Find what Python is used for
MATCH (p:Language {name: 'Python'})<-[:BUILT_WITH]-(n)
RETURN p, n
```

## Development

### Project Structure

```
knowledge-chat/
├── chatbot/
│   ├── Dockerfile
│   ├── app.py              # Flask chatbot application
│   └── requirements.txt    # Python dependencies
├── data_loader/
│   ├── Dockerfile
│   ├── loader.py           # Data loading script
│   └── requirements.txt    # Python dependencies
├── docker-compose.yml      # Multi-container orchestration
├── .env.example           # Environment variable template
└── README.md
```

### Customizing the Knowledge Graph

Edit `data_loader/loader.py` to add your own knowledge:

```python
# Add new nodes
graph.query("""
    CREATE (node:CustomType {name: 'MyNode', description: 'My description'})
""")

# Add relationships
graph.query("""
    MATCH (a:TypeA {name: 'NodeA'})
    MATCH (b:TypeB {name: 'NodeB'})
    CREATE (a)-[:RELATIONSHIP_TYPE]->(b)
""")
```

Then restart the services:
```bash
docker-compose restart data_loader
```

### Stopping the Services

```bash
docker-compose down
```

To remove all data (including Neo4j database):
```bash
docker-compose down -v
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://neo4j:7687` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `password123` | Neo4j password |
| `OPENAI_API_KEY` | `your-api-key-here` | OpenAI API key (optional) |

## Troubleshooting

### Services not starting
- Ensure Docker and Docker Compose are installed and running
- Check that ports 7474, 7687, and 8000 are not in use

### Neo4j connection issues
- Wait for the Neo4j health check to pass (can take 30-60 seconds)
- Check logs: `docker-compose logs neo4j`

### Data not loading
- Check data loader logs: `docker-compose logs data_loader`
- Ensure Neo4j is healthy before data loader starts

### Chatbot not responding
- Check chatbot logs: `docker-compose logs chatbot`
- Verify Neo4j contains data: Access Neo4j Browser and run `MATCH (n) RETURN count(n)`

## Technologies Used

- **Neo4j**: Graph database
- **Python**: Application language
- **LangChain**: Framework for LLM applications
- **Flask**: Web framework
- **Docker**: Containerization
- **OpenAI**: Optional AI enhancement

## License

This project is licensed under the terms specified in the LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
