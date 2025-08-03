# MCP Server for Phext

An MCP (Model Context Protocol) server that provides access to [phext](https://pypi.org/project/libphext/) - a hyperdimensional text processing system.

> **NOTE**: We will be publishing this as a pip package soon. For now, please use the developer installation below.

## Developer Installation

For developers who want to try the latest features:

1. **Download the repository:**
   ```bash
   git clone https://github.com/your-org/mcp-server-phext.git
   cd mcp-server-phext
   ```

2. **Install uv (if you haven't already):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

4. **Add to Claude Desktop config:**
   ```json
   {
     "mcpServers": {
       "phext-dev": {
         "command": "uv",
         "args": [
           "run",
           "--directory",
           "{full path to your local mcp-server-phext repo}",
           "python",
           "-m",
           "mcp_server_phext"
         ],
         "env": {
           "PHEXT_DEFAULT_FILE": "~/.claude/claude_desktop.phext"
         }
       }
     }
   }
   ```
5. In the project knowledge of Claude desktop, you can add "Start all conversations with initialize_phext()" ... this will inform Claude how to use Phext, and can be customized to have Claude Desktop automatically save memories, milestones, or whatever he wants to remember about your interactions! Just tell him what you want to be saved, and he can update the initialize script automatically for you.

## What is Phext?

Phext is a hyperdimensional text coordinate system that allows you to organize and navigate text in three-dimensional space using coordinates like `1.1.1`, `2.3.4`, etc. It enables unique ways of structuring and accessing textual information.

## Installation

```bash
# Install with uv (recommended)
uv add mcp-server-phext

# Or with pip
pip install mcp-server-phext
```

## Usage

### With Claude Desktop

Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "phext": {
      "command": "uv",
      "args": ["run", "mcp-server-phext"],
      "env": {
        "PHEXT_DEFAULT_FILE": "~/.claude/claude_desktop.phext"
      }
    }
  }
}
```

### With Claude Code or other MCP clients

```bash
# Run the server directly
uv run mcp-server-phext

# Or with a specific default file
uv run mcp-server-phext --default-phext-file ~/my-phext-file.phext
```

## Features

The MCP server provides the following tools:

### Core Operations
- **phext_fetch**: Read content from a coordinate (e.g., `1.1.1/1.1.1/1.1.1`)
- **phext_insert**: Insert content at a coordinate (appends to existing)
- **phext_replace**: Replace content at a coordinate
- **phext_range_replace**: Replace content across a range of coordinates
- **phext_remove**: Remove content at a coordinate

### File Management
- **phext_create_file**: Create new phext files
- **phext_explode**: Get a map of all coordinates and content
- **phext_textmap**: Get a text summary of all coordinates
- **phext_normalize**: Clean up and optimize phext structure
- **phext_merge**: Merge two phext files together

### Resources
- Access to phext files as MCP resources
- Read raw phext file content

## Example Interactions

```
# Fetch content at coordinate
phext_fetch(coordinate="1.1.1/1.1.1/1.1.1")

# Insert content at a coordinate
phext_insert(coordinate="1.1.1/1.1.1/1.2.1", content="Hello, hyperdimensional world!")

# Replace content across a range
phext_range_replace(
    start_coordinate="1.1.1/1.1.1/1.1.1", 
    end_coordinate="1.1.1/1.1.1/1.1.5", 
    content="New content"
)

# Get a map of all content
phext_textmap()
```

## Configuration

### Environment Variables
- `PHEXT_DEFAULT_FILE`: Default phext file to use if none specified

### Command Line Arguments
- `--default-phext-file`: Specify default phext file

## Development

```bash
# Clone and setup
git clone <repository>
cd mcp-server-phext

# Install dependencies
uv sync

# Run in development
uv run mcp-server-phext
```

## License

MIT License
