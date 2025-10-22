# Claude Desktop Tools - Complete Prompts Guide

## Filesystem Tools Prompts with Payloads

### 1. Explore Project Structure
```
Get the directory structure of demo_onnx at depth 2.
```
**Payload:**
```json
{
  "depth": 2,
  "path": "demo_onnx"
}
```
**Successful Completion:** Returns folders like `demo_onnx/runtime_cpp`, `demo_onnx/runtime_python`

---

### 2. List Files in Directory
```
Show me all files in demo_onnx directory.
```
**Payload:**
```json
{
  "paths": ["demo_onnx"]
}
```
**Successful Completion:**
```json
{
  "demo_onnx\\Dockerfile": {"size": 3142, "type": "code"},
  "demo_onnx\\pyproject.toml": {"size": 253, "type": "data"},
  "demo_onnx\\uv.lock": {"size": 393900, "type": "text"}
}
```

---

### 3. Read File Contents
```
Read the pyproject.toml file from demo_onnx.
```
**Payload:**
```json
{
  "paths": ["demo_onnx/pyproject.toml"],
  "start": 1,
  "count": 50
}
```
**Successful Completion:** Returns the file content with all lines readable

---

### 4. Search for Text in Files
```
Search for all TODO comments in demo_onnx Python files.
```
**Payload:**
```json
{
  "patterns": ["TODO"],
  "included_globs": ["demo_onnx/**/*.py"],
  "max_depth": 3,
  "max_results": 10
}
```
**Successful Completion:** Returns all files and lines containing "TODO"

---

### 5. Find Specific Files
```
Find all .onnx model files in demo_onnx.
```
**Payload:**
```json
{
  "included_globs": ["demo_onnx/**/*.onnx"],
  "max_depth": 3,
  "max_results": 20
}
```
**Successful Completion:**
```json
{
  "demo_onnx/runtime_cpp/yolov8n.onnx": {"size": 12836439, "type": "unknown"},
  "demo_onnx/runtime_python/yolov8n.onnx": {"size": 12836439, "type": "unknown"}
}
```

---

### 6. Read Multiple Files
```
Read both inference.cpp and inference.h from demo_onnx/runtime_cpp.
```
**Payload:**
```json
{
  "paths": ["demo_onnx/runtime_cpp/inference.cpp", "demo_onnx/runtime_cpp/inference.h"],
  "start": 1,
  "count": 100
}
```
**Successful Completion:** Returns contents of both files

---

### 7. Create New File
```
Create a new requirements.txt file in demo_onnx.
```
**Payload:**
```json
{
  "path": "demo_onnx/requirements.txt",
  "content": [
    "opencv-python>=4.8.0",
    "numpy>=1.24.0",
    "onnxruntime>=1.16.0",
    "Pillow>=9.5.0"
  ]
}
```
**Successful Completion:** File created at `demo_onnx/requirements.txt`

---

### 8. Replace File Content
```
Replace the content of demo_onnx/pyproject.toml with updated version.
```
**Payload:**
```json
{
  "path": "demo_onnx/pyproject.toml",
  "content": [
    "[project]",
    "name = \"demo-onnx\"",
    "version = \"0.2.0\"",
    "description = \"ONNX Runtime YOLO V8 inference demo\""
  ]
}
```
**Successful Completion:** File updated successfully

---

### 9. Append Lines to File
```
Add a new section to the end of demo_onnx/README.md.
```
**Payload:**
```json
{
  "path": "demo_onnx/README.md",
  "content": [
    "",
    "## Recent Updates",
    "- Fixed CUDA compatibility",
    "- Improved inference speed by 15%"
  ]
}
```
**Successful Completion:** Lines appended to file

---

### 10. Delete Lines from File
```
Remove deprecated functions from demo_onnx/runtime_python/ex_27_YOLO_onnx.py.
```
**Payload:**
```json
{
  "path": "demo_onnx/runtime_python/ex_27_YOLO_onnx.py",
  "line_numbers": [5, 6, 7, 8]
}
```
**Successful Completion:** Lines 5-8 deleted

---

### 11. Replace Specific Lines
```
Update the function definition in inference.cpp.
```
**Payload:**
```json
{
  "path": "demo_onnx/runtime_cpp/inference.cpp",
  "start_line_number": 45,
  "current_lines": [
    "void YOLO_V8::PreProcess(cv::Mat& image) {",
    "    // old implementation"
  ],
  "new_lines": [
    "void YOLO_V8::PreProcess(cv::Mat& image) {",
    "    // new optimized implementation",
    "    cv::resize(image, image, cv::Size(640, 640));"
  ]
}
```
**Successful Completion:** Lines 45-46 replaced with new content

---

### 12. Insert Lines into File
```
Add import statements to the top of ex_27_YOLO_onnx.py.
```
**Payload:**
```json
{
  "path": "demo_onnx/runtime_python/ex_27_YOLO_onnx.py",
  "start_line_number": 1,
  "before_or_after": "after",
  "current_line": "import cv2",
  "insert_lines": [
    "import logging",
    "from pathlib import Path"
  ]
}
```
**Successful Completion:** New imports added after line 1

---

### 13. Create New Directory
```
Create a new directory for test outputs in demo_onnx.
```
**Payload:**
```json
{
  "path": "demo_onnx/test_outputs"
}
```
**Successful Completion:** Directory created at `demo_onnx/test_outputs`

---

### 14. Delete Directory
```
Delete the temporary build folder in demo_onnx/runtime_cpp.
```
**Payload:**
```json
{
  "path": "demo_onnx/runtime_cpp/build",
  "recursive": true
}
```
**Successful Completion:** Directory and all contents deleted

---

## GitHub Tools Prompts with Payloads

### 15. Get Repository Info
```
Get information about dryabokon/tools repository.
```
**Payload:**
```json
{
  "repo": "dryabokon/tools"
}
```
**Successful Completion:**
```json
{
  "full_name": "dryabokon/tools",
  "description": "Dependencies for other projects in my repository",
  "stars": 2,
  "forks": 3,
  "open_issues": 0,
  "language": "Python"
}
```

---

### 16. Read Repository README
```
Get the README from dryabokon/tools.
```
**Payload:**
```json
{
  "repo": "dryabokon/tools",
  "ref": null
}
```
**Successful Completion:** Returns README.md content

---

### 17. List Repository Files
```
List all files in dryabokon/tools at root level.
```
**Payload:**
```json
{
  "repo": "dryabokon/tools",
  "path": "",
  "ref": null
}
```
**Successful Completion:** Returns list of all files and directories

---

### 18. Get Specific File
```
Get the content of tools_image.py from dryabokon/tools.
```
**Payload:**
```json
{
  "repo": "dryabokon/tools",
  "path": "tools_image.py",
  "ref": null
}
```
**Successful Completion:** Returns file content

---

### 19. List Open Issues
```
Show all open issues in dryabokon/tools.
```
**Payload:**
```json
{
  "repo": "dryabokon/tools",
  "state": "open"
}
```
**Successful Completion:** Returns list of open issues

---

### 20. List Pull Requests
```
Show all closed pull requests in dryabokon/tools.
```
**Payload:**
```json
{
  "repo": "dryabokon/tools",
  "state": "closed"
}
```
**Successful Completion:** Returns list of pull requests

---

## Combined Workflow Prompts

### 21. Complete Project Analysis Workflow
```
Analyze demo_onnx project:
1. List all Python files
2. Read main entry point
3. Identify code issues
4. Suggest improvements
```
**Step 1 Payload:**
```json
{
  "included_globs": ["demo_onnx/**/*.py"],
  "max_depth": 3
}
```

---

### 22. Create Documentation Workflow
```
1. Get demo_onnx structure
2. Read all key files
3. Create comprehensive README
4. Save it to demo_onnx/README_NEW.md
```

---

## Tips for Using These Prompts

1. **Copy and Paste:** Copy any prompt directly and paste into the chat
2. **Customize:** Replace example paths (demo_onnx, dryabokon/tools) with your own
3. **Combine:** Mix prompts to create custom workflows
4. **Reference:** Keep this file open for quick lookup

---

Generated: October 17, 2025
Claude Desktop Tools Guide - All Prompts with Successful Payloads