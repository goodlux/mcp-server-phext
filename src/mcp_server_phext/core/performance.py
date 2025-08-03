"""
Performance and memory management tools for phext MCP server.

This module implements Will's recommended performance optimization tools for
managing hash-based state and memory usage.
"""

import logging
from typing import Optional, Dict, Any, List

from .state import get_state

logger = logging.getLogger(__name__)


def phext_load_to_memory(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Explicitly load file into hash for performance."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        return {
            "success": True,
            "file_path": actual_file_path,
            "coordinates_loaded": len(coord_hash),
            "total_content_size": sum(len(content) for content in coord_hash.values()),
            "message": f"Loaded {len(coord_hash)} coordinates from {actual_file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error loading file to memory: {str(e)}"
        }


def phext_flush_to_disk(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Force save dirty hashes to disk."""
    try:
        state = get_state()
        
        if file_path:
            # Flush specific file
            actual_file_path = state.get_file_path(file_path)
            if actual_file_path in state.phext_hashes:
                if state.is_dirty(actual_file_path):
                    state.save_hash_to_file(actual_file_path)
                    return {
                        "success": True,
                        "file_path": actual_file_path,
                        "message": f"Flushed {actual_file_path} to disk"
                    }
                else:
                    return {
                        "success": True,
                        "file_path": actual_file_path,
                        "message": f"File {actual_file_path} is already clean (no changes to save)"
                    }
            else:
                return {
                    "success": False,
                    "error": f"File {actual_file_path} not loaded in memory",
                    "message": f"File {actual_file_path} not loaded in memory"
                }
        else:
            # Flush all dirty files
            results = state.flush_dirty_files()
            saved_count = sum(1 for result in results.values() if result == "saved")
            error_count = len(results) - saved_count
            
            return {
                "success": error_count == 0,
                "files_saved": saved_count,
                "files_with_errors": error_count,
                "results": results,
                "message": f"Flushed {saved_count} files to disk, {error_count} errors"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error flushing to disk: {str(e)}"
        }


def phext_memory_status() -> Dict[str, Any]:
    """Show what's loaded in memory."""
    try:
        state = get_state()
        status = state.get_memory_status()
        
        # Add summary information
        total_coord_count = status["total_coordinates"]
        total_content_size = sum(
            file_info["content_size"] 
            for file_info in status["files"].values()
        )
        
        status.update({
            "summary": {
                "total_coordinates": total_coord_count,
                "total_content_size_bytes": total_content_size,
                "total_content_size_mb": round(total_content_size / (1024 * 1024), 2),
                "files_needing_save": len(state.dirty_files),
                "performance_mode_files": len(state.file_loaded_as_hash)
            }
        })
        
        return status
    except Exception as e:
        return {
            "error": str(e),
            "message": f"Error getting memory status: {str(e)}"
        }


def phext_unload_file(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Unload a file from memory (saves if dirty first)."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        
        if actual_file_path not in state.phext_hashes:
            return {
                "success": False,
                "file_path": actual_file_path,
                "message": f"File {actual_file_path} is not loaded in memory"
            }
        
        was_dirty = state.is_dirty(actual_file_path)
        coord_count = len(state.phext_hashes[actual_file_path])
        
        state.unload_file(actual_file_path)
        
        return {
            "success": True,
            "file_path": actual_file_path,
            "coordinates_unloaded": coord_count,
            "was_dirty": was_dirty,
            "message": f"Unloaded {coord_count} coordinates from memory" + 
                      (" (saved changes first)" if was_dirty else "")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error unloading file: {str(e)}"
        }


def phext_file_info(file_path: Optional[str] = None) -> Dict[str, Any]:
    """File metadata (size, coordinate count, etc.)."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        
        # Load file to get info
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Calculate statistics
        coord_count = len(coord_hash)
        total_content_size = sum(len(content) for content in coord_hash.values())
        non_empty_coords = sum(1 for content in coord_hash.values() if content.strip())
        avg_content_size = total_content_size / coord_count if coord_count > 0 else 0
        
        # Find coordinate bounds
        coordinates = list(coord_hash.keys())
        
        # Get file system info
        import os
        file_stats = os.stat(actual_file_path) if os.path.exists(actual_file_path) else None
        
        info = {
            "file_path": actual_file_path,
            "exists": os.path.exists(actual_file_path),
            "coordinates": {
                "total": coord_count,
                "non_empty": non_empty_coords,
                "empty": coord_count - non_empty_coords
            },
            "content": {
                "total_size_bytes": total_content_size,
                "total_size_mb": round(total_content_size / (1024 * 1024), 2),
                "avg_content_size": round(avg_content_size, 2)
            },
            "memory_status": {
                "loaded_as_hash": actual_file_path in state.file_loaded_as_hash,
                "dirty": state.is_dirty(actual_file_path)
            }
        }
        
        if file_stats:
            info["file_system"] = {
                "size_bytes": file_stats.st_size,
                "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                "modified_time": file_stats.st_mtime,
                "created_time": file_stats.st_ctime
            }
        
        if coordinates:
            info["coordinate_sample"] = coordinates[:10]  # First 10 coordinates
        
        return info
    except Exception as e:
        return {
            "error": str(e),
            "message": f"Error getting file info: {str(e)}"
        }


def phext_optimize_memory() -> Dict[str, Any]:
    """Optimize memory usage by cleaning up and reorganizing data."""
    try:
        state = get_state()
        
        # Statistics before optimization
        initial_status = state.get_memory_status()
        initial_files = len(state.phext_hashes)
        initial_coords = initial_status["total_coordinates"]
        
        # Optimization steps:
        # 1. Save all dirty files
        flush_results = state.flush_dirty_files()
        
        # 2. Remove empty coordinate entries
        cleaned_coords = 0
        for file_path, coord_hash in state.phext_hashes.items():
            empty_coords = [coord for coord, content in coord_hash.items() if not content.strip()]
            for coord in empty_coords:
                del coord_hash[coord]
                cleaned_coords += 1
            if empty_coords:
                state.mark_dirty(file_path)
        
        # 3. Save cleaned files
        if cleaned_coords > 0:
            state.flush_dirty_files()
        
        # Statistics after optimization
        final_status = state.get_memory_status()
        final_coords = final_status["total_coordinates"]
        
        return {
            "success": True,
            "optimization_results": {
                "files_flushed": len([r for r in flush_results.values() if r == "saved"]),
                "empty_coordinates_removed": cleaned_coords,
                "coordinates_before": initial_coords,
                "coordinates_after": final_coords,
                "coordinates_saved": initial_coords - final_coords,
                "memory_improvement": f"{cleaned_coords} empty coordinates removed"
            },
            "message": f"Optimized memory: removed {cleaned_coords} empty coordinates"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error optimizing memory: {str(e)}"
        }
