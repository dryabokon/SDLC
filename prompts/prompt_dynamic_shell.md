# Running Batch Files - Quick Instruction

When executing a batch file, always change to its directory first:

```bash
cd <script_directory> && <script_name>.bat
```

**Why:** Batch files with relative paths (like `mkdir output`) need to run from their own directory to work correctly.

**Example:**
```bash
cd D:\source\digits\a_demo_codebase\ && simple.bat
```


# Running Batch Files - Complete Workflow

## 1. Execute from correct directory
```bash
cd <script_directory> && <script_name>.bat
```

**Why:** Batch files with relative paths need to run from their own directory.

**Example:**
```bash
cd D:\source\digits\a_demo_codebase\ && run_me.bat
```

## 2. Wait for completion
Check status until `Status: completed`:
```bash
get_process_status(<process_id>)
```

Look for:
- `Status: completed`
- `Return code: 0` (success)

## 3. View full log output
Get the full output (including truncated parts):
```bash
get_process_output(<process_id>, max_lines=500)
```

Or read the log file directly:
```bash
type C:\Users\acer\.config\mcp-shell-server\logs\<process_id>.log
```

## Quick Reference
1. Run: `cd <dir> && <script>.bat`
2. Wait: Check `get_process_status()` until completed
3. View: Use `get_process_output(max_lines=500)` for full output