# 🚀 Quick Start Guide - C4 Architecture Generator

Get up and running with the C4 Architecture Generator in minutes!

## ⚡ Quick Setup (5 minutes)

### 1. Prerequisites Check
```bash
# Check Python version (3.8+ required)
python --version

# Check if pip is available
pip --version
```

### 2. Install Dependencies
```bash
# Navigate to project directory
cd langgraph_c4_generator

# Install required packages
pip install -r requirements.txt
```

### 3. Set OpenAI API Key
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Or create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 4. Test Installation
```bash
# Navigate to c_gen_new directory
cd c_gen_new

# Run the test script
python test_installation.py
```

## 🎯 Your First C4 Diagram

### 1. Create a Simple Technical Specification
```python
# Create a file called my_first_diagram.py
from c_gen_new.c4_generator_new import generate_c4_architecture, save_dsl_files

# Define your system
spec = """
The system is a simple web application with:
1. Frontend: React web app that users interact with
2. Backend: Node.js API server that handles requests
3. Database: PostgreSQL that stores user data
4. External: Payment gateway API for processing payments

Users interact with the Frontend, which sends requests to the Backend.
The Backend processes requests, stores data in the Database, and
communicates with the Payment gateway when needed.
"""

# Generate C4 architecture
result = generate_c4_architecture(spec)

if result.get("success"):
    # Save the generated DSL files
    saved_files = save_dsl_files(result, "my_first_diagram")
    print(f"Generated {len(saved_files)} files!")
```

### 2. Run Your First Generation
```bash
python my_first_diagram.py
```

### 3. View Results
Check the `my_first_diagram/` directory for:
- `system_context.dsl` - High-level system overview
- `container.dsl` - Container-level architecture
- `component.dsl` - Detailed component view
- `architecture_summary.json` - Summary of all elements

## 🎮 Interactive Demo

### Run the Built-in Examples
```bash
cd c_gen_new
python demo_c4_generator.py
```

Choose from:
1. **Simple Web Application** - Basic 3-tier architecture
2. **Microservices Architecture** - Complex distributed system
3. **Data Pipeline System** - ETL and analytics workflow
4. **Custom Specification** - Input your own system description

## 📚 Common Use Cases

### 1. System Documentation
```python
# Generate documentation for existing systems
spec = """
Our current system includes:
1. Legacy mainframe for core business logic
2. Web interface for modern user access
3. Integration layer for connecting systems
4. Reporting database for analytics
"""
```

### 2. Architecture Review
```python
# Review proposed architecture changes
spec = """
The proposed new architecture will have:
1. Microservices replacing monolithic backend
2. Event-driven communication via message queue
3. Containerized deployment with Kubernetes
4. Multi-region database replication
"""
```

### 3. Technical Specifications
```python
# Convert technical specs to visual diagrams
spec = """
Technical Requirements:
1. RESTful API with OpenAPI 3.0 specification
2. JWT-based authentication and authorization
3. Redis caching layer for performance
4. PostgreSQL with connection pooling
5. Docker containerization
6. CI/CD pipeline with automated testing
"""
```

## 🔧 Customization

### Modify Prompts
```python
# Customize the analysis prompts in c4_generator_new.py
prompt = f"""
You are a specialized {domain} architect. Analyze this specification:
{state["raw_spec"]}

Focus on {specific_aspects} and provide {custom_output_format}.
"""
```

### Add New Agents
```python
def custom_validation_node(state: C4State) -> C4State:
    """Custom validation logic"""
    # Your custom validation here
    return state

# Add to workflow
workflow.add_node("custom_validation", custom_validation_node)
workflow.add_edge("parse_spec", "custom_validation")
```

## 🚨 Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `OPENAI_API_KEY not set` | Set environment variable: `export OPENAI_API_KEY="your-key"` |
| Import errors | Install dependencies: `pip install -r requirements.txt` |
| API rate limits | Check OpenAI usage dashboard |
| Memory issues | Break large specs into smaller parts |
| Parsing errors | Make your technical specification more detailed |

### Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check workflow state at each step
print(f"Current state: {state}")
```

## 📖 Next Steps

1. **Explore Examples**: Run through all demo scenarios
2. **Customize Prompts**: Adapt to your specific domain
3. **Integrate with CI/CD**: Generate diagrams automatically
4. **Share Results**: Use generated DSL with Structurizr tools
5. **Contribute**: Submit improvements and new features

## 🆘 Need Help?

- **Check the README.md** for comprehensive documentation
- **Run test_installation.py** to diagnose setup issues
- **Review error messages** for specific guidance
- **Check OpenAI API status** if experiencing API issues

---

**Ready to generate your first C4 diagram? Let's go! 🏗️✨**
