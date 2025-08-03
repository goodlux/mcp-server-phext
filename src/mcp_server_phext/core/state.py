"""
Enhanced state management for phext MCP server with hash-based performance optimization.

This module implements Will's recommendation for performance improvements:
- Use hash/dictionary interfaces for runtime performance instead of string serialization
- Load file → explode to hash → operations on hash → implode → save file
"""

import os
import logging
from typing import Dict, Set, Optional, Any
from phext.phext import Phext
from phext.coordinate import Coordinate

logger = logging.getLogger(__name__)


class PhextServerState:
    """Enhanced state management with hash-based performance optimization."""
    
    def __init__(self, default_phext_file: Optional[str] = None):
        self.default_phext_file = default_phext_file
        self.phext = Phext()
        
        # Hash-based state management for performance
        self.phext_hashes: Dict[str, Dict[str, str]] = {}  # file_path -> {coordinate: content}
        self.dirty_files: Set[str] = set()  # Track which files need saving
        self.file_loaded_as_hash: Set[str] = set()  # Track which files are loaded as hashes
        
        # Legacy string buffer support (kept for compatibility)
        self.phext_buffers: Dict[str, str] = {}
    
    def get_file_path(self, file_path: Optional[str] = None) -> str:
        """Get the file path to use, defaulting to the configured default."""
        if file_path is None:
            file_path = self.default_phext_file
        
        if file_path is None:
            raise ValueError("No phext file specified and no default set")
        
        # Expand user path
        return os.path.expanduser(file_path)
    
    def load_file_as_hash(self, file_path: str) -> Dict[str, str]:
        """Load file and explode to coordinate→content hash for performance."""
        if file_path not in self.phext_hashes:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        buffer = f.read()
                    # Explode to hash
                    coord_map = self.phext.explode(buffer)
                    # Convert Coordinate objects to strings for JSON serialization
                    self.phext_hashes[file_path] = {str(coord): content for coord, content in coord_map.items()}
                else:
                    # Create new empty hash
                    self.phext_hashes[file_path] = {}
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                self.file_loaded_as_hash.add(file_path)
                logger.info(f"Loaded {len(self.phext_hashes[file_path])} coordinates from {file_path}")
            except Exception as e:
                raise RuntimeError(f"Error loading phext file as hash {file_path}: {str(e)}")
        
        return self.phext_hashes[file_path]
    
    def save_hash_to_file(self, file_path: str) -> None:
        """Implode hash and save to file."""
        if file_path not in self.phext_hashes:
            raise RuntimeError(f"No hash loaded for file {file_path}")
        
        try:
            # Convert string coordinates back to Coordinate objects
            coord_map = {}
            for coord_str, content in self.phext_hashes[file_path].items():
                try:
                    coord = Coordinate.from_string(coord_str)
                    coord_map[coord] = content
                except Exception as e:
                    logger.warning(f"Skipping invalid coordinate {coord_str}: {e}")
            
            # Implode hash back to string
            buffer = self.phext.implode(coord_map)
            
            # Save to disk
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(buffer)
            
            # Mark as clean
            self.dirty_files.discard(file_path)
            logger.info(f"Saved {len(coord_map)} coordinates to {file_path}")
        except Exception as e:
            raise RuntimeError(f"Error saving hash to file {file_path}: {str(e)}")
    
    def mark_dirty(self, file_path: str) -> None:
        """Mark a file as dirty (needs saving)."""
        self.dirty_files.add(file_path)
    
    def is_dirty(self, file_path: str) -> bool:
        """Check if a file is dirty (needs saving)."""
        return file_path in self.dirty_files
    
    def flush_dirty_files(self) -> Dict[str, str]:
        """Save all dirty files to disk."""
        results = {}
        for file_path in list(self.dirty_files):
            try:
                self.save_hash_to_file(file_path)
                results[file_path] = "saved"
            except Exception as e:
                results[file_path] = f"error: {str(e)}"
        return results
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get memory usage and status information."""
        status = {
            "files_loaded_as_hash": len(self.phext_hashes),
            "dirty_files": len(self.dirty_files),
            "legacy_buffers": len(self.phext_buffers),
            "total_coordinates": sum(len(coord_map) for coord_map in self.phext_hashes.values()),
            "files": {}
        }
        
        for file_path in self.phext_hashes:
            coord_count = len(self.phext_hashes[file_path])
            total_content_size = sum(len(content) for content in self.phext_hashes[file_path].values())
            status["files"][file_path] = {
                "coordinates": coord_count,
                "content_size": total_content_size,
                "dirty": file_path in self.dirty_files,
                "loaded_as_hash": file_path in self.file_loaded_as_hash
            }
        
        return status
    
    def unload_file(self, file_path: str) -> None:
        """Unload a file from memory (saves if dirty first)."""
        if file_path in self.dirty_files:
            self.save_hash_to_file(file_path)
        
        self.phext_hashes.pop(file_path, None)
        self.phext_buffers.pop(file_path, None)
        self.dirty_files.discard(file_path)
        self.file_loaded_as_hash.discard(file_path)
    
    # Legacy methods for backward compatibility
    def load_file(self, file_path: str) -> str:
        """Legacy method: Load a phext file into memory as string buffer."""
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
        """Legacy method: Save the phext buffer to disk."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.phext_buffers[file_path])
        except Exception as e:
            raise RuntimeError(f"Error saving phext file {file_path}: {str(e)}")


# Global state instance
_state: Optional[PhextServerState] = None


def get_state() -> PhextServerState:
    """Get the global state instance."""
    global _state
    if _state is None:
        _state = PhextServerState()
    return _state


def init_state(default_phext_file: Optional[str] = None) -> PhextServerState:
    """Initialize the global state with configuration."""
    global _state
    _state = PhextServerState(default_phext_file)
    return _state
