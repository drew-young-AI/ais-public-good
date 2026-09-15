# Codegraph MCP Configuration Reference

## Working Configuration (as verified 2026-06-04)

```yaml
mcp_servers:
  codegraph:
    command: npx
    args:
      - "-y"
      - "@colbymchenry/codegraph"
      - "serve"
      - "--mcp"
    timeout: 120
```

## Verification Steps

1. Test MCP server connection:
   ```bash
   hermes mcp test codegraph
   ```
   Expected output: ✓ Connected (XXXms) ✓ Tools discovered: 8

2. List available MCP tools:
   ```bash
   hermes mcp list
   ```
   Should show codegraph with all tools enabled

3. Common pitfalls to avoid:
   - ❌ Using a string for args instead of a YAML list
   - ❌ Missing the "-y" flag (causes npx to fail if package not globally installed)
   - ❌ Incorrect ordering of arguments
   - ❌ Forgetting the "--mcp" flag

## Troubleshooting

If tools are not appearing after configuration:

1. Check Hermes logs for MCP registration errors:
   ```bash
   grep -i mcp ~/.hermes/logs/hermes.log | tail -20
   ```

2. Verify the npx command works directly:
   ```bash
   timeout 10 npx @colbymchenry/codegraph serve --mcp
   ```
   Should show no output and exit with code 0 when ready

3. Ensure Node.js >= 14 and npm are installed:
   ```bash
   node --version
   npm --version
   ```