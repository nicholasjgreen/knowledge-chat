# Quick Start Guide

This is a quick reference for getting the Knowledge Chat application up and running.

## Start the Application

```bash
# Clone the repository
git clone https://github.com/nicholasjgreen/knowledge-chat.git
cd knowledge-chat

# Start all services
docker compose up --build
```

## Access the Services

- **Chatbot**: http://localhost:8000
- **Neo4j Browser**: http://localhost:7474 (user: neo4j, password: password123)

## Sample Questions to Ask the Chatbot

- "What is Python?"
- "Tell me about Django"
- "What frameworks are built with Python?"
- "What libraries are used for AI development?"
- "Show me data science tools"

## Stop the Application

```bash
# Stop services
docker compose down

# Stop and remove all data
docker compose down -v
```

## Enable Advanced AI Features

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
4. Restart the services:
   ```bash
   docker compose down
   docker compose up --build
   ```

## Troubleshooting

**Services won't start?**
- Ensure ports 7474, 7687, and 8000 are available
- Check Docker is running: `docker --version`

**No data in Neo4j?**
- Wait 30-60 seconds for data loader to complete
- Check logs: `docker compose logs data_loader`

**Chatbot not responding?**
- Check chatbot logs: `docker compose logs chatbot`
- Verify Neo4j is healthy: `docker compose ps`

## Next Steps

See the full [README.md](README.md) for:
- Customizing the knowledge graph
- Development guide
- Complete documentation
