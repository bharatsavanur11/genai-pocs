# C4 Architecture Diagram Generator

A powerful tool that automatically generates C4 model diagrams from technical specifications using LangGraph and OpenAI's GPT models.

## Features

- **Automatic C4 Model Generation**: Converts natural language technical specifications into structured C4 diagrams
- **LangGraph Workflow**: Uses a multi-agent workflow to parse, analyze, and generate diagrams
- **Excel Integration**: Supports additional data from Excel files for enhanced specifications
- **Multiple C4 Levels**: Automatically determines and generates appropriate C4 levels (Context, Container, Component)
- **Structurizr DSL Output**: Generates ready-to-use Structurizr DSL code
- **Web Interface**: Streamlit-based web application for easy interaction
- **Command Line Support**: Can be used programmatically or from command line
- **Smart Component Detection**: Automatically identifies software systems, containers, components, and external systems
- **Relationship Mapping**: Maps interactions and dependencies between components

## Architecture

The system uses a LangGraph workflow with four main agents:

1. **Parse Spec Node**: Analyzes technical specifications and extracts C4 components and relationships
2. **Request Info Node**: Identifies missing information and requests clarification
3. **Summarize Node**: Creates a concise summary of system requirements
4. **Generate DSL Node**: Produces Structurizr DSL code for the C4 diagram

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd langgraph_c4_generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### 1. Web Interface (Recommended)

Run the Streamlit web application:
```bash
streamlit run c4_with_excel_tech_spec.py
```

This provides a user-friendly interface where you can:
- Enter technical specifications in natural language
- Upload Excel files with additional data
- Generate C4 diagrams interactively
- Download the generated DSL files

### 2. Command Line Usage

Generate C4 diagrams from a specification file:
```bash
python c4_with_excel_tech_spec.py your_spec_file.txt
```

### 3. Programmatic Usage

```python
from c4_with_excel_tech_spec import generate_c4_from_spec

# Define your technical specification
spec = """
The system is a web application with:
- A web server that handles HTTP requests
- A database that stores user data
- An external payment API for transactions

Users interact with the web server, which queries the database and communicates with the payment API.
"""

# Generate the C4 diagram
result = generate_c4_from_spec(spec)

# Access the results
print(f"Summary: {result['summary']}")
print(f"Components: {len(result['components'])}")
print(f"Relationships: {len(result['relationships'])}")
print(f"DSL Code:\n{result['dsl']}")
```

### 4. Example Usage

Run the provided examples:
```bash
python example_usage.py
```

This will generate three example C4 diagrams:
- Simple web application
- Microservices architecture
- Data pipeline system

## Technical Specification Format

The generator works best with specifications that clearly describe:

1. **Components**: What systems, services, or applications exist
2. **Responsibilities**: What each component does
3. **Interactions**: How components communicate with each other
4. **Technologies**: What technologies are used (optional)
5. **External Systems**: Any third-party services or APIs

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

## Excel Integration

You can enhance your specifications by uploading Excel files containing:

- Component details
- Technology stacks
- Configuration parameters
- Additional metadata

The system will automatically incorporate this data into the C4 model generation.

## Output

The generator produces:

1. **System Summary**: A concise description of the architecture
2. **Component List**: All identified components with types and descriptions
3. **Relationship Map**: Interactions between components
4. **Structurizr DSL**: Ready-to-use code for C4 diagram tools

## Generated DSL Structure

The output follows Structurizr DSL format:

```dsl
workspace {
    name "C4 Architecture Diagram"
    description "Generated from technical specification"
    
    model {
        // Component definitions
        user_service = component "User Service" "Manages user authentication"
        product_service = component "Product Service" "Handles product catalog"
        
        // Relationships
        user_service -> product_service "Queries product information"
    }
    
    views {
        component system "Components" "Component Diagram" {
            include *
        }
    }
}
```

## Supported C4 Levels

The generator automatically determines the appropriate C4 level:

- **Context Level**: System context and external dependencies
- **Container Level**: Application containers and deployment
- **Component Level**: Internal components and services
- **Code Level**: Detailed code structure (basic support)

## Customization

You can customize the generator by:

1. **Modifying Prompts**: Adjust the LLM prompts in each node for specific domains
2. **Adding Components**: Extend the component type detection
3. **Custom Views**: Modify the DSL generation for specific diagram types
4. **Integration**: Connect with other tools in your workflow

## Dependencies

- `langgraph`: Workflow orchestration
- `langchain_openai`: OpenAI integration
- `pandas`: Excel file processing
- `streamlit`: Web interface
- `python-dotenv`: Environment variable management

## Troubleshooting

### Common Issues

1. **Missing API Key**: Ensure `OPENAI_API_KEY` is set
2. **Parsing Errors**: Check that your specification is clear and well-structured
3. **Component Detection**: Make sure components and relationships are clearly described
4. **Excel Processing**: Verify Excel file format and content

### Debug Mode

Enable debug output by setting:
```bash
export DEBUG=1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Examples

See the `example_usage.py` file for comprehensive examples of different architecture types and the `*.dsl` files for sample outputs.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the examples
3. Open an issue on GitHub
4. Check the LangGraph and Structurizr documentation

## Roadmap

- [ ] Support for more C4 diagram types
- [ ] Integration with additional diagram tools
- [ ] Enhanced Excel processing
- [ ] Custom styling and themes
- [ ] Batch processing capabilities
- [ ] API endpoint for integration
