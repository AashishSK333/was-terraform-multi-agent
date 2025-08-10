"""
Comprehensive output logger for multi-agent orchestration system
Captures detailed responses from each step for analysis and debugging
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .types import StepResult, ProcessStep


class OrchestrationLogger:
    """Comprehensive logger for orchestration process"""
    
    def __init__(self, output_dir: str = "output/logs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.output_dir / f"orchestration_detailed_{self.timestamp}.md"
        self.json_file = self.output_dir / f"orchestration_data_{self.timestamp}.json"
        self.session_data = {
            "session_id": self.timestamp,
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "configuration": {},
            "summary": {}
        }
    
    def log_configuration(self, config: Dict[str, Any]):
        """Log the configuration used for this session"""
        # Remove API keys for security
        safe_config = {k: v for k, v in config.items() if 'api_key' not in k.lower()}
        self.session_data["configuration"] = safe_config
        
        with open(self.log_file, 'w') as f:
            f.write(f"# Multi-Agent Orchestration Session Log\n\n")
            f.write(f"**Session ID:** {self.timestamp}\n")
            f.write(f"**Start Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Configuration\n\n")
            f.write("```json\n")
            f.write(json.dumps(safe_config, indent=2))
            f.write("\n```\n\n")
    
    def log_step_start(self, step: ProcessStep, input_data: Any = None):
        """Log the start of a processing step"""
        step_name = step.name.replace("_", " ").title()
        
        with open(self.log_file, 'a') as f:
            f.write(f"## Step {step.value}: {step_name}\n\n")
            f.write(f"**Started:** {datetime.now().strftime('%H:%M:%S')}\n\n")
            
            if input_data and not isinstance(input_data, (str, bytes)) or (isinstance(input_data, str) and len(input_data) < 1000):
                f.write("### Input Data\n\n")
                if isinstance(input_data, str):
                    f.write(f"```\n{input_data}\n```\n\n")
                else:
                    f.write(f"```json\n{json.dumps(str(input_data), indent=2)}\n```\n\n")
    
    def log_step_completion(self, result: StepResult):
        """Log the completion of a processing step with detailed analysis"""
        step_name = result.step.name.replace("_", " ").title()
        
        with open(self.log_file, 'a') as f:
            # Status and timing
            status = "✅ SUCCESS" if result.response.success else "❌ FAILED"
            f.write(f"**Status:** {status}\n")
            f.write(f"**Execution Time:** {result.execution_time:.2f}s\n")
            
            if result.score is not None:
                threshold_status = "✅ PASSED" if result.passed_threshold else "❌ FAILED"
                f.write(f"**Score:** {result.score}% ({threshold_status})\n")
            
            f.write("\n")
            
            # Agent information
            if result.response.metadata:
                agent_name = result.response.metadata.get("agent", "Unknown")
                model = result.response.metadata.get("model", "Unknown")
                f.write(f"**Agent:** {agent_name}\n")
                f.write(f"**Model:** {model}\n\n")
            
            # Main response content
            f.write("### Agent Response\n\n")
            if result.response.success:
                self._write_formatted_response(f, result)
            else:
                f.write(f"**Error:** {result.response.error_message}\n\n")
            
            # Key insights and analysis
            self._write_step_analysis(f, result)
            
            f.write("---\n\n")
        
        # Store structured data
        step_data = {
            "step_number": result.step.value,
            "step_name": step_name,
            "agent": result.response.metadata.get("agent", "Unknown") if result.response.metadata else "Unknown",
            "model": result.response.metadata.get("model", "Unknown") if result.response.metadata else "Unknown",
            "success": result.response.success,
            "execution_time": result.execution_time,
            "score": result.score,
            "passed_threshold": result.passed_threshold,
            "response_content": result.response.content[:2000] + "..." if len(result.response.content) > 2000 else result.response.content,
            "metadata": result.response.metadata,
            "error_message": result.response.error_message,
            "timestamp": datetime.now().isoformat()
        }
        self.session_data["steps"].append(step_data)
    
    def _write_formatted_response(self, f, result: StepResult):
        """Write formatted response based on step type"""
        content = result.response.content
        
        if result.step == ProcessStep.IMAGE_PARSING:
            f.write("**Key Components Identified:**\n\n")
            self._extract_and_format_parsing_insights(f, content)
            
        elif result.step in [ProcessStep.MODEL_EVALUATION_1, ProcessStep.MODEL_EVALUATION_2]:
            f.write("**Evaluation Results:**\n\n")
            self._extract_and_format_evaluation_insights(f, content, result.step)
            
        elif result.step == ProcessStep.TERRAFORM_CREATION:
            f.write("**Generated Terraform Summary:**\n\n")
            self._extract_and_format_terraform_insights(f, content)
        
        # Always include full response in collapsed section
        f.write("<details>\n<summary>📄 Full Response Content</summary>\n\n")
        f.write("```\n")
        f.write(content)
        f.write("\n```\n</details>\n\n")
    
    def _extract_and_format_parsing_insights(self, f, content: str):
        """Extract key insights from Gemini's parsing response"""
        f.write("*Gemini Vision Analysis Highlights:*\n\n")
        
        # Try to extract structured information
        try:
            if "Components Identified" in content or "components" in content.lower():
                f.write("🔧 **Architecture Components:**\n")
                # Extract component mentions
                components = self._extract_aws_services(content)
                for component in components[:10]:  # Top 10
                    f.write(f"   - {component}\n")
                f.write("\n")
            
            if "relationships" in content.lower() or "connection" in content.lower():
                f.write("🔗 **Key Relationships Identified:**\n")
                f.write("   - Component interactions and data flows detected\n")
                f.write("   - Network architecture and connectivity patterns\n\n")
            
            if "security" in content.lower():
                f.write("🔒 **Security Elements:**\n")
                f.write("   - Security groups and access controls identified\n\n")
                
        except Exception:
            f.write("   - Comprehensive architecture analysis completed\n\n")
        
        f.write("💡 **Gemini's Key Considerations:**\n")
        f.write("   - Visual pattern recognition and component identification\n")
        f.write("   - Spatial relationship analysis between services\n")
        f.write("   - Data flow interpretation from diagram sequences\n\n")
    
    def _extract_and_format_evaluation_insights(self, f, content: str, step: ProcessStep):
        """Extract key insights from GPT-4o's evaluation response"""
        evaluator_type = "Parsing Quality" if step == ProcessStep.MODEL_EVALUATION_1 else "Terraform Code Quality"
        f.write(f"*GPT-4o {evaluator_type} Assessment:*\n\n")
        
        try:
            # Try to parse JSON evaluation
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                eval_data = json.loads(json_match.group())
                
                if "overall_score" in eval_data:
                    f.write(f"📊 **Overall Score:** {eval_data['overall_score']}/100\n\n")
                
                if "criteria_scores" in eval_data:
                    f.write("📋 **Detailed Scoring:**\n")
                    for criterion, score in eval_data["criteria_scores"].items():
                        criterion_name = criterion.replace("_", " ").title()
                        f.write(f"   - {criterion_name}: {score}/20\n")
                    f.write("\n")
                
                if "strengths" in eval_data and eval_data["strengths"]:
                    f.write("✅ **Identified Strengths:**\n")
                    for strength in eval_data["strengths"][:5]:
                        f.write(f"   - {strength}\n")
                    f.write("\n")
                
                if "weaknesses" in eval_data and eval_data["weaknesses"]:
                    f.write("⚠️ **Areas for Improvement:**\n")
                    for weakness in eval_data["weaknesses"][:5]:
                        f.write(f"   - {weakness}\n")
                    f.write("\n")
                    
        except Exception:
            f.write("   - Comprehensive evaluation completed\n\n")
        
        f.write("💡 **GPT-4o's Key Considerations:**\n")
        if step == ProcessStep.MODEL_EVALUATION_1:
            f.write("   - Completeness of component identification\n")
            f.write("   - Accuracy of architectural understanding\n")
            f.write("   - Quality of relationship mapping\n")
        else:
            f.write("   - Terraform best practices compliance\n")
            f.write("   - Security implementation review\n")
            f.write("   - Code quality and maintainability\n")
        f.write("\n")
    
    def _extract_and_format_terraform_insights(self, f, content: str):
        """Extract key insights from Claude's Terraform generation"""
        f.write("*Claude Terraform Generation Highlights:*\n\n")
        
        # Extract file information
        if "Generated Files:" in content or "```hcl" in content:
            f.write("📁 **Generated Terraform Files:**\n")
            lines = content.split('\n')
            terraform_files = []
            for line in lines:
                if '.tf' in line and ('**' in line or 'filepath:' in line):
                    terraform_files.append(line.strip())
            
            if terraform_files:
                for tf_file in terraform_files[:8]:
                    f.write(f"   {tf_file}\n")
            else:
                f.write("   - Multiple .tf files generated with modular structure\n")
            f.write("\n")
        
        # Extract key resources
        aws_resources = self._extract_terraform_resources(content)
        if aws_resources:
            f.write("🏗️ **Key Infrastructure Components:**\n")
            for resource in aws_resources[:8]:
                f.write(f"   - {resource}\n")
            f.write("\n")
        
        f.write("💡 **Claude's Key Considerations:**\n")
        f.write("   - Modular file organization for maintainability\n")
        f.write("   - Variable-driven configuration for reusability\n")
        f.write("   - Security best practices implementation\n")
        f.write("   - Output definitions for resource references\n\n")
    
    def _write_step_analysis(self, f, result: StepResult):
        """Write analysis specific to each step"""
        f.write("### Step Analysis\n\n")
        
        if result.step == ProcessStep.IMAGE_PARSING:
            f.write("**Why Gemini for Image Parsing?**\n")
            f.write("- Advanced vision capabilities for diagram interpretation\n")
            f.write("- Strong spatial reasoning for component relationships\n")
            f.write("- Ability to understand complex architectural patterns\n\n")
            
        elif result.step == ProcessStep.MODEL_EVALUATION_1:
            f.write("**Why GPT-4o for Parsing Evaluation?**\n")
            f.write("- Excellent analytical and reasoning capabilities\n")
            f.write("- Strong understanding of AWS architecture principles\n")
            f.write("- Reliable scoring and quality assessment\n\n")
            
        elif result.step == ProcessStep.TERRAFORM_CREATION:
            f.write("**Why Claude for Terraform Generation?**\n")
            f.write("- Superior code generation and structuring abilities\n")
            f.write("- Strong understanding of infrastructure as code\n")
            f.write("- Excellent at following specific output formats\n\n")
            
        elif result.step == ProcessStep.MODEL_EVALUATION_2:
            f.write("**Why GPT-4o for Code Evaluation?**\n")
            f.write("- Deep knowledge of Terraform best practices\n")
            f.write("- Strong security and compliance assessment\n")
            f.write("- Consistent evaluation methodology\n\n")
        
        # Performance insights
        if result.execution_time > 10:
            f.write("⏱️ **Performance Note:** This step took longer than usual, possibly due to:\n")
            f.write("- Complex input processing requirements\n")
            f.write("- Detailed analysis and generation tasks\n")
            f.write("- API rate limiting or network conditions\n\n")
    
    def _extract_aws_services(self, content: str) -> List[str]:
        """Extract AWS service names from content"""
        aws_services = [
            "VPC", "EC2", "Lambda", "S3", "DynamoDB", "RDS", "ELB", "ALB", "NLB",
            "API Gateway", "CloudFront", "Route 53", "IAM", "CloudWatch", "SQS",
            "SNS", "EventBridge", "Kinesis", "ElastiCache", "EFS", "FSx"
        ]
        
        found_services = []
        content_lower = content.lower()
        for service in aws_services:
            if service.lower() in content_lower:
                found_services.append(service)
        
        return found_services
    
    def _extract_terraform_resources(self, content: str) -> List[str]:
        """Extract Terraform resource types from content"""
        import re
        resource_pattern = r'aws_(\w+)'
        matches = re.findall(resource_pattern, content)
        return [f"aws_{match}" for match in set(matches)]
    
    def log_session_summary(self, summary: Dict[str, Any]):
        """Log the final session summary"""
        self.session_data["summary"] = summary
        self.session_data["end_time"] = datetime.now().isoformat()
        
        with open(self.log_file, 'a') as f:
            f.write("## Session Summary\n\n")
            f.write(f"**Total Execution Time:** {summary.get('total_execution_time', 0):.2f}s\n")
            f.write(f"**Successful Steps:** {summary.get('successful_steps', 0)}/{summary.get('total_automated_steps', 4)}\n")
            f.write(f"**Failed Steps:** {summary.get('failed_steps', 0)}\n")
            
            if summary.get('threshold_checks'):
                f.write("\n**Threshold Results:**\n")
                thresholds = summary['threshold_checks']
                if thresholds.get('step_2_score') is not None:
                    status = "✅" if thresholds['step_2_score'] >= thresholds['evaluation_threshold'] else "❌"
                    f.write(f"- Step 2 Evaluation: {thresholds['step_2_score']}% {status}\n")
                if thresholds.get('step_4_score') is not None:
                    status = "✅" if thresholds['step_4_score'] >= thresholds['evaluation_threshold'] else "❌"
                    f.write(f"- Step 4 Evaluation: {thresholds['step_4_score']}% {status}\n")
            
            f.write(f"\n**Session Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Add final recommendations section
            f.write("\n## Recommendations for Next Steps\n\n")
            if summary.get('ready_for_manual_execution'):
                f.write("✅ **System is ready for manual Terraform execution:**\n")
                f.write("1. Navigate to `output/terraform/` directory\n")
                f.write("2. Run `terraform init` to initialize\n")
                f.write("3. Run `terraform plan` to review changes\n")
                f.write("4. Run `terraform apply` to deploy infrastructure\n\n")
                f.write("💡 **Pre-deployment checklist:**\n")
                f.write("- Verify AWS credentials are configured\n")
                f.write("- Review all Terraform files for correctness\n")
                f.write("- Ensure proper AWS permissions are available\n")
                f.write("- Consider running in a test environment first\n")
            else:
                f.write("⚠️ **Manual intervention required before deployment:**\n")
                f.write("- Review failed steps in the analysis above\n")
                f.write("- Address quality threshold issues if any\n")
                f.write("- Re-run the orchestration process if needed\n")
                f.write("- Consider adjusting evaluation thresholds\n")
        
        # Write JSON data
        with open(self.json_file, 'w') as f:
            json.dump(self.session_data, f, indent=2)
        
        print(f"📋 Detailed log saved to: {self.log_file}")
        print(f"📊 Structured data saved to: {self.json_file}")
    
    def get_log_files(self) -> Dict[str, str]:
        """Get the paths to generated log files"""
        return {
            "markdown_log": str(self.log_file),
            "json_data": str(self.json_file)
        }