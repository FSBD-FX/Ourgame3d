# Upstream and local preparation changes

- Source: https://github.com/chongdashu/unreal-mcp
- Commit: `4e5f00da50733190481311e254d16d137a84ef33`
- Original plugin path: `MCPGameProject/Plugins/UnrealMCP`
- Copied to the project on 2026-10-10 for local connectivity testing.
- Upstream README declares MIT, but the checked-out tree has no standalone LICENSE file. This note does not substitute for a license grant.

Local fixes in `MCPServerRunnable.cpp`: both receive buffers reserve an extra byte for the null terminator; both response send paths use the UTF-8 byte length rather than FString's TCHAR length. These changes are limited to the project copy. The upstream checkout is unchanged.

The bridge binds TCP `127.0.0.1:55557`. It has no authentication and should remain on the local loopback interface.
