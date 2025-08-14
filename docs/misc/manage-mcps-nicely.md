# Managing MCPs Nicely: Scope, Example, Commands

**VERIFIED** against official Anthropic documentation:
- https://docs.anthropic.com/en/docs/claude-code/mcp
- https://docs.anthropic.com/en/docs/claude-code/settings

There are three MCP installation scopes to choose from. I use "Project Scope" for my solo projects as I like the MCP config in source control. Some MCPs, like https://ref.tools/mcp, need an API Key. This guide shows one simple way to "keep your API keys in one place" (and never in source control).

## MCP installation scopes

| Scope | Command (with flag) | Where's the config? | Use Case |
|:------|:----------|:--------|:---------|
| **Local Scope**<br/>_Private to you in a **specific project**_ | `claude mcp add --scope local` | Outside project<br/>*`~/.claude.json` (not in source control)* | MCPs for a specific project, you don't care about keeping config in source control. Default scope. |
| **Project Scope**<br/>*Shared with team via source control* | `claude mcp add --scope project` | Inside project directory<br/> *`.mcp.json` (checked into source control)* | Team-shared MCPs that everyone can access OR its your project and you want config source control. |
| **User Scope**<br/>_Private to you across **all projects**_ | `claude mcp add --scope user` | Outside project<br/>*`~/.claude.json` (not in source control)* | MCPs available to all projects, you don't care about keeping config in source control. |

**Key Notes**
- **All Scopes Active**: MCPs from all three scopes (local + project + user) are available simultaneously in your project.
- **Precedence: Local (strongest) → Project → User**: When the same MCP is installed, local overrides project, project overrides user.
- **Security**: Project-scoped servers from `.mcp.json` require approval before use for security
- **Source control**: Only `.mcp.json` (project scope) should be checked into source control
- **Reset**: Use `claude mcp reset-project-choices` to reset project-scoped server approval choices

## Example: Add Ref MCP with an API Key

On https://ref.tools/mcp the installation instructions that are given will hardcode your API key into a configuration file:

```bash
claude mcp add --transport http Ref "https://api.ref.tools/mcp?apiKey=ref-4b23455555gat3434f7c"
```

**Rather than hardcoding, keep your MCP API keys in "one place":**

1. Check your shell, run: `claude` then ➜ `echo $SHELL` ➜ `exit` claude
2. Open shell settings (e.g., `cursor ~/.zshrc` or `cursor ~/.bashrc` for bash).
3. Append this to the file that opens:
   ```text
   # ⭐ MCP API keys "One Place"
   export API_KEY_MCP_REF="ref-4b23455555gat3434f7c"
   export API_KEY_MCP_ANOTHER="another-key"
   ```
4. Refresh your shell `source ~/.zshrc`
5. Verify the variable is set `echo $API_KEY_MCP_REF`.

🔥 Ensure you replace "ref-4b23455555gat3434f7c" above with your own Ref API key (the above is a dummy key)

**Add Ref MCP for all scopes using your "one place" API key:**

```bash
# Use this exactly (keep "API_KEY_MCP_REF" )
claude mcp add --scope local --transport http Ref 'https://api.ref.tools/mcp?apiKey=${API_KEY_MCP_REF}'
claude mcp add --scope project --transport http Ref 'https://api.ref.tools/mcp?apiKey=${API_KEY_MCP_REF}'
claude mcp add --scope user --transport http Ref 'https://api.ref.tools/mcp?apiKey=${API_KEY_MCP_REF}'
```

Take a look at the config files in the table. You'll see the API Key is in none of them. That's super. It means you can safely check `mcp.json` into source control. And you can easily change your API Key if you need to.

**See how precedence works: Local (strongest) → Project → User**

1. Accessible MCPs: `claude mcp list`
2. Verify Ref at Local scope: `claude mcp get Ref`
3. Remove Ref from Local scope: `claude mcp remove Ref --scope local`
4. Verify Ref now at Project scope: `claude mcp get Ref`
5. Remove Ref from Project scope: `claude mcp remove Ref --scope project`
6. Verify Ref now at User scope: `claude mcp get Ref`
7. Remove Ref from User scope: `claude mcp remove Ref --scope user`
8. Add Ref again at your preferred scope(s)
9. Open Claude Code `claude` → see your MCP(s) `/mcp`

For me, I like source control. So my MCPs are added once at Project Scope and it's always obvious what MCPs Claude Code can use for that project.