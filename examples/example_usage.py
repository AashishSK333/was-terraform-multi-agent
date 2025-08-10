"""
Example script demonstrating the multi-agent orchestration system
"""

import asyncio
from pathlib import Path
from src.orchestration.orchestrator import MultiAgentOrchestrator, load_config_from_env


async def example_basic_usage():
    """Basic usage example for 4-step automated process"""
    print("🔹 Basic Usage Example (Steps 1-4)")
    print("-" * 50)
    
    # Load configuration
    config = load_config_from_env()
    
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator(config)
    await orchestrator.initialize_agents()
    
    # Example with a sample image
    image_path = "examples/sample_diagrams/AWS_ServerlessD15.jpg"
    
    if not Path(image_path).exists():
        print(f"⚠️  Sample image not found: {image_path}")
        return
    
    print(f"Processing image: {image_path}")
    
    # Execute automated process (Steps 1-4)
    results = await orchestrator.execute_full_process(image_path)
    
    # Display results
    summary = orchestrator.get_process_summary()
    print(f"Completed {summary['successful_steps']}/{summary['total_automated_steps']} automated steps successfully")
    
    if summary['ready_for_manual_execution']:
        print("✅ Ready for manual steps 5-6")
        manual_instructions = orchestrator.get_manual_instructions()
        print("Manual steps:")
        for step_key, step_info in manual_instructions["next_manual_steps"].items():
            print(f"  {step_info['name']}: {step_info['description']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(example_basic_usage())
