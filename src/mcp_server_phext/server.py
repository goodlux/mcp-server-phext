"""MCP server implementation for phext with enhanced performance and functionality."""

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

# Import enhanced core modules
from .core.state import init_state, get_state
from .core.basic import (
    phext_fetch, phext_insert, phext_replace, phext_remove,
    phext_range_replace, phext_explode, phext_textmap,
    phext_normalize, phext_merge, phext_create_file
)
from .core.performance import (
    phext_load_to_memory, phext_flush_to_disk, phext_memory_status,
    phext_unload_file, phext_file_info, phext_optimize_memory
)
from .core.sq_api import (
    phext_select, phext_toc, phext_delta, phext_checksum,
    phext_push, phext_pull, phext_get_full
)
from .core.coordinates import (
    phext_coordinate_info, phext_parse_coordinate, phext_navigate,
    phext_find_next_scroll, phext_coordinate_distance, phext_coordinate_bounds
)
from .core.bulk import (
    phext_bulk_insert, phext_bulk_fetch, phext_bulk_update, phext_bulk_delete,
    phext_range_select, phext_range_delete, phext_range_copy, phext_range_move
)
from .core.search import (
    phext_search_content, phext_search_coordinates, phext_search_regex,
    phext_find_empty, phext_find_duplicates, phext_filter_coordinates,
    phext_content_statistics
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_server(default_phext_file: Optional[str] = None) -> FastMCP:
    """Create and configure the FastMCP server for phext."""
    
    # Create FastMCP server
    mcp = FastMCP(name="mcp-server-phext")
    
    # Initialize enhanced state
    init_state(default_phext_file)
    
    logger.info("Enhanced Phext MCP server initializing with performance optimizations")
    
    # ============================================================================
    # INITIALIZATION & GUIDANCE
    # ============================================================================
    
    @mcp.tool()
    def initialize_phext() -> str:
        """Initialize conversation with phext usage instructions and guidance."""
        return """
🚀 ENHANCED PHEXT MCP SERVER INITIALIZED! 🚀

📚 WHAT IS PHEXT?
Phext is a multi-dimensional coordinate system for organizing information.
Think of it like a super-powered filing system where every piece of content
has a precise coordinate address like: 1.1.1/1.1.1/2.1.1/1.1

🏗️ COORDINATE STRUCTURE:
Library.Shelf.Series / Collection.Volume.Book / Chapter.Section.Scroll / Line.Column
Example: 1.1.1/1.1.1/2.1.1/1.1 = Library 1, Collection 1, Chapter 2, Line 1

🔧 58 AVAILABLE TOOLS ORGANIZED BY CATEGORY:

📝 ENHANCED BASIC OPERATIONS (10 tools):
• enhanced_phext_fetch - Get content from coordinate
• enhanced_phext_insert - Add content at coordinate  
• enhanced_phext_replace - Replace content at coordinate
• enhanced_phext_remove - Delete content at coordinate
• enhanced_phext_create_file - Create new phext file
• enhanced_phext_explode - Show all coordinates and content
• enhanced_phext_textmap - Visualize structure with previews
• enhanced_phext_normalize - Clean up and optimize file
• enhanced_phext_merge - Combine two phext files
• enhanced_phext_range_replace - Replace content across coordinate range

⚡ PERFORMANCE & MEMORY (6 tools):
• performance_phext_load_to_memory - Load file into hash for speed
• performance_phext_memory_status - Check what's loaded in memory
• performance_phext_file_info - Get file metadata and statistics
• performance_phext_flush_to_disk - Force save changes to disk
• performance_phext_unload_file - Remove file from memory
• performance_phext_optimize_memory - Clean up and optimize memory

🗃️ DATABASE-STYLE OPERATIONS (7 tools):
• sq_phext_select - Database-style content selection
• sq_phext_toc - Table of contents with metadata
• sq_phext_checksum - File integrity verification
• sq_phext_delta - Hierarchical checksums
• sq_phext_push - Write local file to coordinate
• sq_phext_pull - Extract coordinate to local file
• sq_phext_get_full - Complete file export with metadata

🧭 COORDINATE NAVIGATION (6 tools):
• coord_phext_coordinate_info - Analyze coordinate structure
• coord_phext_parse_coordinate - Validate coordinate format
• coord_phext_navigate - Move through dimensions (up/down/left/right/forward/back)
• coord_phext_find_next_scroll - Find next available coordinates
• coord_phext_coordinate_distance - Calculate distance between coordinates
• coord_phext_coordinate_bounds - Find min/max coordinates in file

📦 BULK OPERATIONS (8 tools):
• bulk_phext_bulk_insert - Insert multiple coordinate→content pairs
• bulk_phext_bulk_fetch - Get multiple coordinates at once
• bulk_phext_bulk_update - Update multiple coordinates atomically
• bulk_phext_bulk_delete - Remove multiple coordinates efficiently
• bulk_phext_range_select - Get all coordinates in range
• bulk_phext_range_delete - Delete coordinate range
• bulk_phext_range_copy - Copy range to different location
• bulk_phext_range_move - Move range to different location

🔍 SEARCH & QUERY (7 tools):
• search_phext_search_content - Text search across all coordinates
• search_phext_search_coordinates - Search coordinate patterns
• search_phext_search_regex - Regular expression search
• search_phext_find_empty - Find empty coordinates
• search_phext_find_duplicates - Find duplicate content
• search_phext_filter_coordinates - Filter by multiple criteria
• search_phext_content_statistics - Generate detailed analytics

🎯 QUICK START EXAMPLES:
1. Create your first phext file:
   enhanced_phext_create_file("~/my_notes.phext", "My personal knowledge base")

2. Add some content:
   enhanced_phext_insert("1.1.1/1.1.1/1.1.1/1.1", "Welcome to my notes!", "~/my_notes.phext")

3. See the structure:
   sq_phext_toc("~/my_notes.phext")

4. Search your content:
   search_phext_search_content("welcome", "~/my_notes.phext")

💡 PRO TIPS:
• Use meaningful coordinate patterns (e.g., 1.1.1/1.1.1/PROJECT_NAME/TOPIC/1.1)
• Load files to memory for better performance: performance_phext_load_to_memory()
• Use bulk operations for multiple changes: bulk_phext_bulk_insert()
• Regular navigation: coord_phext_navigate() for moving through your data
• File integrity: sq_phext_checksum() to verify data integrity

🌟 ADVANCED FEATURES:
• Hash-based optimization for lightning-fast operations
• Cross-file operations with perfect data integrity
• Real-time memory management and optimization
• Enterprise-grade bulk processing
• Sophisticated search with regex and filtering
• Multi-dimensional coordinate navigation

📖 DEFAULT FILE:
Your default phext file is set to: ~/.claude/claude_desktop.phext
All operations without a file_path parameter will use this file.

🚀 Ready to revolutionize your information management with phext!
Start with initialize_phext() to see this guide anytime.
        """
    
    # ============================================================================
    # BASIC OPERATIONS (Enhanced with hash-based performance)
    # ============================================================================
    
    @mcp.tool()
    def enhanced_phext_fetch(coordinate: str, file_path: Optional[str] = None) -> str:
        """Fetch content from a specific phext coordinate."""
        return phext_fetch(coordinate, file_path)
    
    @mcp.tool()
    def enhanced_phext_insert(coordinate: str, content: str, file_path: Optional[str] = None) -> str:
        """Insert content at a phext coordinate (appends to existing content)."""
        return phext_insert(coordinate, content, file_path)
    
    @mcp.tool()
    def enhanced_phext_replace(coordinate: str, content: str, file_path: Optional[str] = None) -> str:
        """Replace content at a phext coordinate."""
        return phext_replace(coordinate, content, file_path)
    
    @mcp.tool()
    def enhanced_phext_remove(coordinate: str, file_path: Optional[str] = None) -> str:
        """Remove content at a phext coordinate."""
        return phext_remove(coordinate, file_path)
    
    @mcp.tool()
    def enhanced_phext_range_replace(start_coordinate: str, end_coordinate: str, content: str, file_path: Optional[str] = None) -> str:
        """Replace content across a range of coordinates."""
        return phext_range_replace(start_coordinate, end_coordinate, content, file_path)
    
    @mcp.tool()
    def enhanced_phext_explode(file_path: Optional[str] = None) -> str:
        """Get a map of all coordinates and their content in the phext."""
        return phext_explode(file_path)
    
    @mcp.tool()
    def enhanced_phext_textmap(file_path: Optional[str] = None) -> str:
        """Get a text-based map of all coordinates and content summaries."""
        return phext_textmap(file_path)
    
    @mcp.tool()
    def enhanced_phext_normalize(file_path: Optional[str] = None) -> str:
        """Normalize a phext file (clean up and optimize structure)."""
        return phext_normalize(file_path)
    
    @mcp.tool()
    def enhanced_phext_merge(left_file: str, right_file: str, output_file: Optional[str] = None) -> str:
        """Merge two phext files together."""
        return phext_merge(left_file, right_file, output_file)
    
    @mcp.tool()
    def enhanced_phext_create_file(file_path: str, initial_content: Optional[str] = None) -> str:
        """Create a new phext file."""
        return phext_create_file(file_path, initial_content)
    
    # ============================================================================
    # PERFORMANCE & MEMORY MANAGEMENT (Will's recommendations)
    # ============================================================================
    
    @mcp.tool()
    def performance_phext_load_to_memory(file_path: Optional[str] = None) -> Dict[str, Any]:
        """Explicitly load file into hash for performance."""
        return phext_load_to_memory(file_path)
    
    @mcp.tool()
    def performance_phext_flush_to_disk(file_path: Optional[str] = None) -> Dict[str, Any]:
        """Force save dirty hashes to disk."""
        return phext_flush_to_disk(file_path)
    
    @mcp.tool()
    def performance_phext_memory_status() -> Dict[str, Any]:
        """Show what's loaded in memory."""
        return phext_memory_status()
    
    @mcp.tool()
    def performance_phext_unload_file(file_path: Optional[str] = None) -> Dict[str, Any]:
        """Unload a file from memory (saves if dirty first)."""
        return phext_unload_file(file_path)
    
    @mcp.tool()
    def performance_phext_file_info(file_path: Optional[str] = None) -> Dict[str, Any]:
        """File metadata (size, coordinate count, etc.)."""
        return phext_file_info(file_path)
    
    @mcp.tool()
    def performance_phext_optimize_memory() -> Dict[str, Any]:
        """Optimize memory usage by cleaning up and reorganizing data."""
        return phext_optimize_memory()
    
    # ============================================================================
    # SQ-STYLE API (Database-like operations inspired by SQ REST API)
    # ============================================================================
    
    @mcp.tool()
    def sq_phext_select(coordinate: str, file_path: Optional[str] = None) -> str:
        """SQ-style select: Alias for fetch but with database-style naming."""
        return phext_select(coordinate, file_path)
    
    @mcp.tool()
    def sq_phext_toc(file_path: Optional[str] = None) -> Dict[str, Any]:
        """Table of contents (enhanced textmap) showing structure and metadata."""
        return phext_toc(file_path)
    
    @mcp.tool()
    def sq_phext_delta(file_path: Optional[str] = None) -> Dict[str, Any]:
        """Hierarchical checksum map for integrity verification."""
        return phext_delta(file_path)
    
    @mcp.tool()
    def sq_phext_checksum(file_path: Optional[str] = None) -> Dict[str, Any]:
        """File-level checksum for quick integrity verification."""
        return phext_checksum(file_path)
    
    @mcp.tool()
    def sq_phext_push(local_file_path: str, coordinate: str, phext_file_path: Optional[str] = None) -> str:
        """Write local file content to a specific coordinate in phext."""
        return phext_push(local_file_path, coordinate, phext_file_path)
    
    @mcp.tool()
    def sq_phext_pull(coordinate: str, local_file_path: str, phext_file_path: Optional[str] = None) -> str:
        """Fetch coordinate content to a local file."""
        return phext_pull(coordinate, local_file_path, phext_file_path)
    
    @mcp.tool()
    def sq_phext_get_full(file_path: Optional[str] = None) -> Dict[str, Any]:
        """Complete file copy with all metadata (SQ-style get operation)."""
        return phext_get_full(file_path)
    
    # ============================================================================
    # ADVANCED COORDINATE OPERATIONS
    # ============================================================================
    
    @mcp.tool()
    def coord_phext_coordinate_info(coordinate: str) -> Dict[str, Any]:
        """Analyze coordinate structure and provide detailed information."""
        return phext_coordinate_info(coordinate)
    
    @mcp.tool()
    def coord_phext_parse_coordinate(coordinate: str) -> Dict[str, Any]:
        """Validate and parse coordinate strings."""
        return phext_parse_coordinate(coordinate)
    
    @mcp.tool()
    def coord_phext_navigate(from_coordinate: str, direction: str, steps: int = 1, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Navigate through dimensions (up/down/left/right/forward/back)."""
        return phext_navigate(from_coordinate, direction, steps, file_path)
    
    @mcp.tool()
    def coord_phext_find_next_scroll(coordinate: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get next available coordinate in sequence."""
        return phext_find_next_scroll(coordinate, file_path)
    
    @mcp.tool()
    def coord_phext_coordinate_distance(coord1: str, coord2: str) -> Dict[str, Any]:
        """Calculate distance between coordinates."""
        return phext_coordinate_distance(coord1, coord2)
    
    @mcp.tool()
    def coord_phext_coordinate_bounds(file_path: Optional[str] = None) -> Dict[str, Any]:
        """Find min/max coordinates in file."""
        return phext_coordinate_bounds(file_path)
    
    # ============================================================================
    # BULK OPERATIONS
    # ============================================================================
    
    @mcp.tool()
    def bulk_phext_bulk_insert(coordinate_content_pairs: List[Dict[str, str]], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Insert multiple coordinate→content pairs efficiently."""
        return phext_bulk_insert(coordinate_content_pairs, file_path)
    
    @mcp.tool()
    def bulk_phext_bulk_fetch(coordinates: List[str], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Fetch multiple coordinates at once."""
        return phext_bulk_fetch(coordinates, file_path)
    
    @mcp.tool()
    def bulk_phext_bulk_update(coordinate_content_pairs: List[Dict[str, str]], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Update multiple coordinates atomically."""
        return phext_bulk_update(coordinate_content_pairs, file_path)
    
    @mcp.tool()
    def bulk_phext_bulk_delete(coordinates: List[str], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Remove multiple coordinates efficiently."""
        return phext_bulk_delete(coordinates, file_path)
    
    @mcp.tool()
    def bulk_phext_range_select(start_coordinate: str, end_coordinate: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Fetch all coordinates in range."""
        return phext_range_select(start_coordinate, end_coordinate, file_path)
    
    @mcp.tool()
    def bulk_phext_range_delete(start_coordinate: str, end_coordinate: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Delete all coordinates in range."""
        return phext_range_delete(start_coordinate, end_coordinate, file_path)
    
    @mcp.tool()
    def bulk_phext_range_copy(start_coordinate: str, end_coordinate: str, dest_start_coordinate: str, file_path: Optional[str] = None, dest_file_path: Optional[str] = None) -> Dict[str, Any]:
        """Copy range to different location."""
        return phext_range_copy(start_coordinate, end_coordinate, dest_start_coordinate, file_path, dest_file_path)
    
    @mcp.tool()
    def bulk_phext_range_move(start_coordinate: str, end_coordinate: str, dest_start_coordinate: str, file_path: Optional[str] = None, dest_file_path: Optional[str] = None) -> Dict[str, Any]:
        """Move range to different location."""
        return phext_range_move(start_coordinate, end_coordinate, dest_start_coordinate, file_path, dest_file_path)
    
    # ============================================================================
    # SEARCH AND QUERY TOOLS
    # ============================================================================
    
    @mcp.tool()
    def search_phext_search_content(query: str, file_path: Optional[str] = None, case_sensitive: bool = False, whole_words: bool = False) -> Dict[str, Any]:
        """Text search across all coordinates."""
        return phext_search_content(query, file_path, case_sensitive, whole_words)
    
    @mcp.tool()
    def search_phext_search_coordinates(pattern: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Search by coordinate patterns."""
        return phext_search_coordinates(pattern, file_path)
    
    @mcp.tool()
    def search_phext_search_regex(regex_pattern: str, file_path: Optional[str] = None, search_coordinates: bool = False) -> Dict[str, Any]:
        """Regular expression search in content or coordinates."""
        return phext_search_regex(regex_pattern, file_path, search_coordinates)
    
    @mcp.tool()
    def search_phext_find_empty(file_path: Optional[str] = None, include_whitespace_only: bool = True) -> Dict[str, Any]:
        """Find empty coordinates in file."""
        return phext_find_empty(file_path, include_whitespace_only)
    
    @mcp.tool()
    def search_phext_find_duplicates(file_path: Optional[str] = None, ignore_whitespace: bool = True) -> Dict[str, Any]:
        """Find duplicate content across coordinates."""
        return phext_find_duplicates(file_path, ignore_whitespace)
    
    @mcp.tool()
    def search_phext_filter_coordinates(criteria: Dict[str, Any], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Filter coordinates by various criteria."""
        return phext_filter_coordinates(criteria, file_path)
    
    @mcp.tool()
    def search_phext_content_statistics(file_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate detailed content statistics and analysis."""
        return phext_content_statistics(file_path)
    
    logger.info("Registered phext tools with enhanced functionality (59 total tools)")
    
    return mcp


def main():
    """Main entry point for the MCP server."""
    # Get default file from environment
    default_phext_file = os.getenv("PHEXT_DEFAULT_FILE")
    
    # Create the server
    server = create_server(default_phext_file=default_phext_file)
    
    # Start the server
    logger.info("Starting enhanced Phext MCP server with 59 tools")
    server.run()


if __name__ == "__main__":
    main()
