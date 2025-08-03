"""
Bulk operations for efficient batch processing of phext coordinates.

This module implements efficient operations on multiple coordinates, including
batch updates, range operations, and bulk data processing.
"""

import logging
from typing import Optional, Dict, Any, List, Union

from .state import get_state

logger = logging.getLogger(__name__)


def phext_bulk_insert(coordinate_content_pairs: List[Dict[str, str]], file_path: Optional[str] = None) -> Dict[str, Any]:
    """Insert multiple coordinate→content pairs efficiently."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Validate input format
        if not isinstance(coordinate_content_pairs, list):
            raise ValueError("coordinate_content_pairs must be a list of dictionaries")
        
        inserted_count = 0
        errors = []
        
        for i, pair in enumerate(coordinate_content_pairs):
            try:
                if not isinstance(pair, dict) or "coordinate" not in pair or "content" not in pair:
                    errors.append(f"Item {i}: Invalid format, expected {{'coordinate': str, 'content': str}}")
                    continue
                
                coordinate = pair["coordinate"]
                content = pair["content"]
                
                # Append to existing content (insert behavior)
                existing_content = coord_hash.get(coordinate, "")
                coord_hash[coordinate] = existing_content + content
                inserted_count += 1
                
            except Exception as e:
                errors.append(f"Item {i} ({pair.get('coordinate', 'unknown')}): {str(e)}")
        
        # Save if any insertions succeeded
        if inserted_count > 0:
            state.mark_dirty(actual_file_path)
            state.save_hash_to_file(actual_file_path)
        
        return {
            "success": inserted_count > 0,
            "inserted_count": inserted_count,
            "total_attempted": len(coordinate_content_pairs),
            "errors": errors,
            "error_count": len(errors),
            "message": f"Bulk insert: {inserted_count} successful, {len(errors)} errors"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error in bulk insert: {str(e)}"
        }


def phext_bulk_fetch(coordinates: List[str], file_path: Optional[str] = None) -> Dict[str, Any]:
    """Fetch multiple coordinates at once."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        results = {}
        found_count = 0
        
        for coordinate in coordinates:
            content = coord_hash.get(coordinate, "")
            results[coordinate] = {
                "content": content,
                "found": bool(content),
                "size": len(content)
            }
            if content:
                found_count += 1
        
        return {
            "success": True,
            "total_requested": len(coordinates),
            "found_count": found_count,
            "missing_count": len(coordinates) - found_count,
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error in bulk fetch: {str(e)}"
        }


def phext_bulk_update(coordinate_content_pairs: List[Dict[str, str]], file_path: Optional[str] = None) -> Dict[str, Any]:
    """Update multiple coordinates atomically."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Validate input format
        if not isinstance(coordinate_content_pairs, list):
            raise ValueError("coordinate_content_pairs must be a list of dictionaries")
        
        updated_count = 0
        errors = []
        
        for i, pair in enumerate(coordinate_content_pairs):
            try:
                if not isinstance(pair, dict) or "coordinate" not in pair or "content" not in pair:
                    errors.append(f"Item {i}: Invalid format, expected {{'coordinate': str, 'content': str}}")
                    continue
                
                coordinate = pair["coordinate"]
                content = pair["content"]
                
                # Replace content (update behavior)
                coord_hash[coordinate] = content
                updated_count += 1
                
            except Exception as e:
                errors.append(f"Item {i} ({pair.get('coordinate', 'unknown')}): {str(e)}")
        
        # Save if any updates succeeded
        if updated_count > 0:
            state.mark_dirty(actual_file_path)
            state.save_hash_to_file(actual_file_path)
        
        return {
            "success": updated_count > 0,
            "updated_count": updated_count,
            "total_attempted": len(coordinate_content_pairs),
            "errors": errors,
            "error_count": len(errors),
            "message": f"Bulk update: {updated_count} successful, {len(errors)} errors"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error in bulk update: {str(e)}"
        }


def phext_bulk_delete(coordinates: List[str], file_path: Optional[str] = None) -> Dict[str, Any]:
    """Remove multiple coordinates efficiently."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        deleted_count = 0
        not_found_count = 0
        
        for coordinate in coordinates:
            if coordinate in coord_hash:
                del coord_hash[coordinate]
                deleted_count += 1
            else:
                not_found_count += 1
        
        # Save if any deletions occurred
        if deleted_count > 0:
            state.mark_dirty(actual_file_path)
            state.save_hash_to_file(actual_file_path)
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "not_found_count": not_found_count,
            "total_attempted": len(coordinates),
            "message": f"Bulk delete: {deleted_count} deleted, {not_found_count} not found"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error in bulk delete: {str(e)}"
        }


def phext_range_select(start_coordinate: str, end_coordinate: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """Fetch all coordinates in range."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Parse coordinate bounds
        start_parts = start_coordinate.split('/')
        end_parts = end_coordinate.split('/')
        
        if len(start_parts) != len(end_parts):
            raise ValueError("Start and end coordinates must have same number of dimensions")
        
        # Generate all coordinates in range
        selected_coords = {}
        total_content_size = 0
        
        for coord_str, content in coord_hash.items():
            if _coordinate_in_range(coord_str, start_coordinate, end_coordinate):
                selected_coords[coord_str] = content
                total_content_size += len(content)
        
        return {
            "success": True,
            "start_coordinate": start_coordinate,
            "end_coordinate": end_coordinate,
            "coordinates_in_range": len(selected_coords),
            "total_content_size": total_content_size,
            "coordinates": selected_coords
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error in range select: {str(e)}"
        }


def phext_range_delete(start_coordinate: str, end_coordinate: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """Delete all coordinates in range."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Find coordinates in range
        coords_to_delete = []
        for coord_str in coord_hash.keys():
            if _coordinate_in_range(coord_str, start_coordinate, end_coordinate):
                coords_to_delete.append(coord_str)
        
        # Delete coordinates
        deleted_count = 0
        for coord in coords_to_delete:
            del coord_hash[coord]
            deleted_count += 1
        
        # Save if any deletions occurred
        if deleted_count > 0:
            state.mark_dirty(actual_file_path)
            state.save_hash_to_file(actual_file_path)
        
        return {
            "success": True,
            "start_coordinate": start_coordinate,
            "end_coordinate": end_coordinate,
            "deleted_count": deleted_count,
            "message": f"Range delete: {deleted_count} coordinates removed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error in range delete: {str(e)}"
        }


def phext_range_copy(start_coordinate: str, end_coordinate: str, dest_start_coordinate: str, file_path: Optional[str] = None, dest_file_path: Optional[str] = None) -> Dict[str, Any]:
    """Copy range to different location."""
    try:
        state = get_state()
        source_file_path = state.get_file_path(file_path)
        destination_file_path = state.get_file_path(dest_file_path or file_path)
        
        source_hash = state.load_file_as_hash(source_file_path)
        dest_hash = state.load_file_as_hash(destination_file_path)
        
        # Find coordinates in source range
        source_coords = {}
        for coord_str, content in source_hash.items():
            if _coordinate_in_range(coord_str, start_coordinate, end_coordinate):
                source_coords[coord_str] = content
        
        if not source_coords:
            return {
                "success": False,
                "message": "No coordinates found in specified range"
            }
        
        # Calculate offset for destination
        offset = _calculate_coordinate_offset(start_coordinate, dest_start_coordinate)
        
        # Copy coordinates with offset
        copied_count = 0
        for source_coord, content in source_coords.items():
            dest_coord = _apply_coordinate_offset(source_coord, offset)
            dest_hash[dest_coord] = content
            copied_count += 1
        
        # Save destination file
        if copied_count > 0:
            state.mark_dirty(destination_file_path)
            state.save_hash_to_file(destination_file_path)
        
        return {
            "success": True,
            "source_range": f"{start_coordinate} to {end_coordinate}",
            "destination_start": dest_start_coordinate,
            "copied_count": copied_count,
            "source_file": source_file_path,
            "destination_file": destination_file_path,
            "message": f"Range copy: {copied_count} coordinates copied"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error in range copy: {str(e)}"
        }


def phext_range_move(start_coordinate: str, end_coordinate: str, dest_start_coordinate: str, file_path: Optional[str] = None, dest_file_path: Optional[str] = None) -> Dict[str, Any]:
    """Move range to different location."""
    try:
        # First copy the range
        copy_result = phext_range_copy(start_coordinate, end_coordinate, dest_start_coordinate, file_path, dest_file_path)
        
        if not copy_result["success"]:
            return copy_result
        
        # Then delete the original range (only if copying to different file)
        if dest_file_path and dest_file_path != file_path:
            delete_result = phext_range_delete(start_coordinate, end_coordinate, file_path)
            
            return {
                "success": delete_result["success"],
                "source_range": f"{start_coordinate} to {end_coordinate}",
                "destination_start": dest_start_coordinate,
                "moved_count": copy_result["copied_count"],
                "source_file": copy_result["source_file"],
                "destination_file": copy_result["destination_file"],
                "message": f"Range move: {copy_result['copied_count']} coordinates moved"
            }
        else:
            return {
                "success": False,
                "message": "Cannot move range within same file (use copy instead)"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error in range move: {str(e)}"
        }


def _coordinate_in_range(coord_str: str, start_coord: str, end_coord: str) -> bool:
    """Check if coordinate is within range (inclusive)."""
    try:
        # Parse coordinates
        coord_parts = coord_str.split('/')
        start_parts = start_coord.split('/')
        end_parts = end_coord.split('/')
        
        if len(coord_parts) != len(start_parts) or len(coord_parts) != len(end_parts):
            return False
        
        # Check each dimension
        for coord_part, start_part, end_part in zip(coord_parts, start_parts, end_parts):
            coord_values = [int(x) for x in coord_part.split('.')]
            start_values = [int(x) for x in start_part.split('.')]
            end_values = [int(x) for x in end_part.split('.')]
            
            # Check if coordinate is within bounds for this dimension
            for coord_val, start_val, end_val in zip(coord_values, start_values, end_values):
                if coord_val < start_val or coord_val > end_val:
                    return False
        
        return True
    except (ValueError, IndexError):
        return False


def _calculate_coordinate_offset(source_coord: str, dest_coord: str) -> List[List[int]]:
    """Calculate offset between two coordinates."""
    source_parts = source_coord.split('/')
    dest_parts = dest_coord.split('/')
    
    offset = []
    for source_part, dest_part in zip(source_parts, dest_parts):
        source_values = [int(x) for x in source_part.split('.')]
        dest_values = [int(x) for x in dest_part.split('.')]
        
        part_offset = []
        for src_val, dst_val in zip(source_values, dest_values):
            part_offset.append(dst_val - src_val)
        
        offset.append(part_offset)
    
    return offset


def _apply_coordinate_offset(coord_str: str, offset: List[List[int]]) -> str:
    """Apply offset to coordinate."""
    coord_parts = coord_str.split('/')
    new_parts = []
    
    for i, (coord_part, part_offset) in enumerate(zip(coord_parts, offset)):
        coord_values = [int(x) for x in coord_part.split('.')]
        new_values = []
        
        for j, (coord_val, off_val) in enumerate(zip(coord_values, part_offset)):
            new_val = coord_val + off_val
            # Ensure coordinates don't go below 1
            new_values.append(max(1, new_val))
        
        new_parts.append('.'.join(str(x) for x in new_values))
    
    return '/'.join(new_parts)
