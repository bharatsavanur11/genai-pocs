# Quick Start Guide - C4 Architecture Diagram Generator

## 🚀 What You've Got

A powerful tool that automatically generates C4 model diagrams from technical specifications using LangGraph and OpenAI's GPT models.

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **OpenAI API key** (get one from [OpenAI](https://platform.openai.com/))
3. **Dependencies** installed (see Installation below)

## ⚡ Quick Installation

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# 3. Test the installation
python3 test_installation.py
```

## 🎯 Quick Usage

### Option 1: Web Interface (Recommended for beginners)
```bash
streamlit run c4_with_excel_tech_spec.py
```
- Open your browser to the displayed URL
- Enter your technical specification
- Upload Excel files (optional)
- Click "Generate C4 Diagram"
- Download the generated DSL file

### Option 2: Command Line
```bash
python3 c4_with_excel_tech_spec.py your_spec_file.txt
```

### Option 3: Programmatic
```python
from c4_with_excel_tech_spec import generate_c4_from_spec

spec = """
The system is a web application with:
- A web server that handles HTTP requests
- A database that stores user data
- An external payment API for transactions

Users interact with the web server, which queries the database and communicates with the payment API.
"""

result = generate_c4_from_spec(spec)
print(result['dsl'])  # Generated Structurizr DSL
```

## 📝 Technical Specification Format

Write your specification in natural language, describing:

1. **Components**: What systems, services, or applications exist
2. **Responsibilities**: What each component does
3. **Interactions**: How components communicate with each other
4. **Technologies**: What technologies are used (optional)

### Example Specification
```
The system is a microservices-based e-commerce platform with:

1. User Service: Manages user authentication and profiles
2. Product Service: Handles product catalog and inventory
3. Order Service: Processes orders and manages lifecycle
4. API Gateway: Routes requests to appropriate services
5. Database Cluster: Stores data for all services

The API Gateway receives requests and routes them to services. Services communicate 
through a message queue for asynchronous operations. Each service has its own 
database within the cluster.
```

## 🔧 What Gets Generated

1. **System Summary**: Concise description of the architecture
2. **Component List**: All identified components with types and descriptions
3. **Relationship Map**: Interactions between components
4. **Structurizr DSL**: Ready-to-use code for C4 diagram tools

## 📊 Output Format

The generator produces Structurizr DSL code that you can use with:

- [Structurizr](https://structurizr.com/) (online)
- [Structurizr CLI](https://github.com/structurizr/cli)
- [Structurizr for VS Code](https://marketplace.visualstudio.com/items?itemName=Structurizr.structurizr)
- Other C4 diagram tools

## 🎨 Generated DSL Example

```dsl
workspace {
    name "C4 Architecture Diagram"
    description "Generated from technical specification"
    
    model {
        user_service = component "User Service" "Manages user authentication"
        product_service = component "Product Service" "Handles product catalog"
        api_gateway = component "API Gateway" "Routes requests to services"
        
        api_gateway -> user_service "Routes user requests"
        api_gateway -> product_service "Routes product requests"
    }
    
    views {
        component system "Components" "Component Diagram" {
            include *
        }
    }
}
```

## 🧪 Test Without API Key

```bash
# Run the demo to see how it works
python3 simple_example.py

# Run comprehensive examples
python3 example_usage.py
```

## 🆘 Troubleshooting

### Common Issues

1. **"No module named 'langgraph'"**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **"OpenAI API key not found"**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

3. **Syntax errors**
   ```bash
   python3 -m py_compile c4_with_excel_tech_spec.py
   ```

### Getting Help

1. Check the troubleshooting section in `README_C4_Generator.md`
2. Run `python3 test_installation.py` to diagnose issues
3. Check the examples in `example_usage.py`

## 🔄 Workflow

The system uses a LangGraph workflow with four agents:

1. **Parse Spec** → Extracts components and relationships
2. **Request Info** → Identifies missing information (if any)
3. **Summarize** → Creates system summary
4. **Generate DSL** → Produces Structurizr DSL code

## 📁 File Structure

```
langgraph_c4_generator/
├── c4_with_excel_tech_spec.py    # Main generator
├── example_usage.py              # Comprehensive examples
├── simple_example.py             # Basic demo
├── test_installation.py          # Installation test
├── requirements.txt              # Dependencies
├── README_C4_Generator.md       # Full documentation
└── QUICK_START.md               # This file
```

## 🎉 Next Steps

1. **Try the web interface**: `streamlit run c4_with_excel_tech_spec.py`
2. **Run examples**: `python3 example_usage.py`
3. **Read full docs**: `README_C4_Generator.md`
4. **Customize**: Modify prompts and workflows for your needs

## 💡 Pro Tips

- **Be specific** in your technical specifications
- **Include relationships** between components
- **Mention technologies** when relevant
- **Use Excel files** for complex specifications
- **Start simple** and iterate

---

**Need help?** Check the full documentation in `README_C4_Generator.md` or run the test scripts to diagnose issues.
