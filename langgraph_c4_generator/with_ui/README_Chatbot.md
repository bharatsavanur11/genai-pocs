# C4 Architecture Generator Chatbot

A Streamlit-based chatbot interface that generates C4 architecture diagrams from technical specifications through natural conversation.

## Features

### 🤖 Smart Chatbot Interface
- **Natural Language Input**: Describe your system architecture in plain English
- **Context Awareness**: Maintains conversation history and builds upon previous inputs
- **Content Filtering**: Automatically filters out irrelevant content, keeping only technical specifications
- **Real-time Generation**: Automatically generates C4 diagrams as you build your specification

### 🏗️ C4 Diagram Generation
- **System Context Diagrams** (Level 1): High-level system overview
- **Container Diagrams** (Level 2): Application and data store details
- **Component Diagrams** (Level 3): Detailed component interactions
- **Unified Views**: Combined context and container diagrams

### 💬 Conversation Management
- **Persistent Context**: Builds comprehensive specifications over multiple conversations
- **Smart Summarization**: Automatically summarizes long specifications to maintain context
- **Example Templates**: Pre-built examples for common system types
- **Export Functionality**: Save conversations and generated diagrams

## Quick Start

### 1. Install Dependencies
```bash
cd with_ui
pip install -r requirements_chatbot.txt
```

### 2. Set Environment Variables
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Chatbot
```bash
streamlit run c4_chatbot_ui.py
```

## How to Use

### Starting a Conversation
1. **Open the chatbot** in your browser
2. **Type your technical specification** in the chat input
3. **Build incrementally** by adding more details over time
4. **View generated diagrams** in real-time

### Example Conversation Flow
```
User: "I need a web application with a React frontend and Node.js backend"

Bot: ✅ Added to technical specification:
     - React frontend web application
     - Node.js backend service

User: "The backend should connect to a PostgreSQL database"

Bot: ✅ Added to technical specification:
     - PostgreSQL database integration
     - Database connection from Node.js backend

[Bot automatically generates updated C4 diagrams]
```

### Building Complex Specifications
- **Start simple**: Begin with basic system components
- **Add details gradually**: Include technology choices, relationships, and external systems
- **Refine iteratively**: Update specifications based on generated diagrams
- **Use examples**: Load pre-built examples as starting points

## Key Features Explained

### Content Filtering
The chatbot automatically identifies and filters content:
- ✅ **Keeps**: System architecture, technology choices, data flows, integrations
- ❌ **Removes**: Personal conversations, non-technical discussions, irrelevant content

### Context Management
- **Maintains conversation history** across sessions
- **Builds comprehensive specifications** from multiple inputs
- **Smart summarization** prevents context overflow
- **Preserves architectural decisions** and relationships

### Real-time Generation
- **Automatic C4 generation** when specifications are substantial
- **Multiple diagram levels** for different architectural views
- **Instant feedback** on specification completeness
- **Export capabilities** for generated DSL files

## Example Use Cases

### 1. E-commerce Platform
```
- React frontend with mobile responsiveness
- Microservices architecture (User, Product, Order services)
- Payment gateway integrations
- Message queue for asynchronous processing
- Multiple database technologies (PostgreSQL, MongoDB, Redis)
```

### 2. Banking System
```
- Customer portal and mobile applications
- Core banking engine with security services
- Compliance and risk management systems
- External integrations (SWIFT, credit bureaus)
- Event-driven architecture with Kafka
```

### 3. Healthcare Platform
```
- Patient and provider portals
- Electronic health record management
- Telemedicine capabilities
- Regulatory compliance systems
- HL7 FHIR API integrations
```

## Output Files

The chatbot generates several types of output:

### DSL Files
- `system_context.dsl`: System context diagrams
- `container.dsl`: Container-level diagrams
- `component.dsl`: Component-level diagrams
- `context_container.dsl`: Unified context and container views

### Data Files
- `architecture_summary.json`: Complete architectural analysis
- `conversation_export.json`: Full conversation history

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for AI-powered content filtering and generation
- `OUTPUT_DIR`: Directory for saving generated files (default: `generated_c4`)

### Customization
- **Model Selection**: Change OpenAI models in the code for different capabilities
- **Context Length**: Adjust `MAX_CONTEXT_LENGTH` for different token limits
- **Filtering Sensitivity**: Modify content filtering prompts for different use cases

## Troubleshooting

### Common Issues

1. **API Key Missing**
   - Ensure `OPENAI_API_KEY` is set in your environment
   - Check the sidebar for API key status

2. **Generation Fails**
   - Verify your technical specification is detailed enough
   - Check for any error messages in the interface
   - Try breaking down complex specifications into smaller parts

3. **Content Not Filtered**
   - The AI filtering may occasionally miss irrelevant content
   - Manually edit the specification context if needed
   - Use the "Clear Specification" button to start fresh

### Performance Tips
- **Keep specifications focused** on architecture and technology
- **Use clear, technical language** for better AI understanding
- **Build incrementally** rather than writing long specifications at once
- **Review generated diagrams** to identify missing components

## Advanced Usage

### Custom Prompts
Modify the filtering and extraction prompts in the code for:
- Different technical domains (IoT, AI/ML, embedded systems)
- Specific architectural patterns (microservices, monoliths, serverless)
- Industry-specific requirements (compliance, security, scalability)

### Integration
- **API Integration**: Use the underlying `generate_c4_architecture` function
- **Batch Processing**: Process multiple specifications programmatically
- **Custom Workflows**: Extend the chatbot for specific use cases

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the generated error messages
3. Ensure all dependencies are properly installed
4. Verify your OpenAI API key is valid and has sufficient credits

## License

This project is part of the C4 Architecture Generator suite. See the main project README for licensing information.
