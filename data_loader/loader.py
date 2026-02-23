"""
Data Loader for Knowledge Graph
Populates Neo4j with sample knowledge using LangChain
"""
import os
import time
from neo4j import GraphDatabase
from langchain_community.graphs import Neo4jGraph


def wait_for_neo4j(uri, user, password, max_retries=30):
    """Wait for Neo4j to be ready"""
    print("Waiting for Neo4j to be ready...")
    for i in range(max_retries):
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            driver.verify_connectivity()
            driver.close()
            print("Neo4j is ready!")
            return True
        except Exception as e:
            print(f"Attempt {i+1}/{max_retries}: Neo4j not ready yet - {e}")
            time.sleep(2)
    return False


def load_sample_data():
    """Load sample knowledge into Neo4j"""
    # Get connection details from environment variables
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password123")
    
    # Wait for Neo4j to be ready
    if not wait_for_neo4j(uri, user, password):
        print("Failed to connect to Neo4j")
        return
    
    try:
        # Initialize Neo4j graph
        graph = Neo4jGraph(
            url=uri,
            username=user,
            password=password
        )
        
        print("Clearing existing data...")
        # Clear existing data
        graph.query("MATCH (n) DETACH DELETE n")
        
        print("Loading sample knowledge...")
        
        # Create sample knowledge about Python programming
        queries = [
            # Python language facts
            """
            CREATE (python:Language {name: 'Python', type: 'Programming Language', 
                    created: 1991, creator: 'Guido van Rossum'})
            """,
            
            # Popular frameworks
            """
            CREATE (django:Framework {name: 'Django', type: 'Web Framework', 
                    description: 'High-level Python web framework'})
            CREATE (flask:Framework {name: 'Flask', type: 'Web Framework', 
                    description: 'Lightweight Python web framework'})
            CREATE (fastapi:Framework {name: 'FastAPI', type: 'Web Framework', 
                    description: 'Modern, fast web framework for APIs'})
            """,
            
            # AI/ML libraries
            """
            CREATE (langchain:Library {name: 'LangChain', type: 'AI Library', 
                    description: 'Framework for developing LLM applications'})
            CREATE (pytorch:Library {name: 'PyTorch', type: 'ML Library', 
                    description: 'Machine learning framework'})
            CREATE (tensorflow:Library {name: 'TensorFlow', type: 'ML Library', 
                    description: 'Machine learning framework'})
            """,
            
            # Data science tools
            """
            CREATE (pandas:Library {name: 'Pandas', type: 'Data Library', 
                    description: 'Data manipulation and analysis'})
            CREATE (numpy:Library {name: 'NumPy', type: 'Data Library', 
                    description: 'Numerical computing'})
            """,
            
            # Create relationships
            """
            MATCH (python:Language {name: 'Python'})
            MATCH (django:Framework {name: 'Django'})
            MATCH (flask:Framework {name: 'Flask'})
            MATCH (fastapi:Framework {name: 'FastAPI'})
            CREATE (django)-[:BUILT_WITH]->(python)
            CREATE (flask)-[:BUILT_WITH]->(python)
            CREATE (fastapi)-[:BUILT_WITH]->(python)
            """,
            
            """
            MATCH (python:Language {name: 'Python'})
            MATCH (langchain:Library {name: 'LangChain'})
            MATCH (pytorch:Library {name: 'PyTorch'})
            MATCH (tensorflow:Library {name: 'TensorFlow'})
            MATCH (pandas:Library {name: 'Pandas'})
            MATCH (numpy:Library {name: 'NumPy'})
            CREATE (langchain)-[:BUILT_WITH]->(python)
            CREATE (pytorch)-[:BUILT_WITH]->(python)
            CREATE (tensorflow)-[:BUILT_WITH]->(python)
            CREATE (pandas)-[:BUILT_WITH]->(python)
            CREATE (numpy)-[:BUILT_WITH]->(python)
            """,
            
            # Add some use cases
            """
            CREATE (webapp:UseCase {name: 'Web Application', 
                    description: 'Building web applications and APIs'})
            CREATE (ai:UseCase {name: 'AI/ML Development', 
                    description: 'Building AI and machine learning applications'})
            CREATE (data:UseCase {name: 'Data Analysis', 
                    description: 'Analyzing and processing data'})
            """,
            
            """
            MATCH (webapp:UseCase {name: 'Web Application'})
            MATCH (django:Framework {name: 'Django'})
            MATCH (flask:Framework {name: 'Flask'})
            MATCH (fastapi:Framework {name: 'FastAPI'})
            CREATE (webapp)-[:USES]->(django)
            CREATE (webapp)-[:USES]->(flask)
            CREATE (webapp)-[:USES]->(fastapi)
            """,
            
            """
            MATCH (ai:UseCase {name: 'AI/ML Development'})
            MATCH (langchain:Library {name: 'LangChain'})
            MATCH (pytorch:Library {name: 'PyTorch'})
            MATCH (tensorflow:Library {name: 'TensorFlow'})
            CREATE (ai)-[:USES]->(langchain)
            CREATE (ai)-[:USES]->(pytorch)
            CREATE (ai)-[:USES]->(tensorflow)
            """,
            
            """
            MATCH (data:UseCase {name: 'Data Analysis'})
            MATCH (pandas:Library {name: 'Pandas'})
            MATCH (numpy:Library {name: 'NumPy'})
            CREATE (data)-[:USES]->(pandas)
            CREATE (data)-[:USES]->(numpy)
            """
        ]
        
        for query in queries:
            graph.query(query)
        
        print("Sample data loaded successfully!")
        
        # Verify data
        result = graph.query("MATCH (n) RETURN count(n) as count")
        print(f"Total nodes created: {result[0]['count']}")
        
        result = graph.query("MATCH ()-[r]->() RETURN count(r) as count")
        print(f"Total relationships created: {result[0]['count']}")
        
        print("\nKnowledge graph populated successfully!")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting data loader...")
    load_sample_data()
    print("Data loader completed.")
