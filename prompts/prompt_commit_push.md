# Commit and Push Workflow

## Step 1: Check Status

```javascript
git:git_status({
  repo_path: "D:\\source\\digits\\a_demo_codebase\\"
})
```

View modified and untracked files to see what needs to be committed.

## Step 2: Stage Changes

```javascript
git:git_add({
  files: ["src/main.py"],
  repo_path: "D:\\source\\digits\\a_demo_codebase\\"
})
```

Add specific files to the staging area. Can add multiple files:
```javascript
files: ["file1.py", "file2.py", "config.json"]
```

## Step 3: Commit

```javascript
git:git_commit({
  message: "Your commit message here",
  repo_path: "D:\\source\\digits\\a_demo_codebase\\"
})
```

Creates a commit with your message. Returns a commit hash for verification.

## Step 4: Push to Remote

```javascript
shell:execute_command({
  command: "cd D:\\source\\digits\\a_demo_codebase\\ && git push"
})
```

Pushes committed changes to the remote repository. Runs as a background process and returns a Process ID.

## Step 5: Verify Push Completed

```javascript
shell:get_process_output({
  process_id: "<ID_from_step_4>"
})
```

Check the output for success confirmation. Look for:
- `Return code: 0` (success)
- Status: `completed`

## Quick Template

1. `git_status()` > check what changed
2. `git_add(files=[...])` > stage files
3. `git_commit(message="...")` > create commit
4. `shell_execute_command("git push")` > push to remote
5. `shell_get_process_output()` > verify success

## Common Issues

- **Nothing to commit**: Make sure files are staged with `git_add()`
- **Push still running**: Wait a few seconds and check status/output again
- **Return code not 0**: Check for authentication or remote errors in output