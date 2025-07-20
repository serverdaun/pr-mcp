# PR-MCP

A Model Context Protocol (MCP) server that helps with pull request management and template generation. Integrates with hosts to analyze git changes and suggest appropriate PR templates.

## Features

- **Git Change Analysis**: Analyze file changes, diffs, and commit history
- **PR Template Management**: Pre-built templates for different types of changes
- **Smart Template Suggestions**: AI-powered template recommendations based on change analysis
- **Multiple Change Types**: Support for bug fixes, features, documentation, refactoring, testing, performance, and security changes

## Installation

### For Host (Claude Code, Cursor, ...)

1. Clone the repository:
```bash
git clone https://github.com/serverdaun/pr-mcp.git
cd pr-mcp
```

2. Install dependencies:
```bash
uv sync
```

3. Add to your configuration (replace `/path/to/pr-mcp` with the absolute path to the cloned repository):
```json
{
  "mcpServers": {
    "pr-agent": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/pr-mcp/src",
        "run",
        "server.py"
        ]
    }
  }
}
```

## Usage

Once installed, you can use the following tools:

### `analyze_file_changes`
Analyze git changes in your repository:
- Compare against a base branch (default: main)
- Get file statistics and commit history
- View full diffs with configurable line limits

### `get_pr_templates`
List all available PR templates with their content.

### `suggest_template`
Get AI-powered template suggestions based on your change analysis.

## Available Templates

- **Bug Fix**: For bug fixes and patches
- **Feature**: For new features and enhancements
- **Documentation**: For documentation updates
- **Refactor**: For code refactoring and cleanup
- **Test**: For test additions and improvements
- **Performance**: For performance optimizations
- **Security**: For security-related changes


### Project Structure

```
pr-mcp/
├── src/
│   ├── server.py          # Main MCP server
│   └── templates/         # PR template files
├── tests/
│   └── test_server.py     # Test suite
└── pyproject.toml         # Project configuration
```

## License

MIT License
