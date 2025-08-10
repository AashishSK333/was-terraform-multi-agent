"""
Main entry point for the multi-agent orchestration system
"""

import asyncio
import sys
from pathlib import Path
from typing import List

from src.orchestration.orchestrator import MultiAgentOrchestrator, load_config_from_env
from src.orchestration.orchestrator import StepResult


def get_image_path() -> str:
    """Get image path from command line arguments or use default"""
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        if not Path(image_path).exists():
            print(f"❌ Image not found at {image_path}")
            sys.exit(1)
        return image_path
    else:
        # Use default sample image
        default_path = "examples/sample_diagrams/AWS_ServerlessD15.jpg"
        if Path(default_path).exists():
            return default_path
        else:
            print("❌ No image path provided and default sample not found")
            print("Usage: python main.py <image_path>")
            print("Example: python main.py examples/sample_diagrams/AWS_ServerlessD15.jpg")
            sys.exit(1)


def print_results_summary(results: List[StepResult], orchestrator: MultiAgentOrchestrator):
    """Print a summary of the automated process results"""
    print("\n📊 Automated Process Summary:")
    print("-" * 50)
    
    for i, result in enumerate(results, 1):
        status = "✅" if result.response.success else "❌"
        step_name = result.step.name.replace("_", " ").title()
        
        if result.score is not None:
            threshold_status = "✅ PASSED" if result.passed_threshold else "❌ FAILED"
            print(f"Step {i}: {step_name} - {status} (Score: {result.score}% {threshold_status})")
        else:
            print(f"Step {i}: {step_name} - {status}")
        
        print(f"        Execution time: {result.execution_time:.2f}s")
    
    summary = orchestrator.get_process_summary()
    print(f"\nTotal Automated Steps: {summary['total_automated_steps']}/4")
    print(f"Successful Steps: {summary['successful_steps']}")
    print(f"Failed Steps: {summary['failed_steps']}")
    print(f"Total Execution Time: {summary['total_execution_time']:.2f}s")
    print(f"Ready for Manual Execution: {summary['ready_for_manual_execution']}")


def print_manual_instructions(manual_instructions: dict):
    """Print detailed manual instructions for steps 5 & 6"""
    print("\n" + "=" * 80)
    print("📋 MANUAL STEPS REQUIRED")
    print("=" * 80)
    print("✅ All automated steps completed successfully!")
    
    if "terraform_files_location" in manual_instructions:
        print(f"\n📂 Terraform files generated in: {manual_instructions['terraform_files_location']}")
    
    print("\n🔄 Next Manual Steps:")
    
    for step_key, step_info in manual_instructions["next_manual_steps"].items():
        print(f"\n🔸 {step_info['name']}")
        print(f"   📝 {step_info['description']}")
        print("   📋 Instructions:")
        for i, instruction in enumerate(step_info['instructions'], 1):
            print(f"      {i}. {instruction}")
        
        # Add specific details for each step
        if step_key == "step_5":
            print("   💡 Quick Start:")
            print("      cd output/terraform")
            print("      terraform init")
            print("      terraform plan")
            print("      terraform apply")
        elif step_key == "step_6":
            print("   💡 Validation Checklist:")
            print("      - AWS resources created successfully")
            print("      - All services are running")
            print("      - Security groups configured properly")
            print("      - Networking connectivity verified")


def print_failure_analysis(results: List[StepResult], orchestrator: MultiAgentOrchestrator):
    """Print analysis of failed steps."""
    failed_steps = [r for r in results if not r.response.success or (r.score is not None and not r.passed_threshold)]
    
    if not failed_steps:
        return

    print("\n" + "❌" * 20 + " FAILURE ANALYSIS " + "❌" * 20)
    
    for result in failed_steps:
        step_name = result.step.name.replace("_", " ").title()
        print(f"\n🔍 Failure in {step_name}:")
        
        if result.score is not None and not result.passed_threshold:
            print(f"   Reason: Quality threshold not met.")
            print(f"   Score: {result.score}% (Required: {orchestrator.config.evaluation_threshold}%)")
        elif not result.response.success:
            print(f"   Reason: Step execution failed.")
            print(f"   Error: {result.response.error_message}")
        
        print(f"   Execution time: {result.execution_time:.2f}s")
    
    print("\n💡 Recommendations:")
    print("   - For quality threshold failures, review the evaluation feedback in the detailed log.")
    print("   - For execution failures, check API keys, network connectivity, and input data.")
    print("   - Verify that all required environment variables are set in your .env file.")
    print("   - Check the detailed log file for LLM response analysis and insights.")


async def main():
    """Main execution function"""
    print("🚀 Multi-Agent Orchestration System for Architecture Diagram to Terraform")
    print("📋 Automated Steps: 1-4 | Manual Steps: 5-6")
    print("=" * 80)
    
    try:
        # Load configuration
        config = load_config_from_env()
        print("✅ Configuration loaded successfully")
        
        # Check API keys
        missing_keys = []
        if not config.openai_api_key:
            missing_keys.append("OpenAI")
        if not config.anthropic_api_key:
            missing_keys.append("Anthropic")
        if not config.google_api_key:
            missing_keys.append("Google")
        
        if missing_keys:
            print(f"❌ Missing API keys for: {', '.join(missing_keys)}")
            print("Please set the required API keys in your .env file")
            return 1
        
        print("🔑 All API keys loaded successfully")
        
        # Initialize orchestrator
        orchestrator = MultiAgentOrchestrator(config)
        print("🔧 Initializing agents...")
        await orchestrator.initialize_agents()
        print("✅ All agents initialized successfully")
        
        # Get image path
        image_path = get_image_path()
        print(f"📸 Input image: {image_path}")
        
        print(f"\n🔄 Starting automated orchestration process (Steps 1-4)")
        print("-" * 80)
        
        # Execute automated steps only
        results = await orchestrator.execute_full_process(image_path)
        
        # Display results
        print_results_summary(results, orchestrator)
        
        # Determine if the process completed successfully and is ready for manual steps
        process_summary = orchestrator.get_process_summary()
        is_ready_for_manual = process_summary.get("ready_for_manual_execution", False)

        if is_ready_for_manual:
            # Display manual instructions
            manual_instructions = orchestrator.get_manual_instructions()
            print_manual_instructions(manual_instructions)
            
            print("\n🎉 Automated orchestration process completed successfully!")
            print("🔄 Ready for manual execution of Terraform deployment")
            print("\n📋 ANALYSIS & INSIGHTS:")
            print("   - Review the detailed log file for complete LLM responses and analysis")
            print("   - Each step includes agent reasoning, key considerations, and performance metrics")
            print("   - Evaluation scores provide detailed breakdown of quality assessments")
            return 0
        else:
            # Display failure analysis
            print_failure_analysis(results, orchestrator)
            
            print("\n\n⚠️  Automated process halted due to issues.")
            print("   The process cannot proceed to the manual steps.")
            print("   Please review the failure analysis and detailed log for complete insights.")
            return 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)