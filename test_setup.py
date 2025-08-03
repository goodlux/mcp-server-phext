#!/usr/bin/env python3
"""Test script to verify the MCP server works."""

import sys
import os

# Add the src directory to the path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from mcp_server_phext import create_server
    print("✅ Successfully imported create_server")
    
    # Try to create a server
    server = create_server()
    print("✅ Successfully created MCP server")
    print(f"   Server name: {server.name}")
    
    # Try importing phext directly
    from phext.phext import Phext
    from phext.coordinate import Coordinate
    print("✅ Successfully imported phext modules")
    
    # Test basic phext functionality
    phext = Phext()
    coord = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
    print(f"✅ Successfully created coordinate: {coord}")
    
    print("\\n🎉 All tests passed! MCP server is ready to use.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
