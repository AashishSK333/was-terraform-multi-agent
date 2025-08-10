"""
Claude agent for Terraform code generation (Step 3)
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
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

    def _get_generation_prompt(self, parsed_json: str) -> str:
        """Creates the prompt for the Claude model to generate Terraform code."""
        return f"""
You are an expert Terraform engineer. Your task is to generate a complete and well-structured set of Terraform configuration files based on a JSON description of cloud resources.

**Instructions:**
1.  Analyze the provided JSON which describes the required infrastructure.
2.  Create a full set of Terraform (.tf) files. Organize the resources logically into separate files (e.g., `providers.tf`, `variables.tf`, `network.tf`, `security.tf`, `storage.tf`, `compute.tf`, `main.tf`, `outputs.tf`).
3.  **Crucially, you MUST wrap the content of each file in an XML-style tag: `<file path="filename.tf">...</file>`.**
4.  Do not include any introductory text, explanations, or markdown formatting outside of the `<file>` tags. The entire output must consist only of one or more `<file>` blocks.
5.  Ensure the generated Terraform code is valid, follows best practices, and is ready for `terraform init` and `terraform apply`.
6.  Create variables in `variables.tf` for key parameters like region, CIDR blocks, and instance types to make the configuration reusable.
7.  Define sensible outputs in `outputs.tf` for important resource identifiers.

**JSON Input:**
```json
{parsed_json}
```

**Example Output Format:**
<file path="providers.tf">
terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region
}}
</file>
<file path="variables.tf">
variable "aws_region" {{
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}}
</file>
<file path="main.tf">
# Main resources go here
</file>

Begin generating the Terraform files now based on the provided JSON.
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

    def _write_terraform_files(self, terraform_files: Dict[str, str]) -> Dict[str, str]:
        """Write Terraform files to the output directory."""
        written_files = {}
        if not terraform_files:
            print("❌ Error: No files to write.")
            return written_files

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
