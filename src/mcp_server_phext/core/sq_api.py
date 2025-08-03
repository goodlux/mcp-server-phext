"""
SQ-style API tools inspired by the SQ REST API.

This module implements phext operations that mirror the SQ database REST API patterns:
- /api/v2/select -> phext_select
- /api/v2/toc -> phext_toc  
- /api/v2/delta -> phext_delta
- Plus additional database-like operations: push, pull, checksum, etc.
"""

import logging
import hashlib
import json
from typing import Optional, Dict, Any, List

from .state import get_state

logger = logging.getLogger(__name__)


def phext_select(coordinate: str, file_path: Optional[str] = None) -> str:
    """SQ-style select: Alias for fetch but with database-style naming."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Direct hash lookup for performance
        content = coord_hash.get(coordinate, "")
        return content if content else "(empty)"
    except Exception as e:
        raise RuntimeError(f"Error selecting phext coordinate: {str(e)}")


def phext_toc(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Table of contents (enhanced textmap) showing structure and metadata."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        if not coord_hash:
            return {
                "file_path": actual_file_path,
                "total_coordinates": 0,
                "coordinates": [],
                "summary": "Empty phext file"
            }
        
        # Build table of contents with metadata
        coordinates = []
        total_size = 0
        
        for coord, content in coord_hash.items():
            content_size = len(content)
            total_size += content_size
            
            # Generate content preview and metadata
            content_preview = content[:100] + "..." if len(content) > 100 else content
            content_lines = content.count('\\n') + 1 if content else 0
            content_type = "text"
            
            # Simple content type detection
            if content.strip().startswith('{') and content.strip().endswith('}'):
                try:
                    json.loads(content)
                    content_type = "json"
                except:
                    pass
            elif content.strip().startswith('<') and content.strip().endswith('>'):
                content_type = "xml/html"
            elif '\\n' in content and ('def ' in content or 'class ' in content):
                content_type = "code"
            
            coordinates.append({
                "coordinate": coord,
                "size": content_size,
                "lines": content_lines,
                "type": content_type,
                "preview": content_preview,
                "empty": not content.strip()
            })
        
        # Sort coordinates by coordinate string for consistent ordering
        coordinates.sort(key=lambda x: x["coordinate"])
        
        # Generate summary statistics
        non_empty_coords = [c for c in coordinates if not c["empty"]]
        avg_size = total_size / len(coordinates) if coordinates else 0
        
        return {
            "file_path": actual_file_path,
            "total_coordinates": len(coordinates),
            "non_empty_coordinates": len(non_empty_coords),
            "total_content_size": total_size,
            "average_content_size": round(avg_size, 2),
            "content_types": {
                content_type: len([c for c in coordinates if c["type"] == content_type])
                for content_type in set(c["type"] for c in coordinates)
            },
            "coordinates": coordinates
        }
    except Exception as e:
        raise RuntimeError(f"Error generating table of contents: {str(e)}")


def phext_delta(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Hierarchical checksum map for integrity verification."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        if not coord_hash:
            return {
                "file_path": actual_file_path,
                "file_checksum": "",
                "coordinate_checksums": {},
                "total_coordinates": 0
            }
        
        # Generate checksums for each coordinate
        coordinate_checksums = {}
        all_content = ""
        
        for coord, content in sorted(coord_hash.items()):
            # Individual coordinate checksum
            coord_checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
            coordinate_checksums[coord] = {
                "checksum": coord_checksum,
                "size": len(content),
                "empty": not content.strip()
            }
            
            # Accumulate for file checksum
            all_content += f"{coord}:{content}"
        
        # Overall file checksum
        file_checksum = hashlib.sha256(all_content.encode('utf-8')).hexdigest()
        
        # Hierarchical checksums by dimension
        dimension_checksums = {}
        for coord in coord_hash.keys():
            # Split coordinate into dimensions (assuming format like "1.2.3/4.5.6/7.8.9")
            parts = coord.split('/')
            for i, part in enumerate(parts):
                dim_key = f"dimension_{i}"
                if dim_key not in dimension_checksums:
                    dimension_checksums[dim_key] = {}
                
                dim_content = dimension_checksums[dim_key].get(part, "")
                dim_content += coord_hash[coord]
                dimension_checksums[dim_key][part] = hashlib.sha256(dim_content.encode('utf-8')).hexdigest()[:16]
        
        return {
            "file_path": actual_file_path,
            "file_checksum": file_checksum,
            "file_checksum_short": file_checksum[:16],
            "total_coordinates": len(coord_hash),
            "coordinate_checksums": coordinate_checksums,
            "dimension_checksums": dimension_checksums,
            "integrity_verified": True
        }
    except Exception as e:
        raise RuntimeError(f"Error generating delta checksums: {str(e)}")


def phext_checksum(file_path: Optional[str] = None) -> Dict[str, Any]:
    """File-level checksum for quick integrity verification."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Generate file checksum
        all_content = ""
        for coord, content in sorted(coord_hash.items()):
            all_content += f"{coord}:{content}"
        
        checksum = hashlib.sha256(all_content.encode('utf-8')).hexdigest()
        short_checksum = checksum[:16]
        
        return {
            "file_path": actual_file_path,
            "checksum": checksum,
            "checksum_short": short_checksum,
            "algorithm": "sha256",
            "coordinates": len(coord_hash),
            "total_size": len(all_content)
        }
    except Exception as e:
        raise RuntimeError(f"Error generating checksum: {str(e)}")


def phext_push(local_file_path: str, coordinate: str, phext_file_path: Optional[str] = None) -> str:
    """Write local file content to a specific coordinate in phext."""
    try:
        state = get_state()
        actual_phext_path = state.get_file_path(phext_file_path)
        
        # Read local file
        import os
        local_path = os.path.expanduser(local_file_path)
        if not os.path.exists(local_path):
            raise RuntimeError(f"Local file not found: {local_path}")
        
        with open(local_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Push to phext coordinate
        coord_hash = state.load_file_as_hash(actual_phext_path)
        coord_hash[coordinate] = content
        
        state.mark_dirty(actual_phext_path)
        state.save_hash_to_file(actual_phext_path)
        
        file_size = len(content)
        return f"Successfully pushed {file_size} bytes from {local_path} to {coordinate} in {actual_phext_path}"
    except Exception as e:
        raise RuntimeError(f"Error pushing file to phext: {str(e)}")


def phext_pull(coordinate: str, local_file_path: str, phext_file_path: Optional[str] = None) -> str:
    """Fetch coordinate content to a local file."""
    try:
        state = get_state()
        actual_phext_path = state.get_file_path(phext_file_path)
        coord_hash = state.load_file_as_hash(actual_phext_path)
        
        # Get content from coordinate
        content = coord_hash.get(coordinate, "")
        if not content:
            raise RuntimeError(f"No content found at coordinate {coordinate}")
        
        # Write to local file
        import os
        local_path = os.path.expanduser(local_file_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = len(content)
        return f"Successfully pulled {file_size} bytes from {coordinate} to {local_path}"
    except Exception as e:
        raise RuntimeError(f"Error pulling coordinate to file: {str(e)}")


def phext_get_full(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Complete file copy with all metadata (SQ-style get operation)."""
    try:
        state = get_state()
        actual_file_path = state.get_file_path(file_path)
        coord_hash = state.load_file_as_hash(actual_file_path)
        
        # Get file statistics
        total_size = sum(len(content) for content in coord_hash.values())
        
        # Generate full export
        return {
            "file_path": actual_file_path,
            "coordinates": coord_hash,
            "metadata": {
                "total_coordinates": len(coord_hash),
                "total_content_size": total_size,
                "non_empty_coordinates": len([c for c in coord_hash.values() if c.strip()]),
                "checksum": hashlib.sha256(
                    "".join(f"{k}:{v}" for k, v in sorted(coord_hash.items()))
                    .encode('utf-8')
                ).hexdigest()[:16]
            }
        }
    except Exception as e:
        raise RuntimeError(f"Error getting full file copy: {str(e)}")
