"""
Search and query capabilities for phext files.

This module implements powerful search functionality across phext coordinate space,
including text search, pattern matching, and content analysis.
"""

import logging
import re
from typing import Optional, Dict, Any, List, Set

from .state import get_state

logger = logging.getLogger(__name__)


def phext_search_content(query: str, file_path: Optional[str] = None, case_sensitive: bool = False, whole_words: bool = False) -> Dict[str, Any]:
    """Text search across all coordinates."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        if not coord_hash:
            return {
                "query": query,
                "file_path": actual_file_path,
                "matches": [],
                "total_matches": 0,
                "message": "No coordinates found in file"
            }
        
        # Prepare search pattern
        search_query = query if case_sensitive else query.lower()
        if whole_words:
            pattern = re.compile(r'\b' + re.escape(search_query) + r'\b', 
                               re.IGNORECASE if not case_sensitive else 0)
        
        matches = []
        total_matches = 0
        
        for coordinate, content in coord_hash.items():
            search_content = content if case_sensitive else content.lower()
            
            if whole_words:
                # Use regex for whole word matching
                found_matches = list(pattern.finditer(content))
                if found_matches:
                    match_positions = [(m.start(), m.end()) for m in found_matches]
                    total_matches += len(found_matches)
                else:
                    continue
            else:
                # Simple substring search
                if search_query not in search_content:
                    continue
                
                # Find all occurrences
                match_positions = []
                start = 0
                while True:
                    pos = search_content.find(search_query, start)
                    if pos == -1:
                        break
                    match_positions.append((pos, pos + len(search_query)))
                    start = pos + 1
                    total_matches += 1
            
            # Extract context around matches
            match_contexts = []
            for start_pos, end_pos in match_positions:
                context_start = max(0, start_pos - 50)
                context_end = min(len(content), end_pos + 50)
                context = content[context_start:context_end]
                
                match_contexts.append({
                    "position": start_pos,
                    "matched_text": content[start_pos:end_pos],
                    "context": context,
                    "line_number": content[:start_pos].count('\n') + 1
                })
            
            matches.append({
                "coordinate": coordinate,
                "match_count": len(match_positions),
                "content_size": len(content),
                "matches": match_contexts
            })
        
        return {
            "query": query,
            "file_path": actual_file_path,
            "case_sensitive": case_sensitive,
            "whole_words": whole_words,
            "total_matches": total_matches,
            "coordinates_with_matches": len(matches),
            "total_coordinates_searched": len(coord_hash),
            "matches": matches
        }
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "message": f"Error searching content: {str(e)}"
        }


def phext_search_coordinates(pattern: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """Search by coordinate patterns."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        if not coord_hash:
            return {
                "pattern": pattern,
                "file_path": actual_file_path,
                "matches": [],
                "message": "No coordinates found in file"
            }
        
        # Compile regex pattern
        try:
            regex_pattern = re.compile(pattern)
        except re.error as e:
            return {
                "pattern": pattern,
                "error": f"Invalid regex pattern: {str(e)}",
                "message": "Please provide a valid regular expression"
            }
        
        matches = []
        for coordinate, content in coord_hash.items():
            if regex_pattern.search(coordinate):
                matches.append({
                    "coordinate": coordinate,
                    "content_size": len(content),
                    "content_preview": content[:100] + "..." if len(content) > 100 else content,
                    "has_content": bool(content.strip())
                })
        
        return {
            "pattern": pattern,
            "file_path": actual_file_path,
            "matching_coordinates": len(matches),
            "total_coordinates": len(coord_hash),
            "matches": matches
        }
    except Exception as e:
        return {
            "pattern": pattern,
            "error": str(e),
            "message": f"Error searching coordinates: {str(e)}"
        }


def phext_search_regex(regex_pattern: str, file_path: Optional[str] = None, search_coordinates: bool = False) -> Dict[str, Any]:
    """Regular expression search in content or coordinates."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        if not coord_hash:
            return {
                "pattern": regex_pattern,
                "file_path": actual_file_path,
                "matches": [],
                "message": "No coordinates found in file"
            }
        
        # Compile regex pattern
        try:
            pattern = re.compile(regex_pattern, re.MULTILINE | re.DOTALL)
        except re.error as e:
            return {
                "pattern": regex_pattern,
                "error": f"Invalid regex pattern: {str(e)}",
                "message": "Please provide a valid regular expression"
            }
        
        matches = []
        total_matches = 0
        
        for coordinate, content in coord_hash.items():
            search_text = coordinate if search_coordinates else content
            found_matches = list(pattern.finditer(search_text))
            
            if found_matches:
                match_details = []
                for match in found_matches:
                    match_details.append({
                        "matched_text": match.group(0),
                        "start_position": match.start(),
                        "end_position": match.end(),
                        "groups": match.groups() if match.groups() else []
                    })
                    total_matches += 1
                
                matches.append({
                    "coordinate": coordinate,
                    "search_target": "coordinate" if search_coordinates else "content",
                    "match_count": len(found_matches),
                    "matches": match_details,
                    "content_size": len(content)
                })
        
        return {
            "pattern": regex_pattern,
            "file_path": actual_file_path,
            "search_target": "coordinates" if search_coordinates else "content",
            "total_matches": total_matches,
            "coordinates_with_matches": len(matches),
            "matches": matches
        }
    except Exception as e:
        return {
            "pattern": regex_pattern,
            "error": str(e),
            "message": f"Error in regex search: {str(e)}"
        }


def phext_find_empty(file_path: Optional[str] = None, include_whitespace_only: bool = True) -> Dict[str, Any]:
    """Find empty coordinates in file."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        empty_coordinates = []
        whitespace_only_coordinates = []
        
        for coordinate, content in coord_hash.items():
            if not content:
                empty_coordinates.append(coordinate)
            elif include_whitespace_only and not content.strip():
                whitespace_only_coordinates.append({
                    "coordinate": coordinate,
                    "content_length": len(content),
                    "whitespace_chars": repr(content)
                })
        
        total_empty = len(empty_coordinates) + len(whitespace_only_coordinates)
        
        return {
            "file_path": actual_file_path,
            "total_coordinates": len(coord_hash),
            "empty_coordinates": len(empty_coordinates),
            "whitespace_only_coordinates": len(whitespace_only_coordinates),
            "total_empty": total_empty,
            "empty_percentage": round((total_empty / len(coord_hash)) * 100, 2) if coord_hash else 0,
            "empty_coords": empty_coordinates,
            "whitespace_coords": whitespace_only_coordinates
        }
    except Exception as e:
        return {
            "file_path": file_path,
            "error": str(e),
            "message": f"Error finding empty coordinates: {str(e)}"
        }


def phext_find_duplicates(file_path: Optional[str] = None, ignore_whitespace: bool = True) -> Dict[str, Any]:
    """Find duplicate content across coordinates."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        if not coord_hash:
            return {
                "file_path": actual_file_path,
                "duplicates": [],
                "message": "No coordinates found in file"
            }
        
        # Group coordinates by content
        content_groups = {}
        for coordinate, content in coord_hash.items():
            # Normalize content for comparison
            normalized_content = content.strip() if ignore_whitespace else content
            
            # Skip empty content
            if not normalized_content:
                continue
            
            if normalized_content not in content_groups:
                content_groups[normalized_content] = []
            content_groups[normalized_content].append(coordinate)
        
        # Find duplicates (groups with more than one coordinate)
        duplicates = []
        total_duplicate_coords = 0
        
        for content, coordinates in content_groups.items():
            if len(coordinates) > 1:
                duplicate_group = {
                    "content": content,
                    "content_size": len(content),
                    "content_preview": content[:100] + "..." if len(content) > 100 else content,
                    "duplicate_count": len(coordinates),
                    "coordinates": coordinates
                }
                duplicates.append(duplicate_group)
                total_duplicate_coords += len(coordinates)
        
        # Sort by duplicate count (most duplicated first)
        duplicates.sort(key=lambda x: x["duplicate_count"], reverse=True)
        
        return {
            "file_path": actual_file_path,
            "total_coordinates": len(coord_hash),
            "unique_content_groups": len(content_groups),
            "duplicate_groups": len(duplicates),
            "total_duplicate_coordinates": total_duplicate_coords,
            "space_wasted": sum(
                (group["duplicate_count"] - 1) * group["content_size"] 
                for group in duplicates
            ),
            "duplicates": duplicates
        }
    except Exception as e:
        return {
            "file_path": file_path,
            "error": str(e),
            "message": f"Error finding duplicates: {str(e)}"
        }


def phext_filter_coordinates(criteria: Dict[str, Any], file_path: Optional[str] = None) -> Dict[str, Any]:
    """Filter coordinates by various criteria."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        if not coord_hash:
            return {
                "criteria": criteria,
                "file_path": actual_file_path,
                "matches": [],
                "message": "No coordinates found in file"
            }
        
        filtered_coordinates = []
        
        for coordinate, content in coord_hash.items():
            matches_criteria = True
            
            # Content size filters
            if "min_size" in criteria and len(content) < criteria["min_size"]:
                matches_criteria = False
            if "max_size" in criteria and len(content) > criteria["max_size"]:
                matches_criteria = False
            
            # Content type filters
            if "has_content" in criteria:
                has_content = bool(content.strip())
                if criteria["has_content"] != has_content:
                    matches_criteria = False
            
            # Line count filters
            if "min_lines" in criteria or "max_lines" in criteria:
                line_count = content.count('\n') + 1 if content else 0
                if "min_lines" in criteria and line_count < criteria["min_lines"]:
                    matches_criteria = False
                if "max_lines" in criteria and line_count > criteria["max_lines"]:
                    matches_criteria = False
            
            # Content pattern filters
            if "contains" in criteria:
                if criteria["contains"] not in content:
                    matches_criteria = False
            
            if "starts_with" in criteria:
                if not content.startswith(criteria["starts_with"]):
                    matches_criteria = False
            
            if "ends_with" in criteria:
                if not content.endswith(criteria["ends_with"]):
                    matches_criteria = False
            
            # Coordinate pattern filters
            if "coordinate_pattern" in criteria:
                try:
                    pattern = re.compile(criteria["coordinate_pattern"])
                    if not pattern.search(coordinate):
                        matches_criteria = False
                except re.error:
                    matches_criteria = False
            
            if matches_criteria:
                filtered_coordinates.append({
                    "coordinate": coordinate,
                    "content_size": len(content),
                    "line_count": content.count('\n') + 1 if content else 0,
                    "content_preview": content[:100] + "..." if len(content) > 100 else content
                })
        
        return {
            "criteria": criteria,
            "file_path": actual_file_path,
            "total_coordinates": len(coord_hash),
            "matching_coordinates": len(filtered_coordinates),
            "matches": filtered_coordinates
        }
    except Exception as e:
        return {
            "criteria": criteria,
            "file_path": file_path,
            "error": str(e),
            "message": f"Error filtering coordinates: {str(e)}"
        }


def phext_content_statistics(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Generate detailed content statistics and analysis."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        if not coord_hash:
            return {
                "file_path": actual_file_path,
                "statistics": {},
                "message": "No coordinates found in file"
            }
        
        # Basic statistics
        total_coords = len(coord_hash)
        total_content_size = sum(len(content) for content in coord_hash.values())
        non_empty_coords = sum(1 for content in coord_hash.values() if content.strip())
        
        # Size distribution
        sizes = [len(content) for content in coord_hash.values()]
        sizes.sort()
        
        # Line count distribution  
        line_counts = [content.count('\n') + 1 if content else 0 for content in coord_hash.values()]
        
        # Content type analysis
        content_types = {
            "empty": 0,
            "whitespace_only": 0,
            "single_line": 0,
            "multi_line": 0,
            "large_content": 0  # > 1KB
        }
        
        for content in coord_hash.values():
            if not content:
                content_types["empty"] += 1
            elif not content.strip():
                content_types["whitespace_only"] += 1
            elif '\n' not in content:
                content_types["single_line"] += 1
            elif len(content) > 1024:
                content_types["large_content"] += 1
            else:
                content_types["multi_line"] += 1
        
        statistics = {
            "basic": {
                "total_coordinates": total_coords,
                "non_empty_coordinates": non_empty_coords,
                "empty_coordinates": total_coords - non_empty_coords,
                "total_content_size": total_content_size,
                "average_content_size": round(total_content_size / total_coords, 2) if total_coords else 0
            },
            "size_distribution": {
                "min_size": min(sizes) if sizes else 0,
                "max_size": max(sizes) if sizes else 0,
                "median_size": sizes[len(sizes) // 2] if sizes else 0,
                "q1_size": sizes[len(sizes) // 4] if sizes else 0,
                "q3_size": sizes[3 * len(sizes) // 4] if sizes else 0
            },
            "line_distribution": {
                "min_lines": min(line_counts) if line_counts else 0,
                "max_lines": max(line_counts) if line_counts else 0,
                "average_lines": round(sum(line_counts) / len(line_counts), 2) if line_counts else 0
            },
            "content_types": content_types,
            "efficiency": {
                "utilization_rate": round((non_empty_coords / total_coords) * 100, 2) if total_coords else 0,
                "average_density": round(total_content_size / total_coords, 2) if total_coords else 0
            }
        }
        
        return {
            "file_path": actual_file_path,
            "statistics": statistics
        }
    except Exception as e:
        return {
            "file_path": file_path,
            "error": str(e),
            "message": f"Error generating statistics: {str(e)}"
        }
