<!-- Use this file to provide workspace-specific custom instructions to Copilot -->

## Project: Orchestrated Multi-Agent System for Architecture Diagram to Terraform

This project implements an orchestrated multi-agent system that processes architecture diagrams and generates Terraform code using multiple LLMs (Gemini, GPT-4o, Claude) with scoring thresholds.

### Project Status:
- ✅ Multi-agent system with Gemini, GPT-4o, and Claude agents
- ✅ 4-step automated orchestration process with threshold checks  
- ✅ Manual steps 5-6 for Terraform execution and deployment
- ✅ Comprehensive configuration management
- ✅ Logging and utility modules
- ✅ Complete test suite
- ✅ Example usage scripts and documentation

### Architecture:
- **Step 1**: Image Parsing (Gemini)
- **Step 2**: Quality Evaluation (GPT-4o) - 80% threshold
- **Step 3**: Terraform Generation (Claude) 
- **Step 4**: Code Evaluation (GPT-4o) - 80% threshold
- **Step 5**: Manual Terraform Execution
- **Step 6**: Manual AWS Deployment

### Key Files:
- `main.py` - Main entry point
- `src/orchestration/orchestrator.py` - Core orchestration logic
- `src/agents/` - Individual agent implementations
- `tests/` - Comprehensive test suite
