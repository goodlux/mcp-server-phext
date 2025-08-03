"""MCP server implementation for phext."""

import os
import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

try:
    from phext.phext import Phext
    from phext.coordinate import Coordinate
    from phext.range import Range
except ImportError as e:
    raise ImportError(
        "phext is required but not installed. "
        "Install it with: pip install phext"
    ) from e

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class PhextServerState:
    """Manages the state of phext files and operations."""
    
    def __init__(self, default_phext_file: Optional[str] = None):
        self.default_phext_file = default_phext_file
        self.phext_buffers: Dict[str, str] = {}
        self.phext = Phext()
    
    def get_file_path(self, file_path: Optional[str] = None) -> str:
        """Get the file path to use, defaulting to the configured default."""
        if file_path is None:
            file_path = self.default_phext_file
        
        if file_path is None:
            raise ValueError("No phext file specified and no default set")
        
        # Expand user path
        return os.path.expanduser(file_path)
    
    def load_file(self, file_path: str) -> str:
        """Load a phext file into memory, creating if it doesn't exist."""
        if file_path not in self.phext_buffers:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.phext_buffers[file_path] = f.read()
                else:
                    # Create new empty phext file
                    self.phext_buffers[file_path] = ""
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
            except Exception as e:
                raise RuntimeError(f"Error loading phext file {file_path}: {str(e)}")
        
        return self.phext_buffers[file_path]
    
    def save_file(self, file_path: str) -> None:
        """Save the phext buffer to disk."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.phext_buffers[file_path])
        except Exception as e:
            raise RuntimeError(f"Error saving phext file {file_path}: {str(e)}")


def create_server(default_phext_file: Optional[str] = None) -> FastMCP:
    """Create and configure the FastMCP server for phext."""
    
    # Create FastMCP server
    mcp = FastMCP(name="mcp-server-phext")
    
    # Initialize state
    state = PhextServerState(default_phext_file)
    
    logger.info("Phext MCP server initializing")
    
    # Register phext tools using FastMCP decorators
    @mcp.tool()
    def phext_fetch(coordinate: str, file_path: Optional[str] = None) -> str:
        """Fetch content from a specific phext coordinate."""
        try:
            coord = Coordinate.from_string(coordinate)
            actual_file_path = state.get_file_path(file_path)
            buffer = state.load_file(actual_file_path)
            content = state.phext.fetch(buffer, coord)
            return content or "(empty)"
        except Exception as e:
            raise RuntimeError(f"Error fetching phext coordinate: {str(e)}")
    
    @mcp.tool()
    def phext_insert(coordinate: str, content: str, file_path: Optional[str] = None) -> str:
        """Insert content at a phext coordinate (appends to existing content)."""
        try:
            coord = Coordinate.from_string(coordinate)
            actual_file_path = state.get_file_path(file_path)
            buffer = state.load_file(actual_file_path)
            new_buffer = state.phext.insert(buffer, coord, content)
            state.phext_buffers[actual_file_path] = new_buffer
            state.save_file(actual_file_path)
            return f"Successfully inserted content at {coordinate}"
        except Exception as e:
            raise RuntimeError(f"Error inserting to phext coordinate: {str(e)}")
    
    @mcp.tool()
    def phext_replace(coordinate: str, content: str, file_path: Optional[str] = None) -> str:
        """Replace content at a phext coordinate."""
        try:
            coord = Coordinate.from_string(coordinate)
            actual_file_path = state.get_file_path(file_path)
            buffer = state.load_file(actual_file_path)
            new_buffer = state.phext.replace(buffer, coord, content)
            state.phext_buffers[actual_file_path] = new_buffer
            state.save_file(actual_file_path)
            return f"Successfully replaced content at {coordinate}"
        except Exception as e:
            raise RuntimeError(f"Error replacing phext coordinate: {str(e)}")
    
    @mcp.tool()
    def phext_remove(coordinate: str, file_path: Optional[str] = None) -> str:
        """Remove content at a phext coordinate."""
        try:
            coord = Coordinate.from_string(coordinate)
            actual_file_path = state.get_file_path(file_path)
            buffer = state.load_file(actual_file_path)
            new_buffer = state.phext.remove(buffer, coord)
            state.phext_buffers[actual_file_path] = new_buffer
            state.save_file(actual_file_path)
            return f"Successfully removed content at {coordinate}"
        except Exception as e:
            raise RuntimeError(f"Error removing phext coordinate: {str(e)}")
    
    @mcp.tool()
    def phext_range_replace(start_coordinate: str, end_coordinate: str, content: str, file_path: Optional[str] = None) -> str:
        """Replace content across a range of coordinates."""
        try:
            start_coord = Coordinate.from_string(start_coordinate)
            end_coord = Coordinate.from_string(end_coordinate)
            range_obj = Range(start_coord, end_coord)
            actual_file_path = state.get_file_path(file_path)
            buffer = state.load_file(actual_file_path)
            new_buffer = state.phext.range_replace(buffer, range_obj, content)
            state.phext_buffers[actual_file_path] = new_buffer
            state.save_file(actual_file_path)
            return f"Successfully replaced range {start_coordinate} to {end_coordinate}"
        except Exception as e:
            raise RuntimeError(f"Error replacing phext range: {str(e)}")
    
    @mcp.tool()
    def phext_explode(file_path: Optional[str] = None) -> str:
        """Get a map of all coordinates and their content in the phext."""
        try:
            actual_file_path = state.get_file_path(file_path)
            buffer = state.load_file(actual_file_path)
            coord_map = state.phext.explode(buffer)
            
            result_text = f"Found {len(coord_map)} coordinates:\\n"
            for coord, content in coord_map.items():
                preview = content[:100] + "..." if len(content) > 100 else content
                result_text += f"  {coord}: {preview}\\n"
            
            return result_text
        except Exception as e:
            raise RuntimeError(f"Error exploding phext file: {str(e)}")
    
    @mcp.tool()
    def phext_textmap(file_path: Optional[str] = None) -> str:
        """Get a text-based map of all coordinates and content summaries."""
        try:
            actual_file_path = state.get_file_path(file_path)
            buffer = state.load_file(actual_file_path)
            textmap = state.phext.textmap(buffer)
            return textmap or "(empty phext)"
        except Exception as e:
            raise RuntimeError(f"Error creating phext textmap: {str(e)}")
    
    @mcp.tool()
    def phext_normalize(file_path: Optional[str] = None) -> str:
        """Normalize a phext file (clean up and optimize structure)."""
        try:
            actual_file_path = state.get_file_path(file_path)
            buffer = state.load_file(actual_file_path)
            normalized = state.phext.normalize(buffer)
            state.phext_buffers[actual_file_path] = normalized
            state.save_file(actual_file_path)
            return f"Successfully normalized phext file: {actual_file_path}"
        except Exception as e:
            raise RuntimeError(f"Error normalizing phext file: {str(e)}")
    
    @mcp.tool()
    def phext_merge(left_file: str, right_file: str, output_file: Optional[str] = None) -> str:
        """Merge two phext files together."""
        try:
            left_path = state.get_file_path(left_file)
            right_path = state.get_file_path(right_file)
            output_path = state.get_file_path(output_file or left_file)
            
            left_buffer = state.load_file(left_path)
            right_buffer = state.load_file(right_path)
            merged = state.phext.merge(left_buffer, right_buffer)
            state.phext_buffers[output_path] = merged
            state.save_file(output_path)
            
            return f"Successfully merged {left_path} and {right_path} into {output_path}"
        except Exception as e:
            raise RuntimeError(f"Error merging phext files: {str(e)}")
    
    @mcp.tool()
    def phext_create_file(file_path: str, initial_content: Optional[str] = None) -> str:
        """Create a new phext file."""
        try:
            actual_file_path = state.get_file_path(file_path)
            
            # Create new phext file
            if initial_content:
                # If initial content provided, insert it at the default coordinate
                default_coord = state.phext.defaultCoordinate()
                new_buffer = state.phext.insert("", default_coord, initial_content)
            else:
                new_buffer = ""
            
            state.phext_buffers[actual_file_path] = new_buffer
            state.save_file(actual_file_path)
            
            return f"Successfully created phext file: {actual_file_path}"
        except Exception as e:
            raise RuntimeError(f"Error creating phext file: {str(e)}")
    
    return mcp


def main():
    """Main entry point for the MCP server."""
    # Get default file from environment
    default_phext_file = os.getenv("PHEXT_DEFAULT_FILE")
    
    # Create the server
    server = create_server(default_phext_file=default_phext_file)
    
    # Start the server
    logger.info("Phext MCP server starting...")
    server.run()
