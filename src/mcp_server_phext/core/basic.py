"""
Basic phext operations with hash-based performance optimization.

This module implements the core CRUD operations on phext files using the enhanced
hash-based state management for better performance.
"""

import logging
from typing import Optional, Dict, Any
from phext.coordinate import Coordinate
from phext.range import Range

from .state import get_state

logger = logging.getLogger(__name__)


def phext_fetch(coordinate: str, file_path: Optional[str] = None) -> str:
    """Fetch content from a specific phext coordinate."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Direct hash lookup for performance
        content = coord_hash.get(coordinate, "")
        return content if content else "(empty)"
    except Exception as e:
        raise RuntimeError(f"Error fetching phext coordinate: {str(e)}")


def phext_insert(coordinate: str, content: str, file_path: Optional[str] = None) -> str:
    """Insert content at a phext coordinate (appends to existing content)."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Hash-based operation
        existing_content = coord_hash.get(coordinate, "")
        coord_hash[coordinate] = existing_content + content
        
        state.mark_dirty(actual_file_path)
        state.save_hash_to_file(actual_file_path)
        
        return f"Successfully inserted content at {coordinate}"
    except Exception as e:
        raise RuntimeError(f"Error inserting to phext coordinate: {str(e)}")


def phext_replace(coordinate: str, content: str, file_path: Optional[str] = None) -> str:
    """Replace content at a phext coordinate."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Hash-based operation
        coord_hash[coordinate] = content
        
        state.mark_dirty(actual_file_path)
        state.save_hash_to_file(actual_file_path)
        
        return f"Successfully replaced content at {coordinate}"
    except Exception as e:
        raise RuntimeError(f"Error replacing phext coordinate: {str(e)}")


def phext_remove(coordinate: str, file_path: Optional[str] = None) -> str:
    """Remove content at a phext coordinate."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Hash-based operation
        coord_hash.pop(coordinate, None)
        
        state.mark_dirty(actual_file_path)
        state.save_hash_to_file(actual_file_path)
        
        return f"Successfully removed content at {coordinate}"
    except Exception as e:
        raise RuntimeError(f"Error removing phext coordinate: {str(e)}")


def phext_range_replace(start_coordinate: str, end_coordinate: str, content: str, file_path: Optional[str] = None) -> str:
    """Replace content across a range of coordinates."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        
        # For range operations, we need to fall back to the phext library
        # since we need to work with the actual coordinate objects
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Convert hash back to string buffer for range operation
        coord_map = {}
        for coord_str, coord_content in coord_hash.items():
            try:
                coord = Coordinate.from_string(coord_str)
                coord_map[coord] = coord_content
            except Exception as e:
                logger.warning(f"Skipping invalid coordinate {coord_str}: {e}")
        
        buffer = state.phext.implode(coord_map)
        
        # Perform range operation
        start_coord = Coordinate.from_string(start_coordinate)
        end_coord = Coordinate.from_string(end_coordinate)
        range_obj = Range(start_coord, end_coord)
        new_buffer = state.phext.range_replace(buffer, range_obj, content)
        
        # Explode back to hash
        new_coord_map = state.phext.explode(new_buffer)
        coord_hash.clear()
        coord_hash.update({str(coord): coord_content for coord, coord_content in new_coord_map.items()})
        
        state.mark_dirty(actual_file_path)
        state.save_hash_to_file(actual_file_path)
        
        return f"Successfully replaced range {start_coordinate} to {end_coordinate}"
    except Exception as e:
        raise RuntimeError(f"Error replacing phext range: {str(e)}")


def phext_explode(file_path: Optional[str] = None) -> str:
    """Get a map of all coordinates and their content in the phext."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        result_text = f"Found {len(coord_hash)} coordinates:\\n"
        for coord, content in coord_hash.items():
            preview = content[:100] + "..." if len(content) > 100 else content
            result_text += f"  {coord}: {preview}\\n"
        
        return result_text
    except Exception as e:
        raise RuntimeError(f"Error exploding phext file: {str(e)}")


def phext_textmap(file_path: Optional[str] = None) -> str:
    """Get a text-based map of all coordinates and content summaries."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        
        # For textmap, we need the phext library's implementation
        # So we'll convert hash to buffer first
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        if not coord_hash:
            return "(empty phext)"
        
        # Convert hash to coord_map for textmap
        coord_map = {}
        for coord_str, content in coord_hash.items():
            try:
                coord = Coordinate.from_string(coord_str)
                coord_map[coord] = content
            except Exception as e:
                logger.warning(f"Skipping invalid coordinate {coord_str}: {e}")
        
        buffer = state.phext.implode(coord_map)
        textmap = state.phext.textmap(buffer)
        return textmap or "(empty phext)"
    except Exception as e:
        raise RuntimeError(f"Error creating phext textmap: {str(e)}")


def phext_normalize(file_path: Optional[str] = None) -> str:
    """Normalize a phext file (clean up and optimize structure)."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Convert to buffer for normalize operation
        coord_map = {}
        for coord_str, content in coord_hash.items():
            try:
                coord = Coordinate.from_string(coord_str)
                coord_map[coord] = content
            except Exception as e:
                logger.warning(f"Skipping invalid coordinate {coord_str}: {e}")
        
        buffer = state.phext.implode(coord_map)
        normalized = state.phext.normalize(buffer)
        
        # Explode back to hash
        new_coord_map = state.phext.explode(normalized)
        coord_hash.clear()
        coord_hash.update({str(coord): content for coord, content in new_coord_map.items()})
        
        state.mark_dirty(actual_file_path)
        state.save_hash_to_file(actual_file_path)
        
        return f"Successfully normalized phext file: {actual_file_path}"
    except Exception as e:
        raise RuntimeError(f"Error normalizing phext file: {str(e)}")


def phext_merge(left_file: str, right_file: str, output_file: Optional[str] = None) -> str:
    """Merge two phext files together."""
    try:
        state = get_state()
        left_path = state.get_file_path(left_file)
        right_path = state.get_file_path(right_file)
        output_path = state.get_file_path(output_file or left_file)
        
        left_hash = state.load_file_as_hash(left_path)
        right_hash = state.load_file_as_hash(right_path)
        
        # Simple merge: right file coordinates override left file coordinates
        merged_hash = left_hash.copy()
        merged_hash.update(right_hash)
        
        # Save merged result
        state.phext_hashes[output_path] = merged_hash
        state.mark_dirty(output_path)
        state.save_hash_to_file(output_path)
        
        return f"Successfully merged {left_path} and {right_path} into {output_path}"
    except Exception as e:
        raise RuntimeError(f"Error merging phext files: {str(e)}")


def phext_create_file(file_path: str, initial_content: Optional[str] = None) -> str:
    """Create a new phext file."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        
        # Create new phext file
        if initial_content:
            # If initial content provided, insert it at the default coordinate
            default_coord = str(state.phext.defaultCoordinate())
            new_hash = {default_coord: initial_content}
        else:
            new_hash = {}
        
        state.phext_hashes[actual_file_path] = new_hash
        state.file_loaded_as_hash.add(actual_file_path)
        state.mark_dirty(actual_file_path)
        state.save_hash_to_file(actual_file_path)
        
        return f"Successfully created phext file: {actual_file_path}"
    except Exception as e:
        raise RuntimeError(f"Error creating phext file: {str(e)}")
