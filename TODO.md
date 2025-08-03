# MCP Server Phext Enhancement TODO

Based on feedback from Will (phext developer) and analysis of the SQ repository, this document outlines improvements and additions for the mcp-server-phext.

## Current Status ✅
- **Working MCP server** with FastMCP implementation
- **10 basic phext tools** implemented:
  - `phext_fetch`, `phext_insert`, `phext_replace`, `phext_remove`
  - `phext_range_replace`, `phext_explode`, `phext_textmap`
  - `phext_normalize`, `phext_merge`, `phext_create_file`
- **Claude Desktop integration** working
- **Local development setup** with uv

## High Priority Enhancements 🚀

### 1. Performance Optimizations (Will's Recommendation)
**Goal**: Use hash/dictionary interfaces for runtime performance instead of string serialization

#### Current vs Optimized Approach:
- **Current**: Load file → string buffer → phext operations → save file
- **Optimized**: Load file → explode to hash → operations on hash → implode → save file

#### Implementation:
```python
class PhextServerState:
    def __init__(self):
        self.phext_hashes: Dict[str, Dict[Coordinate, str]] = {}  # In-memory hash maps
        self.dirty_files: Set[str] = set()  # Track which files need saving
    
    def load_file_as_hash(self, file_path: str) -> Dict[Coordinate, str]:
        """Load file and explode to coordinate→content hash"""
        
    def save_hash_to_file(self, file_path: str, coord_hash: Dict[Coordinate, str]):
        """Implode hash and save to file"""
```

#### Tools to Add:
- `phext_load_to_memory` - Explicitly load file into hash for performance
- `phext_flush_to_disk` - Force save dirty hashes to disk
- `phext_memory_status` - Show what's loaded in memory

### 2. SQ-Style REST API Methods 🌐
**Goal**: Implement methods inspired by SQ's REST API for database-like operations

#### Based on SQ REST API Analysis:
- `/api/v2/select?p=<phext>&c=<coordinate>` → `phext_select`
- `/api/v2/toc?p=<phext>` → `phext_toc` (table of contents)
- `/api/v2/delta?p=<phext>` → `phext_delta` (hierarchical checksums)
- `/api/v2/get?p=<phext>` → `phext_get_full` (complete file copy)

#### Tools to Add:
- `phext_select` - Alias for fetch but with SQ-style naming
- `phext_toc` - Table of contents (enhanced textmap)
- `phext_delta` - Hierarchical checksum map for integrity
- `phext_checksum` - File-level checksum
- `phext_push` - Write local file to coordinate
- `phext_pull` - Fetch coordinate to local file

### 3. Advanced Coordinate Operations 📍
**Goal**: More sophisticated navigation and coordinate manipulation

#### Coordinate Navigation:
- `phext_navigate` - Move through dimensions (up/down/left/right/forward/back)
- `phext_coordinate_info` - Analyze coordinate structure
- `phext_find_next_scroll` - Get next available coordinate in sequence
- `phext_coordinate_distance` - Calculate distance between coordinates

#### Coordinate Utilities:
- `phext_parse_coordinate` - Validate and parse coordinate strings
- `phext_coordinate_bounds` - Find min/max coordinates in file
- `phext_coordinate_tree` - Show hierarchical structure

### 4. Bulk Operations 📦
**Goal**: Efficient operations on multiple coordinates

#### Batch Tools:
- `phext_bulk_insert` - Insert multiple coordinate→content pairs
- `phext_bulk_fetch` - Fetch multiple coordinates at once
- `phext_bulk_delete` - Remove multiple coordinates
- `phext_batch_update` - Update multiple coordinates atomically

#### Range Operations:
- `phext_range_select` - Fetch all coordinates in range
- `phext_range_delete` - Delete all coordinates in range
- `phext_range_copy` - Copy range to different location
- `phext_range_move` - Move range to different location

### 5. File and Format Operations 🗂️
**Goal**: Better file management and format conversion

#### File Management:
- `phext_file_info` - File metadata (size, coordinate count, etc.)
- `phext_file_optimize` - Clean up and optimize file structure
- `phext_file_compare` - Compare two phext files
- `phext_file_backup` - Create timestamped backup

#### Format Conversion (Based on SQ examples):
- `phext_from_csv` - Convert CSV to phext format
- `phext_to_csv` - Export phext to CSV
- `phext_from_json` - Convert JSON to phext coordinates
- `phext_to_json` - Export phext as JSON
- `phext_from_xml` - Convert XML to phext structure

### 6. Search and Query 🔍
**Goal**: Powerful search capabilities across phext space

#### Search Tools:
- `phext_search_content` - Text search across all coordinates
- `phext_search_coordinates` - Search by coordinate patterns
- `phext_search_regex` - Regular expression search
- `phext_find_empty` - Find empty coordinates in range
- `phext_find_duplicates` - Find duplicate content

#### Query Tools:
- `phext_filter` - Filter coordinates by criteria
- `phext_sort` - Sort coordinates by content/position
- `phext_group` - Group coordinates by content similarity

### 7. Version Control & History 📚
**Goal**: Track changes and enable version control

#### Version Tools:
- `phext_diff` - Show differences between files/versions
- `phext_log` - Show change history
- `phext_revert` - Revert changes to previous state
- `phext_branch` - Create branched version of file

### 8. Integration & Import/Export 🔌
**Goal**: Better integration with external systems

#### Import/Export:
- `phext_import_directory` - Import directory structure to phext
- `phext_export_directory` - Export phext to directory structure
- `phext_import_database` - Import from database tables
- `phext_export_database` - Export to database format

## Medium Priority Enhancements 🎯

### 9. Visualization Tools 👁️
- `phext_visualize` - Generate ASCII art visualization of structure
- `phext_stats` - Statistical analysis of content distribution
- `phext_density_map` - Show density of content across dimensions

### 10. Collaboration Features 🤝
- `phext_lock` - Lock coordinates for editing
- `phext_unlock` - Release coordinate locks
- `phext_conflict_detect` - Find conflicting changes
- `phext_merge_conflicts` - Resolve merge conflicts

### 11. Performance Monitoring 📊
- `phext_benchmark` - Performance testing of operations
- `phext_memory_usage` - Show memory consumption
- `phext_operation_stats` - Statistics on operation frequency

## Low Priority / Future Enhancements 🔮

### 12. Advanced Features
- `phext_compress` - Compress phext files
- `phext_encrypt` - Encrypt sensitive coordinates
- `phext_sync` - Synchronize with remote phext servers
- `phext_replicate` - Set up replication between files

### 13. Plugin System
- Support for custom phext operations
- Plugin discovery and loading
- Custom coordinate validators

## Implementation Strategy 📋

### Phase 1: Performance (Next Session)
1. Implement hash-based state management
2. Add memory management tools
3. Optimize existing operations

### Phase 2: SQ-Style API
1. Add SQ-inspired REST-style tools
2. Implement toc/delta/checksum functionality
3. Add push/pull operations

### Phase 3: Advanced Operations
1. Navigation and coordinate utilities
2. Bulk operations
3. Search and query tools

### Phase 4: Integration
1. Format conversion tools
2. Import/export capabilities
3. External system integration

## Technical Notes 📝

### Performance Considerations:
- Use `explode()` to convert to hash for operations
- Use `implode()` only when saving to disk
- Cache coordinate hashes in memory
- Batch operations when possible

### API Design:
- Maintain consistency with existing tool naming
- Follow SQ REST API patterns where applicable
- Ensure all tools are stateless (MCP requirement)
- Use clear, descriptive parameter names

### Testing Strategy:
- Unit tests for each new tool
- Performance benchmarks for optimized operations
- Integration tests with Claude Desktop
- Test with various phext file sizes

## References 📚
- [SQ Repository](https://github.com/wbic16/SQ) - REST API examples and unit tests
- [Phext.io](https://phext.io) - Official phext documentation
- [libphext-py](https://github.com/wbic16/libphext-py) - Python library documentation
- Will's feedback on performance optimization patterns

---

**Next Steps**: Start with Phase 1 performance optimizations, focusing on hash-based state management as recommended by Will.
