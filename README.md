# Orchestrated Multi-Agent System for Architecture Diagram to Terraform

This project implements an advanced orchestrated multi-agent system that processes architecture diagrams and generates Terraform code using multiple Large Language Models (LLMs) with scoring thresholds and intelligent routing.

## 🏗️ Architecture Overview

The system follows a 6-step orchestrated process:

| Step | Process | Component | Pattern | Description |
|------|---------|-----------|---------|-------------|
| 1 | Image Parsing | Gemini | A2A | Specialized vision agent analyzes architecture diagrams |
| 2 | Model Evaluation | GPT-4o | A2A | Evaluates parsing quality with 80% threshold |
| 3 | Terraform Creation | Claude 4 | A2A | Generates production-ready Terraform code |
| 4 | Model Evaluation | GPT-4o | A2A | Validates Terraform code with 80% threshold |
| 5 | Terraform Execution | MCP Client/Server | MCP | Executes Terraform through MCP pattern |
| 6 | Infrastructure Deployment | AWS | MCP | Deploys infrastructure to AWS |

## 🚀 Features

- **Multi-Agent Coordination**: Orchestrates Gemini, GPT-4o, and Claude agents
- **Scoring Thresholds**: 80% evaluation threshold for quality gates
- **Intelligent Routing**: A2A and MCP patterns for different operations
- **Retry Logic**: Automatic retry with exponential backoff
- **Comprehensive Logging**: Detailed execution tracking and metrics
- **Error Handling**: Robust error handling and failure recovery
- **Async Processing**: High-performance async execution

## 📋 Prerequisites

- Python 3.8+
- API Keys for:
  - OpenAI (GPT-4o)
  - Anthropic (Claude)
  - Google (Gemini)

## ⚙️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd aws-terraform-1
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## 🔧 Configuration

Create a `.env` file with the following variables:

```env
# API Keys (Required)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Model Configuration
GEMINI_MODEL=gemini-1.5-pro
GPT4_MODEL=gpt-4o
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Scoring Configuration
EVALUATION_THRESHOLD=80
MAX_RETRIES=3

# Orchestration Settings
ENABLE_PARALLEL_EXECUTION=true
TIMEOUT_SECONDS=300
```

## 🎯 Usage

### Basic Usage

```bash
python main.py path/to/your/architecture_diagram.jpg
```

### Example with Sample Diagram

```bash
python main.py examples/sample_diagrams/AWS_ServerlessD15.jpg
```

### Programmatic Usage

```python
import asyncio
from src.orchestration.orchestrator import MultiAgentOrchestrator, load_config_from_env

async def run_orchestration():
    # Load configuration
    config = load_config_from_env()
    
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator(config)
    await orchestrator.initialize_agents()
    
    # Execute process
    results = await orchestrator.execute_full_process("path/to/image.jpg")
    
    # Get summary
    summary = orchestrator.get_process_summary()
    print(f"Process completed with {summary['successful_steps']} successful steps")

# Run
asyncio.run(run_orchestration())
```

## 📊 Output

The system generates comprehensive output including:

- **Step-by-step execution logs**
- **Evaluation scores for each threshold check**
- **Generated Terraform code**
- **Execution timing metrics**
- **Detailed error reports (if any)**
- **JSON summary file (`orchestration_results.json`)**

### Sample Output

```
🚀 Multi-Agent Orchestration System for Architecture Diagram to Terraform
================================================================================
✅ Configuration loaded successfully
🔧 Initializing agents...
✅ All agents initialized successfully
🔄 Starting orchestration process with image: examples/sample_diagrams/AWS_ServerlessD15.jpg
--------------------------------------------------------------------------------
📊 Process Summary:
Total Steps Executed: 6
Successful Steps: 6
Failed Steps: 0
Total Execution Time: 45.32 seconds
Step 2 Evaluation Score: 87% ✅ PASSED
Step 4 Evaluation Score: 92% ✅ PASSED

📋 Step Details:
  ✅ IMAGE_PARSING: 8.45s
  ✅ MODEL_EVALUATION_1: 12.23s (Score: 87%)
  ✅ TERRAFORM_CREATION: 15.67s
  ✅ MODEL_EVALUATION_2: 6.89s (Score: 92%)
  ✅ TERRAFORM_EXECUTION: 1.23s
  ✅ INFRASTRUCTURE_DEPLOYMENT: 0.85s

💾 Results saved to: orchestration_results.json
🎉 Orchestration process completed successfully!
```

## 🔍 Project Structure

```
aws-terraform-1/
├── src/
│   ├── agents/
│   │   ├── base_agent.py         # Base agent class
│   │   ├── gemini_agent.py       # Gemini vision agent
│   │   ├── gpt4o_agent.py        # GPT-4o evaluation agent
│   │   └── claude_agent.py       # Claude Terraform agent
│   └── orchestration/
│       └── orchestrator.py       # Main orchestration logic
├── examples/
│   └── sample_diagrams/          # Sample architecture diagrams
├── main.py                       # Main entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

## 🔄 Process Flow

1. **Image Parsing**: Gemini analyzes the architecture diagram
2. **Quality Gate 1**: GPT-4o evaluates parsing quality (≥80% required)
3. **Code Generation**: Claude generates Terraform code
4. **Quality Gate 2**: GPT-4o validates Terraform code (≥80% required)
5. **Execution**: MCP pattern executes Terraform
6. **Deployment**: Infrastructure deployed to AWS

## 🛠️ Extending the System

### Adding New Agents

```python
from src.agents.base_agent import BaseAgent, AgentResponse

class CustomAgent(BaseAgent):
    async def initialize(self):
        # Initialize your agent
        pass
    
    async def process(self, input_data, context=None) -> AgentResponse:
        # Implement your processing logic
        return AgentResponse(content="result", success=True)
```

### Custom Evaluation Criteria

Modify the evaluation prompts in `gpt4o_agent.py` to add custom scoring criteria:

```python
# Add new evaluation criteria
evaluation_criteria = {
    "completeness": 20,
    "accuracy": 20,
    "security": 20,
    "performance": 20,
    "maintainability": 20
}
```

## ⚠️ Error Handling

The system includes comprehensive error handling:

- **Retry Logic**: Automatic retry with exponential backoff
- **Threshold Checks**: Process stops if evaluation scores fall below 80%
- **Graceful Degradation**: Detailed error reporting and partial results
- **Timeout Management**: Configurable timeouts for long-running operations

## 📈 Performance Optimization

- **Async Processing**: All agent calls are asynchronous
- **Parallel Execution**: Where possible, operations run in parallel
- **Connection Pooling**: Efficient API client management
- **Memory Management**: Optimized for large diagram processing

## 🔐 Security Considerations

- **API Key Management**: Environment-based configuration
- **Input Validation**: Comprehensive input sanitization
- **Error Sanitization**: No sensitive data in error messages
- **Secure Defaults**: Conservative timeout and retry settings

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_agents.py
pytest tests/test_orchestration.py
```

## 📝 Logging

The system provides detailed logging at multiple levels:

- **INFO**: Process progress and milestones
- **WARNING**: Threshold failures and retries
- **ERROR**: Failures and exceptions
- **DEBUG**: Detailed execution traces (when enabled)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋 Support

For questions, issues, or contributions, please:

1. Check the existing issues
2. Create a new issue with detailed description
3. Include logs and configuration (without API keys)

---

**Note**: This system is designed for production use with appropriate error handling, logging, and monitoring. Ensure you have proper AWS credentials and permissions for infrastructure deployment.

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Clear logs
rm -rf logs/* 2>/dev/null

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# One command to test everything
source .venv/bin/activate && \
pip install -r requirements.txt && \
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
keys_ok = all([os.getenv('OPENAI_API_KEY'), os.getenv('ANTHROPIC_API_KEY'), os.getenv('GOOGLE_API_KEY')])
print('✅ Environment ready!' if keys_ok else '❌ Please set API keys in .env file')
" && \
pytest tests/test_orchestration.py::TestMultiAgentOrchestrator::test_initialization -v && \
echo "🚀 System ready! Run: python main.py"
