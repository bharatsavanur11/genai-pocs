# C4 Architecture Generator using LangGraph

A comprehensive Python solution for generating C4 architecture diagrams from technical specifications using LangGraph workflow. This tool can automatically generate Structurizr DSL code for System Context, Container, and Component diagrams.

## 🚀 Features

- **Multi-Level C4 Diagrams**: Generates diagrams at all C4 levels (Context, Container, Component)
- **Intelligent Parsing**: Uses AI to analyze technical specifications and extract architectural elements
- **LangGraph Workflow**: Implements a sophisticated multi-agent workflow for robust architecture generation
- **Structurizr DSL Output**: Generates ready-to-use DSL code for visualization tools
- **Relationship Mapping**: Automatically identifies and maps relationships between systems, containers, and components
- **Technology Detection**: Recognizes technology stacks and implementation details
- **Validation & Review**: Includes validation steps to ensure architectural consistency

## 📋 What is C4 Architecture?

C4 is a hierarchical way of thinking about and documenting software architecture, based on the context, containers, components, and code (C4) model. It provides different levels of abstraction:

- **Level 1: System Context Diagram** - Shows the system in its environment
- **Level 2: Container Diagram** - Shows the high-level technical building blocks
- **Level 3: Component Diagram** - Shows the major components within a container
- **Level 4: Code Diagram** - Shows the implementation details (not covered in this generator)

## 🏗️ Architecture

The generator uses a LangGraph workflow with specialized agents:

1. **Parse Spec Node**: Analyzes technical specifications and extracts C4 elements
2. **Validate Architecture Node**: Reviews and validates the extracted architecture
3. **Generate Context DSL Node**: Creates System Context Diagram DSL
4. **Generate Container DSL Node**: Creates Container Diagram DSL
5. **Generate Component DSL Node**: Creates Component Diagram DSL
6. **Final Review Node**: Performs comprehensive review and summary

## 📦 Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd langgraph_c4_generator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## 🎯 Usage

### Basic Usage

```python
from c_gen_new.c4_generator_new import generate_c4_architecture, save_dsl_files

# Define your technical specification
spec = """
The system is a web application with:
1. Frontend: React web app
2. Backend: Node.js API server
3. Database: PostgreSQL
4. External: Payment gateway API
"""

# Generate C4 architecture
result = generate_c4_architecture(spec)

if result.get("success"):
    # Save generated DSL files
    saved_files = save_dsl_files(result, "output_directory")
    print(f"Generated {len(saved_files)} files")
```

### Running the Demo

```bash
cd c_gen_new
python demo_c4_generator.py
```

The demo provides several examples:
- Simple Web Application
- Microservices Architecture
- Data Pipeline System
- Custom Technical Specification

## 📝 Input Format

The generator accepts technical specifications in natural language. Here are some examples:

### Simple Web App
```
The system is a simple web application with:
1. A web browser (client) that users interact with
2. A web server that handles HTTP requests
3. A database that stores user data
4. An external payment gateway API
```

### Microservices
```
The system is a microservices-based platform with:
1. User Service: Manages authentication and profiles
2. Product Service: Handles product catalog
3. Order Service: Processes orders
4. API Gateway: Routes requests
5. Message Queue: Handles communication
```

## 📊 Output

The generator produces:

1. **System Context DSL** (`system_context.dsl`): High-level system overview
2. **Container DSL** (`container.dsl`): Container-level architecture
3. **Component DSL** (`component.dsl`): Detailed component view
4. **Architecture Summary** (`architecture_summary.json`): JSON summary of all elements

### Sample Output Structure

```json
{
  "success": true,
  "summary": "Generated C4 architecture for e-commerce platform...",
  "systems": [
    {
      "name": "E-commerce Platform",
      "description": "Main business system",
      "technology": "Microservices",
      "tags": ["business", "core"]
    }
  ],
  "containers": [
    {
      "name": "User Service",
      "system": "E-commerce Platform",
      "description": "User management service",
      "technology": "Java Spring Boot",
      "tags": ["service", "user"]
    }
  ],
  "components": [...],
  "relationships": [...],
  "dsl": {
    "context": "workspace { ... }",
    "container": "workspace { ... }",
    "component": "workspace { ... }"
  }
}
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for OpenAI API access

### Model Configuration

The generator uses GPT-4 by default. You can modify the model in the agent functions:

```python
llm = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0.1)
```

## 🎨 Customization

### Adding New Agents

To add new agents to the workflow:

```python
def custom_agent_node(state: C4State) -> C4State:
    """Custom agent logic"""
    # Your custom logic here
    return state

# Add to workflow
workflow.add_node("custom_agent", custom_agent_node)
workflow.add_edge("previous_node", "custom_agent")
```

### Modifying Prompts

Each agent has customizable prompts. You can modify them to suit your specific needs:

```python
prompt = f"""
Your custom prompt here with {variables}
"""
```

## 📚 Examples

### Example 1: E-commerce Platform

```python
spec = """
The system is a modern e-commerce platform with:
1. Frontend System: React-based web application
2. API Gateway: Node.js service for routing
3. User Service: Java Spring Boot for user management
4. Product Service: Python FastAPI for catalog
5. Order Service: Go service for order processing
6. Payment Service: .NET Core for payments
7. Database Layer: PostgreSQL, MongoDB, Redis
8. Message Queue: Apache Kafka
9. External Systems: Stripe, SendGrid, Twilio
"""
```

### Example 2: Data Pipeline

```python
spec = """
The system is a data processing pipeline with:
1. Data Sources: External APIs and databases
2. Data Collector: Service for data ingestion
3. Data Processor: Service for data transformation
4. Data Warehouse: Centralized storage
5. Analytics Engine: Query and reporting service
6. Dashboard: Web interface for visualization
7. Alert Service: Monitoring and notifications
"""
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure `OPENAI_API_KEY` is set correctly
2. **Parsing Errors**: Check that your technical specification is clear and detailed
3. **Memory Issues**: For large specifications, consider breaking them into smaller parts

### Debug Mode

Enable debug output by modifying the agent functions to include more detailed logging.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Bug reports
- Feature requests
- Documentation improvements
- Code optimizations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [OpenAI](https://openai.com/)
- Inspired by [C4 Model](https://c4model.com/) methodology
- Uses [Structurizr](https://structurizr.com/) DSL format

## 📞 Support

For support and questions:

1. Check the existing issues
2. Create a new issue with detailed description
3. Provide your technical specification and error details

---

**Happy Architecture Generation! 🏗️✨**
