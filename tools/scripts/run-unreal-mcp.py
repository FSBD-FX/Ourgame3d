"""Run the pinned upstream MCP module with project-local logs and no duplicate import."""
import os
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[2]
SOURCE = PROJECT / "tools" / "unreal-mcp"
RUNTIME = PROJECT / "tools" / "runtime" / "unreal-mcp"
EXPECTED_COMMIT = "4e5f00da50733190481311e254d16d137a84ef33"
# The prepared checkout is detached. Reading HEAD avoids a GUI client's PATH
# dependency on git.exe and refuses a later switch back to a moving branch.
actual_commit = (SOURCE / ".git" / "HEAD").read_text(encoding="ascii").strip()
if actual_commit != EXPECTED_COMMIT:
    raise RuntimeError(f"Unreal MCP checkout changed: expected {EXPECTED_COMMIT}, got {actual_commit}")

log_directory = RUNTIME / "logs"
log_directory.mkdir(parents=True, exist_ok=True)
os.chdir(log_directory)
sys.path.insert(0, str(SOURCE / "Python"))
import unreal_mcp_server

if unreal_mcp_server.UNREAL_HOST != "127.0.0.1" or unreal_mcp_server.UNREAL_PORT != 55557:
    raise RuntimeError("The pinned Unreal MCP loopback endpoint changed.")
unreal_mcp_server.mcp.run(transport="stdio")
