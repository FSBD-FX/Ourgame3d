"""Use this project's Python environment without a copied Windows launcher."""
from pathlib import Path
import sys

project = Path(__file__).resolve().parents[2]
expected = project / 'tools/runtime/blender-mcp/.venv'
if Path(sys.prefix).resolve() != expected.resolve():
    raise RuntimeError(f'Use the project Blender MCP Python environment: {expected}')

from blender_mcp.server import main

if __name__ == '__main__':
    main()
