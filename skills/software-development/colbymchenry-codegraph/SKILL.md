---
name: colbymchenry-codegraph
type: skill
description: Use @colbymchenry/codegraph npm package to generate code dependency graphs.
---
# Colbymchenry Codegraph Skill

## Triggers
- User wants to visualize code dependencies, call graph, or module interactions using the @colbymchenry/codegraph npm package.
- User asks for "codegraph", "dependency graph", "call graph", or mentions @colbymchenry/codegraph.
- User encounters "codegraph (stdio) failed" errors and needs to fix MCP configuration.

## Context
This skill wraps the @colbymchenry/codegraph npm CLI tool, which provides local-first code intelligence for AI agents (MCP). It supports multiple languages via tree-sitter grammars and does not execute code.

## Steps
1. Install the package globally (or locally in project):
   ```bash
   npm install -g @colbymchenry/codegraph
   ```
   Alternatively, install locally and use npx:
   ```bash
   npm install @colbymchenry/codegraph
   npx codegraph ...
   ```

2. Navigate to the project root or target directory containing source code.

3. Initialize CodeGraph in the project (creates `.codegraph/` directory and indexes files):
   ```bash
   codegraph init .
   ```
   This scans and parses supported source files.

4. (Optional) Update the index after changes:
   ```bash
   codegraph index .
   ```
   or use `codegraph sync .` for incremental updates.

5. To inspect the index or run queries:
   - List indexed files: `codegraph files`
   - Search for symbols: `codegraph query "<search>"`
   - Show status: `codegraph status`

6. For use with Hermes Agent via MCP, start the MCP server:
   ```bash
   codegraph serve --mcp
   ```
   (The server can also be started without `--mcp` for a interactive agent configuration prompt.)

7. The MCP server provides tools such as `mcp_codegraph_explore`, `mcp_codegraph_callers`, etc., which can be used by Hermes to answer code‑graph questions.

8. (Legacy) Older versions of the tool accepted `codegraph <path>` to generate a standalone HTML graph. This mode is no longer the default; if you need a static graph, consider exporting via MCP tools or using third‑party visualization.

9. Always verify the MCP connection after configuration:
   ```bash
   hermes mcp test codegraph
   # Should show: ✓ Connected (XXXms) ✓ Tools discovered: 8
   ```

## Pitfalls
- Empty directory → empty graph. Ensure source files are present.
- Dynamic imports/reflection (e.g., `__import__()`, `require()`) may be missed because the tool does not execute code.
- Large codebases can produce overly dense graphs; use `--distance` to limit scope.
- The tool may not support certain language constructs; check output for warnings.
- Ensure Node.js >= 14 and npm are installed.
- **Command syntax changed**: In versions >= 0.9.0, the tool uses subcommands (`init`, `index`, `serve`, etc.). Running `codegraph <path>` directly is no longer supported and will yield "unknown command" errors. Always initialize first with `codegraph init <path>`.

## References
- GitHub repository: https://github.com/colbymchenry/codegraph
- npm package: https://www.npmjs.com/package/@colbymchenry/codegraph

## Example
```bash
# Generate interactive graph for current directory
codegraph . --output mygraph.html

# Static matplotlib graph for report
codegraph src/ --matplotlib --output graph.png

# Limit depth to 2 and export data
codegraph . --distance 2 --object-only | jq '.' > deps.json
```
## Hermes MCP Integration

When using @colbymchenry/codegraph with Hermes Agent via MCP, configure the MCP server in ~/.hermes/config.yaml:

```yaml
mcp_servers:
  codegraph:
    command: npx
    args:
      - "-y"
      - "@colbymchenry/codegraph"
      - "serve"
      - "--mcp"
```

**Important**: The `args` must be a YAML list with each argument as a separate item. The `-y` flag is required for npx to automatically install the package if not present globally.

See `references/mcp-configuration.md` for detailed verification steps and troubleshooting.

A ready-to-use template is available at `templates/mcp-configuration.yaml` — copy it into your Hermes config directory and adjust as needed.

After configuration, tools become available as `mcp_codegraph_*` (e.g., `mcp_codegraph_explore`, `mcp_codegraph_callers`).

**Verification**: Always test the MCP connection after configuration:
```bash
hermes mcp test codegraph
# Should show: ✓ Connected (XXXms) ✓ Tools discovered: 8
```

**Common Pitfall**: If you see "codegraph (stdio) failed" errors, double-check that:
1. The mcp_servers section exists in config.yaml
2. args is a YAML list (not a string)
3. The "-y" flag is included as a separate array item
4. You've restarted Hermes after configuration changes

---