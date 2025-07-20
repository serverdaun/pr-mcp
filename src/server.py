#!/usr/bin/env python3

import json
import os
import subprocess
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("pr-agent")

# PR template directory
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Default PR templates
DEFAULT_TEMPLATES = {
    "bug.md": "Bug Fix",
    "feature.md": "Feature",
    "docs.md": "Documentation",
    "refactor.md": "Refactor",
    "test.md": "Test",
    "performance.md": "Performance",
    "security.md": "Security",
}

# Type mapping for PR templates
TYPE_MAPPING = {
    "bug": "bug.md",
    "fix": "bug.md",
    "feature": "feature.md",
    "enhancement": "feature.md",
    "docs": "docs.md",
    "documentation": "docs.md",
    "refactor": "refactor.md",
    "cleanup": "refactor.md",
    "test": "test.md",
    "testing": "test.md",
    "performance": "performance.md",
    "optimization": "performance.md",
    "security": "security.md",
}


@mcp.tool()
async def analyze_file_changes(
    base_branch: str = "main",
    include_diff: bool = True,
    max_diff_lines: int = 500,
    working_directory: Optional[str] = None,
) -> str:
    """Get the full diff and list of changed files in the current git repository.

    Args:
        base_branch: Base branch to compare against (default: main)
        include_diff: Include the full diff content (default: true)
        max_diff_lines: Maximum number of lines to include in the diff (default: 500)
        working_directory: Directory to run git commands in (default: current directory)
    """
    try:
        # Try to get working directory from roots first
        if working_directory is None:
            try:
                context = mcp.get_context()
                roots_result = await context.session.list_roots()
                root = roots_result.roots[0]
                working_directory = root.uri.path
            except Exception:
                # Fall back to current directory
                pass

        # Use provided working directory or current directory
        cwd = working_directory if working_directory else os.getcwd()

        # Run git diff command
        diff_command = ["git", "diff", base_branch, "--", "."]
        diff_result = subprocess.run(
            diff_command, cwd=cwd, capture_output=True, text=True
        )

        # Get changed files
        changed_files = subprocess.run(
            ["git", "diff", "--name-status", base_branch],
            cwd=cwd,
            capture_output=True,
            text=True,
        )

        # Get commit messages
        commit_messages = subprocess.run(
            ["git", "log", "--oneline", base_branch],
            cwd=cwd,
            capture_output=True,
            text=True,
        )

        # Parse the diff output
        diff_output = diff_result.stdout
        diff_lines = diff_output.split("\n")

        # Truncate the diff output if it is too long
        truncated = False
        if len(diff_lines) > max_diff_lines:
            truncated_diff = "\n".join(diff_lines[:max_diff_lines])
            truncated_diff += f"\n\n... Output truncated due to length limit. Showing {max_diff_lines} lines of {len(diff_lines)} total lines."
            diff_output = truncated_diff
            truncated = True

        # Get summary statistics
        stats_result = subprocess.run(
            ["git", "diff", "--stat", base_branch],
            cwd=cwd,
            capture_output=True,
            text=True,
        )

        return json.dumps(
            {
                "base_branch": base_branch,
                "stats": stats_result.stdout,
                "total_lines": len(diff_lines),
                "commits": commit_messages.stdout,
                "diff": (
                    diff_output
                    if include_diff
                    else "Diff content not included. Use include_diff=True to include the diff."
                ),
                "truncated": truncated,
                "files_changed": changed_files.stdout,
            }
        )

    except Exception as e:
        return json.dumps({"error": str(e), "hint": "Check git diff --stat command"})


@mcp.tool()
async def get_pr_templates() -> str:
    """List available PR templates with their content."""
    try:
        templates = [
            {
                "filename": filename,
                "type": template_type,
                "content": (TEMPLATES_DIR / filename).read_text(),
            }
            for filename, template_type in DEFAULT_TEMPLATES.items()
        ]
        return json.dumps(templates, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "hint": "Check template directory"})


@mcp.tool()
async def suggest_template(changes_summary: str, change_type: str) -> str:
    """Let Claude analyze the changes and suggest the most appropriate PR template.

    Args:
        changes_summary: Your analysis of what the changes do
        change_type: The type of change you've identified (bug, feature, docs, refactor, test, etc.)
    """
    try:
        templates_response = await get_pr_templates()
        templates = json.loads(templates_response)

        template_file = TYPE_MAPPING.get(change_type.lower(), "feature.md")
        selected_template = next(
            (t for t in templates if t["filename"] == template_file),
            templates[0],  # Default to first template if no match
        )

        suggestion = {
            "recommended_template": selected_template,
            "reasoning": f"Based on your analysis: '{changes_summary}', this appears to be a {change_type} change.",
            "template_content": selected_template["content"],
            "usage_hint": "Claude can help you fill out this template based on the specific changes in your PR.",
        }

        return json.dumps(suggestion, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e), "hint": "Check template mapping"})


if __name__ == "__main__":
    mcp.run()
