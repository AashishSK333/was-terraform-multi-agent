"""
Claude agent for Terraform code generation (Step 3)
"""

import os
import re
import glob
from pathlib import Path
from typing import Dict, Any, Optional, List
from anthropic import AsyncAnthropic

from .base_agent import BaseAgent, AgentResponse


class ClaudeAgent(BaseAgent):
    """Claude agent specialized for Terraform code generation"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__("Claude Terraform Agent", model, api_key)
        self.output_dir = Path("output/terraform")

    async def initialize(self):
        """Initialize Anthropic client and output directory"""
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Clear existing .tf files before generation
        self._clear_existing_tf_files()

    def _clear_existing_tf_files(self):
        """Remove all existing .tf files from the output directory"""
        tf_files = glob.glob(str(self.output_dir / "*.tf"))
        if tf_files:
            print(f"🧹 Clearing {len(tf_files)} existing .tf files...")
            for tf_file in tf_files:
                try:
                    os.remove(tf_file)
                    print(f"  ✅ Removed: {os.path.basename(tf_file)}")
                except OSError as e:
                    print(f"  ❌ Failed to remove {os.path.basename(tf_file)}: {e}")
        else:
            print("📁 No existing .tf files found to clear")

    def _get_generation_prompt(self, parsed_json: str) -> str:
        """Creates the prompt for the Claude model to generate Terraform code."""
        return f"""
You are an expert Terraform engineer. Your task is to generate a complete and well-structured set of Terraform configuration files based on a JSON description of cloud resources.

**CRITICAL REQUIREMENTS:**

1. **NO DUPLICATE RESOURCES**: Ensure each AWS resource is defined exactly ONCE across all files. Do not create the same resource (same type + name) in multiple files.

2. **RESOURCE ORGANIZATION**: Organize resources logically into separate files based on AWS service categories:
   - `providers.tf`: Provider configuration and required_providers
   - `variables.tf`: Input variables for configuration flexibility
   - `network.tf`: VPC, subnets, routes, NAT/Internet gateways, VPC endpoints
   - `security.tf`: Security groups, NACLs, IAM roles, policies, and access controls
   - `storage.tf`: S3 buckets, DynamoDB tables, RDS, EFS, EBS volumes, backup vaults
   - `compute.tf`: EC2 instances, Auto Scaling groups, Launch templates, placement groups
   - `lambda.tf`: Lambda functions, layers, aliases, and related configurations
   - `containers.tf`: ECS/EKS clusters, Fargate services, ECR repositories
   - `databases.tf`: RDS instances, Aurora clusters, ElastiCache, DocumentDB
   - `messaging.tf`: SQS queues, SNS topics, EventBridge rules, Kinesis streams
   - `analytics.tf`: Data analytics services (Redshift, EMR, Glue, Athena)
   - `monitoring.tf`: CloudWatch resources, alarms, dashboards, X-Ray tracing
   - `main.tf`: Main resource orchestration, dependencies, and data sources
   - `outputs.tf`: Output values for resource references and endpoints

3. **DUPLICATE PREVENTION CHECKLIST**:
   - Before defining any resource, verify it doesn't exist in your planned files
   - Use consistent naming conventions: `<project>_<service>_<purpose>_<environment>`
   - Reference existing resources using Terraform interpolation (e.g., `aws_vpc.main.id`)
   - Consolidate resources that serve the same architectural purpose
   - Share common resources (VPCs, security groups) across related services

4. **XML FILE STRUCTURE**: 
   - **Crucially, you MUST wrap the content of each file in an XML-style tag: `<file path="filename.tf">...</file>`.**
   - Do not include any introductory text, explanations, or markdown formatting outside of the `<file>` tags.

5. **TERRAFORM BEST PRACTICES**:
   - Use meaningful resource names that reflect their architectural purpose
   - Add comprehensive tags to all resources (Environment, Project, Owner, CostCenter)
   - Include proper dependencies using `depends_on` when implicit dependencies aren't sufficient
   - Use variables for all configurable values (regions, instance types, CIDR blocks)
   - Include detailed descriptions for all variables and outputs
   - Implement proper resource lifecycle management where applicable
   - Use data sources for existing AWS resources when appropriate

6. **VALIDATION REQUIREMENTS**:
   - Ensure all resource references are valid and properly scoped
   - Verify security group rules reference existing or co-created security groups
   - Confirm subnet availability zone assignments are consistent
   - Validate IAM policy attachments reference existing roles/policies/users
   - Check that all required AWS service quotas are considered
   - Ensure cross-service integrations are properly configured

7. **ARCHITECTURE PATTERN DETECTION**:
   - Analyze the JSON input to identify the architecture pattern (web application, data pipeline, microservices, etc.)
   - Apply appropriate AWS Well-Architected Framework principles
   - Implement security best practices relevant to the detected pattern
   - Consider high availability and disaster recovery requirements
   - Include appropriate monitoring and logging for the architecture type

**JSON Input:**
```json
{parsed_json}
```

**Example Output Format:**
<file path="providers.tf">
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region
  
  default_tags {{
    tags = {{
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }}
  }}
}}
</file>

<file path="variables.tf">
variable "project_name" {{
  description = "The name of the project for resource naming and tagging."
  type        = string
  validation {{
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }}
}}

variable "environment" {{
  description = "The deployment environment (dev, staging, prod)."
  type        = string
  validation {{
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }}
}}

variable "aws_region" {{
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}}
</file>

**IMPORTANT**: Analyze the provided JSON to understand the specific architecture pattern and generate appropriate Terraform code. Do not make assumptions about the architecture type - base your implementation strictly on the provided resource descriptions. Ensure the generated code is production-ready, secure, and follows AWS best practices for the identified architecture pattern.

Begin generating the Terraform files now. Remember: NO DUPLICATE RESOURCES across files!
"""

    def _parse_terraform_files(self, response_content: str) -> Dict[str, str]:
        """
        Parses the model's response to extract file content based on <file> tags.
        """
        files = {}
        # Regex to find all occurrences of <file path="...">...</file>
        pattern = re.compile(r'<file path="(?P<filename>[^"]+)">\s*(?P<content>.*?)\s*</file>', re.DOTALL)

        matches = pattern.finditer(response_content)
        for match in matches:
            filename = match.group('filename').strip()
            content = match.group('content').strip()
            if filename and content:
                # Further clean up the content from potential markdown code blocks
                content = re.sub(r'^```[a-z]*\n', '', content, flags=re.MULTILINE)
                content = re.sub(r'\n```$', '', content, flags=re.MULTILINE)
                files[filename] = content.strip()

        if not files:
            print("⚠️  Warning: Could not find any <file> tags in the response. Attempting to treat the entire response as a single main.tf file.")
            # Fallback for when the model completely ignores instructions
            cleaned_content = response_content.strip()
            if cleaned_content:
                return {'main.tf': cleaned_content}

        return files

    def _validate_for_duplicates(self, terraform_files: Dict[str, str]) -> List[str]:
        """
        Validate terraform files for duplicate resource definitions
        Returns list of duplicate issues found
        """
        duplicate_issues = []
        all_resources = {}  # resource_type.resource_name -> file_name
        
        # Parse all resources from all files
        for filename, content in terraform_files.items():
            # Find all resource definitions using regex
            resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{'
            resources = re.findall(resource_pattern, content)
            
            for resource_type, resource_name in resources:
                resource_key = f"{resource_type}.{resource_name}"
                
                if resource_key in all_resources:
                    # Duplicate found
                    original_file = all_resources[resource_key]
                    duplicate_issues.append(
                        f"Duplicate resource '{resource_key}' found in {filename} "
                        f"(originally defined in {original_file})"
                    )
                else:
                    all_resources[resource_key] = filename
        
        # Check for potential logical duplicates (same resource type serving similar purpose)
        self._check_logical_duplicates(terraform_files, duplicate_issues)
        
        return duplicate_issues

    def _check_logical_duplicates(self, terraform_files: Dict[str, str], duplicate_issues: List[str]):
        """Check for logical duplicates - resources that serve the same purpose"""
        # Track resource types that should typically be unique
        unique_resource_types = {
            'aws_vpc': [],
            'aws_internet_gateway': [],
            'aws_nat_gateway': [],
        }
        
        for filename, content in terraform_files.items():
            for resource_type in unique_resource_types.keys():
                pattern = rf'resource\s+"{resource_type}"\s+"([^"]+)"'
                matches = re.findall(pattern, content)
                for resource_name in matches:
                    unique_resource_types[resource_type].append((resource_name, filename))
        
        # Check for multiple instances of resources that should be unique
        for resource_type, instances in unique_resource_types.items():
            if len(instances) > 1:
                instance_list = [f"{name} in {filename}" for name, filename in instances]
                duplicate_issues.append(
                    f"Multiple {resource_type} resources detected: {', '.join(instance_list)}. "
                    f"Consider if all are necessary or if they should be consolidated."
                )

    def _write_terraform_files(self, terraform_files: Dict[str, str]) -> Dict[str, str]:
        """Write Terraform files to the output directory after validation."""
        written_files = {}
        if not terraform_files:
            print("❌ Error: No files to write.")
            return written_files

        # Validate for duplicates before writing
        duplicate_issues = self._validate_for_duplicates(terraform_files)
        if duplicate_issues:
            print("⚠️  DUPLICATE RESOURCES DETECTED:")
            for issue in duplicate_issues:
                print(f"   🔄 {issue}")
            print("   📝 Files will still be written, but review and fix duplicates before applying.")

        print(f"📝 Attempting to write {len(terraform_files)} Terraform files...")
        for filename, content in terraform_files.items():
            if not content.strip():
                print(f"⚠️  Skipping empty file: {filename}")
                continue

            file_path = self.output_dir / filename
            try:
                file_path.write_text(content, encoding='utf-8')
                written_files[filename] = str(file_path)
                file_size = file_path.stat().st_size
                print(f"✅ Generated: {filename} ({file_size} bytes)")
            except IOError as e:
                print(f"❌ Failed to write {filename}: {e}")

        return written_files

    def _create_terraform_summary(self, written_files: Dict[str, str]) -> str:
        """Create a summary of the generated Terraform files."""
        if not written_files:
            return "Terraform code generation failed: No files were written."

        summary = "# Terraform Code Generation Summary\n\n## Generated Files:\n"
        for filename, filepath in written_files.items():
            file_size = Path(filepath).stat().st_size if Path(filepath).exists() else 0
            summary += f"- **{filename}**: `{filepath}` ({file_size} bytes)\n"

        summary += f"""
## Next Steps:

The generated Terraform files are located in the `{self.output_dir}` directory.

To deploy the infrastructure, navigate to the directory and run the following commands:

1.  **Initialize Terraform:**
    ```sh
    cd {self.output_dir}
    terraform init
    ```

2.  **Review the Plan:**
    ```sh
    terraform plan
    ```

3.  **Apply the Configuration:**
    ```sh
    terraform apply
    ```
"""
        return summary.strip()

    async def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Generates Terraform code from a JSON description and writes it to separate files.
        """
        try:
            # Clear existing files before generating new ones
            self._clear_existing_tf_files()
            
            prompt = self._get_generation_prompt(input_data)

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            raw_content = response.content[0].text
            print("🔍 Debug: Raw Claude response received.")

            terraform_files = self._parse_terraform_files(raw_content)

            if not terraform_files:
                raise Exception("Parsing failed. The model did not return content in the expected format, and no files could be extracted.")

            written_files = self._write_terraform_files(terraform_files)

            if not written_files:
                raise Exception("File writing failed. Although content was parsed, no files were successfully written to disk.")

            summary = self._create_terraform_summary(written_files)

            return AgentResponse(
                content=summary,
                confidence=0.95,
                metadata={
                    "agent": self.name,
                    "model": self.model,
                    "task": "terraform_generation",
                    "output_type": "terraform_code",
                    "generated_files": written_files,
                    "file_count": len(written_files)
                }
            )

        except Exception as e:
            print(f"❌ Claude Agent Error: {e}")
            return AgentResponse(
                content="",
                success=False,
                error_message=f"An error occurred in the Claude agent: {e}"
            )
