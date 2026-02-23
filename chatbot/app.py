"""
Knowledge Chat Bot using LangChain and Neo4j
"""
import os
import time
from flask import Flask, request, jsonify, render_template_string
from neo4j import GraphDatabase
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_openai import ChatOpenAI

app = Flask(__name__)


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


# Get configuration from environment
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Wait for Neo4j
wait_for_neo4j(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

# Initialize Neo4j graph
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USER,
    password=NEO4J_PASSWORD
)

# Initialize the chatbot chain only if OpenAI API key is provided
qa_chain = None
if OPENAI_API_KEY and OPENAI_API_KEY != "your-api-key-here":
    try:
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
        qa_chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=graph,
            verbose=True,
            return_intermediate_steps=True
        )
        print("ChatBot initialized with OpenAI")
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI chain: {e}")
else:
    print("Warning: No valid OpenAI API key provided. Using fallback query mode.")


# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Knowledge Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .chat-container {
            margin-top: 20px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .user-message {
            background-color: #e3f2fd;
            text-align: right;
        }
        .bot-message {
            background-color: #f1f8e9;
        }
        .input-container {
            margin-top: 20px;
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .info {
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .stats {
            background-color: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Knowledge Chat Bot</h1>
        <div class="info">
            <strong>Powered by:</strong> Neo4j Knowledge Graph + LangChain
        </div>
        
        <div class="stats">
            <h3>Knowledge Graph Stats</h3>
            <div id="stats">Loading stats...</div>
        </div>
        
        <div class="chat-container" id="chat-container">
            <!-- Messages will appear here -->
        </div>
        
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Ask a question about Python, frameworks, or libraries..." 
                   onkeypress="if(event.keyCode==13) sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <script>
        // Load stats on page load
        fetch('/stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('stats').innerHTML = 
                    `<p>Total Nodes: ${data.nodes} | Total Relationships: ${data.relationships}</p>`;
            });
        
        function addMessage(text, isUser) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
            messageDiv.innerHTML = '<strong>' + (isUser ? 'You: ' : 'Bot: ') + '</strong>' + text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function sendMessage() {
            const input = document.getElementById('user-input');
            const question = input.value.trim();
            
            if (!question) return;
            
            addMessage(question, true);
            input.value = '';
            
            fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.answer || data.error || 'No response', false);
            })
            .catch(error => {
                addMessage('Error: ' + error, false);
            });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def home():
    """Serve the chat interface"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/stats')
def stats():
    """Get knowledge graph statistics"""
    try:
        nodes = graph.query("MATCH (n) RETURN count(n) as count")[0]['count']
        relationships = graph.query("MATCH ()-[r]->() RETURN count(r) as count")[0]['count']
        return jsonify({
            'nodes': nodes,
            'relationships': relationships
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/query', methods=['POST'])
def query():
    """Handle chat queries"""
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        # If OpenAI is configured, use the QA chain
        if qa_chain:
            result = qa_chain.invoke({"query": question})
            return jsonify({
                'answer': result.get('result', 'No answer found'),
                'query': result.get('intermediate_steps', [{}])[0].get('query', '') if result.get('intermediate_steps') else ''
            })
        else:
            # Fallback: Use simple keyword matching to find relevant nodes
            result = simple_query(question)
            return jsonify({'answer': result})
    except Exception as e:
        print(f"Error processing query: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error processing query: {str(e)}'}), 500


def simple_query(question):
    """Simple fallback query without OpenAI"""
    question_lower = question.lower()
    
    # Try to find relevant nodes based on keywords
    keywords = question_lower.split()
    
    # Search for matching entities
    cypher_query = """
    MATCH (n)
    WHERE toLower(n.name) CONTAINS $keyword OR toLower(n.description) CONTAINS $keyword
    RETURN n.name as name, n.type as type, n.description as description
    LIMIT 5
    """
    
    results = []
    for keyword in keywords:
        if len(keyword) > 3:  # Only search for words longer than 3 characters
            try:
                matches = graph.query(cypher_query, params={"keyword": keyword})
                results.extend(matches)
            except Exception:
                pass
    
    if results:
        response = "I found the following information:\n\n"
        seen = set()
        for r in results:
            if r['name'] not in seen:
                seen.add(r['name'])
                response += f"• {r['name']} ({r['type']})"
                if r.get('description'):
                    response += f": {r['description']}"
                response += "\n"
        return response
    else:
        # If no matches, return general info
        return ("I couldn't find specific information about that. Try asking about:\n"
                "• Python programming language\n"
                "• Web frameworks (Django, Flask, FastAPI)\n"
                "• AI/ML libraries (LangChain, PyTorch, TensorFlow)\n"
                "• Data libraries (Pandas, NumPy)")


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'chatbot'})


if __name__ == '__main__':
    print("Starting Knowledge Chat Bot...")
    print(f"Neo4j URI: {NEO4J_URI}")
    print(f"OpenAI configured: {bool(qa_chain)}")
    # Get debug mode from environment, default to False for production safety
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    app.run(host='0.0.0.0', port=8000, debug=debug_mode)
