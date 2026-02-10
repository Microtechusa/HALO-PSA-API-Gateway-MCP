#!/usr/bin/env python3
"""HaloPSA API Gateway MCP Server — Main Entry Point"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_gateway.server import main

if __name__ == "__main__":
    main()
