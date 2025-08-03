"""
Advanced coordinate operations and navigation tools.

This module implements sophisticated navigation and coordinate manipulation tools
for working with phext's 11-dimensional coordinate space.
"""

import logging
import re
from typing import Optional, Dict, Any, List, Tuple

from .state import get_state

logger = logging.getLogger(__name__)


def phext_coordinate_info(coordinate: str) -> Dict[str, Any]:
    """Analyze coordinate structure and provide detailed information."""
    try:
        # Parse coordinate structure
        # Expected format: "library.shelf.series/collection.volume.book/chapter.section.scroll/line.column"
        parts = coordinate.split('/')
        
        info = {
            "coordinate": coordinate,
            "valid": True,
            "dimensions": len(parts),
            "structure": {},
            "analysis": {}
        }
        
        # Standard phext dimension names
        dimension_names = [
            ["library", "shelf", "series"],
            ["collection", "volume", "book"], 
            ["chapter", "section", "scroll"],
            ["line", "column"]
        ]
        
        # Parse each dimension
        for i, part in enumerate(parts):
            if i < len(dimension_names):
                dim_names = dimension_names[i]
                values = part.split('.')
                
                dim_info = {
                    "raw": part,
                    "values": values,
                    "count": len(values)
                }
                
                # Map values to named dimensions
                for j, value in enumerate(values):
                    if j < len(dim_names):
                        try:
                            dim_info[dim_names[j]] = int(value)
                        except ValueError:
                            dim_info[dim_names[j]] = value
                            info["valid"] = False
                
                info["structure"][f"dimension_{i}"] = dim_info
        
        # Analysis
        total_components = sum(len(part.split('.')) for part in parts)
        info["analysis"] = {
            "total_components": total_components,
            "max_dimension": len(parts),
            "is_default": coordinate == "1.1.1/1.1.1/1.1.1/1.1",
            "is_root_level": all(part.startswith("1.1.1") for part in parts[:3]),
            "complexity_score": total_components + len(parts)
        }
        
        return info
    except Exception as e:
        return {
            "coordinate": coordinate,
            "valid": False,
            "error": str(e),
            "message": f"Error analyzing coordinate: {str(e)}"
        }


def phext_parse_coordinate(coordinate: str) -> Dict[str, Any]:
    """Validate and parse coordinate strings."""
    try:
        from phext.coordinate import Coordinate
        
        # Try to parse with phext library
        try:
            coord_obj = Coordinate.from_string(coordinate)
            parsed = {
                "valid": True,
                "coordinate": coordinate,
                "parsed_successfully": True,
                "library_dimensions": str(coord_obj).split('/')[0] if '/' in str(coord_obj) else "",
                "message": "Coordinate is valid"
            }
        except Exception as parse_error:
            parsed = {
                "valid": False,
                "coordinate": coordinate,
                "parsed_successfully": False,
                "error": str(parse_error),
                "message": f"Invalid coordinate format: {parse_error}"
            }
        
        # Additional validation
        parts = coordinate.split('/')
        parsed["structure_analysis"] = {
            "dimension_count": len(parts),
            "expected_dimensions": 4,  # Standard phext has 4 main dimensions
            "dimension_parts": [part.split('.') for part in parts],
            "total_components": sum(len(part.split('.')) for part in parts)
        }
        
        # Check for common patterns
        patterns = {
            "is_default": coordinate == "1.1.1/1.1.1/1.1.1/1.1",
            "is_numeric": all(
                all(comp.isdigit() for comp in part.split('.'))
                for part in parts
            ),
            "has_letters": any(
                any(not comp.isdigit() for comp in part.split('.'))
                for part in parts
            )
        }
        parsed["patterns"] = patterns
        
        return parsed
    except Exception as e:
        return {
            "valid": False,
            "coordinate": coordinate,
            "error": str(e),
            "message": f"Error parsing coordinate: {str(e)}"
        }


def phext_navigate(from_coordinate: str, direction: str, steps: int = 1, file_path: Optional[str] = None) -> Dict[str, Any]:
    """Navigate through dimensions (up/down/left/right/forward/back)."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Parse starting coordinate
        parts = from_coordinate.split('/')
        if len(parts) != 4:
            raise ValueError("Coordinate must have 4 dimensions separated by /")
        
        # Convert to numeric arrays for navigation
        coords = []
        for part in parts:
            coords.append([int(x) for x in part.split('.')])
        
        # Navigation directions mapping
        nav_map = {
            "right": (3, 1),     # column + 1
            "left": (3, 1, -1),  # column - 1
            "down": (3, 0),      # line + 1
            "up": (3, 0, -1),    # line - 1
            "forward": (2, 2),   # scroll + 1
            "back": (2, 2, -1),  # scroll - 1
            "next_section": (2, 1),  # section + 1
            "prev_section": (2, 1, -1),  # section - 1
            "next_chapter": (2, 0),  # chapter + 1
            "prev_chapter": (2, 0, -1),  # chapter - 1
            "next_book": (1, 2),     # book + 1
            "prev_book": (1, 2, -1), # book - 1
        }
        
        if direction not in nav_map:
            raise ValueError(f"Unknown direction: {direction}. Valid: {list(nav_map.keys())}")
        
        # Apply navigation
        nav_info = nav_map[direction]
        dim_idx = nav_info[0]
        coord_idx = nav_info[1]
        multiplier = nav_info[2] if len(nav_info) > 2 else 1
        
        # Calculate new coordinate
        new_coords = [dim.copy() for dim in coords]
        new_coords[dim_idx][coord_idx] += (steps * multiplier)
        
        # Ensure coordinates don't go below 1
        if new_coords[dim_idx][coord_idx] < 1:
            new_coords[dim_idx][coord_idx] = 1
        
        # Build new coordinate string
        new_coordinate = '/'.join(
            '.'.join(str(x) for x in dim)
            for dim in new_coords
        )
        
        # Check if destination has content
        dest_content = coord_hash.get(new_coordinate, "")
        
        return {
            "from": from_coordinate,
            "to": new_coordinate,
            "direction": direction,
            "steps": steps,
            "has_content": bool(dest_content.strip()),
            "content_preview": dest_content[:100] + "..." if len(dest_content) > 100 else dest_content,
            "navigation_successful": True
        }
    except Exception as e:
        return {
            "from": from_coordinate,
            "direction": direction,
            "steps": steps,
            "navigation_successful": False,
            "error": str(e),
            "message": f"Navigation error: {str(e)}"
        }


def phext_find_next_scroll(coordinate: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """Get next available coordinate in sequence."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Parse base coordinate
        parts = coordinate.split('/')
        if len(parts) != 4:
            raise ValueError("Coordinate must have 4 dimensions")
        
        base_coords = []
        for part in parts:
            base_coords.append([int(x) for x in part.split('.')])
        
        # Find next available coordinates by incrementing scroll, then section, then chapter
        search_strategies = [
            (2, 2, "next_scroll"),      # Same section, next scroll
            (2, 1, "next_section"),     # Same chapter, next section  
            (2, 0, "next_chapter"),     # Same book, next chapter
            (1, 2, "next_book"),        # Same collection, next book
        ]
        
        found_coordinates = []
        
        for dim_idx, coord_idx, strategy_name in search_strategies:
            test_coords = [dim.copy() for dim in base_coords]
            
            # Try next 10 positions
            for i in range(1, 11):
                test_coords[dim_idx][coord_idx] = base_coords[dim_idx][coord_idx] + i
                
                # Reset lower dimensions to 1
                if strategy_name in ["next_section", "next_chapter", "next_book"]:
                    for reset_dim, reset_coord in [(2, 2)]:  # Reset scroll to 1
                        if reset_dim == dim_idx and reset_coord > coord_idx:
                            test_coords[reset_dim][reset_coord] = 1
                
                test_coordinate = '/'.join(
                    '.'.join(str(x) for x in dim) 
                    for dim in test_coords
                )
                
                # Check if this coordinate exists
                if test_coordinate in coord_hash:
                    content = coord_hash[test_coordinate]
                    found_coordinates.append({
                        "coordinate": test_coordinate,
                        "strategy": strategy_name,
                        "distance": i,
                        "has_content": bool(content.strip()),
                        "content_size": len(content),
                        "content_preview": content[:50] + "..." if len(content) > 50 else content
                    })
                    
                    if len(found_coordinates) >= 5:  # Limit results
                        break
        
        return {
            "base_coordinate": coordinate,
            "found_coordinates": found_coordinates,
            "total_found": len(found_coordinates),
            "search_successful": len(found_coordinates) > 0
        }
    except Exception as e:
        return {
            "base_coordinate": coordinate,
            "search_successful": False,
            "error": str(e),
            "message": f"Error finding next scroll: {str(e)}"
        }


def phext_coordinate_distance(coord1: str, coord2: str) -> Dict[str, Any]:
    """Calculate distance between coordinates."""
    try:
        # Parse both coordinates
        parts1 = coord1.split('/')
        parts2 = coord2.split('/')
        
        if len(parts1) != 4 or len(parts2) != 4:
            raise ValueError("Both coordinates must have 4 dimensions")
        
        coords1 = []
        coords2 = []
        
        for part1, part2 in zip(parts1, parts2):
            coords1.append([int(x) for x in part1.split('.')])
            coords2.append([int(x) for x in part2.split('.')])
        
        # Calculate distances for each dimension
        distances = []
        total_distance = 0
        
        dimension_names = ["library", "collection", "chapter", "line"]
        
        for i, (dim1, dim2) in enumerate(zip(coords1, coords2)):
            dim_distances = []
            for j, (val1, val2) in enumerate(zip(dim1, dim2)):
                dist = abs(val2 - val1)
                dim_distances.append(dist)
                total_distance += dist
            
            distances.append({
                "dimension": dimension_names[i] if i < len(dimension_names) else f"dim_{i}",
                "distances": dim_distances,
                "total": sum(dim_distances)
            })
        
        # Calculate Manhattan distance (sum of absolute differences)
        manhattan_distance = total_distance
        
        # Calculate Euclidean distance
        euclidean_distance = sum(
            sum((val2 - val1) ** 2 for val1, val2 in zip(dim1, dim2))
            for dim1, dim2 in zip(coords1, coords2)
        ) ** 0.5
        
        return {
            "coordinate1": coord1,
            "coordinate2": coord2,
            "dimension_distances": distances,
            "manhattan_distance": manhattan_distance,
            "euclidean_distance": round(euclidean_distance, 2),
            "same_coordinate": coord1 == coord2,
            "adjacent": manhattan_distance == 1
        }
    except Exception as e:
        return {
            "coordinate1": coord1,
            "coordinate2": coord2,
            "error": str(e),
            "message": f"Error calculating distance: {str(e)}"
        }


def phext_coordinate_bounds(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Find min/max coordinates in file."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        if not coord_hash:
            return {
                "file_path": actual_file_path,
                "bounds": None,
                "message": "No coordinates found in file"
            }
        
        # Parse all coordinates
        all_coords = []
        for coord_str in coord_hash.keys():
            try:
                parts = coord_str.split('/')
                coords = []
                for part in parts:
                    coords.append([int(x) for x in part.split('.')])
                all_coords.append((coord_str, coords))
            except ValueError:
                continue  # Skip invalid coordinates
        
        if not all_coords:
            return {
                "file_path": actual_file_path,
                "bounds": None,
                "message": "No valid numeric coordinates found"
            }
        
        # Find bounds for each dimension
        num_dimensions = len(all_coords[0][1])
        bounds = []
        
        for dim_idx in range(num_dimensions):
            max_components = max(len(coord[1][dim_idx]) for _, coord in all_coords)
            dim_bounds = []
            
            for comp_idx in range(max_components):
                values = []
                for _, coord in all_coords:
                    if dim_idx < len(coord) and comp_idx < len(coord[dim_idx]):
                        values.append(coord[dim_idx][comp_idx])
                
                if values:
                    dim_bounds.append({
                        "min": min(values),
                        "max": max(values),
                        "range": max(values) - min(values) + 1
                    })
            
            bounds.append(dim_bounds)
        
        # Find min and max coordinate strings
        min_coord = min(coord_str for coord_str, _ in all_coords)
        max_coord = max(coord_str for coord_str, _ in all_coords)
        
        return {
            "file_path": actual_file_path,
            "total_coordinates": len(coord_hash),
            "valid_coordinates": len(all_coords),
            "min_coordinate": min_coord,
            "max_coordinate": max_coord,
            "dimension_bounds": bounds,
            "bounds_summary": {
                "dimensions": len(bounds),
                "total_span": sum(
                    sum(comp["range"] for comp in dim_bounds)
                    for dim_bounds in bounds
                )
            }
        }
    except Exception as e:
        return {
            "file_path": file_path,
            "error": str(e),
            "message": f"Error finding coordinate bounds: {str(e)}"
        }
