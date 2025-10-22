@echo off
REM ============================================================================
REM MCP Development Environment Setup for Windows
REM Self-contained setup - no external files needed
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo MCP Development Environment Setup
echo ============================================================================
echo.

REM Check if uv is installed
echo [1/5] Checking for uv installation...
uv --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv is not installed or not in PATH
    echo Please install uv from https://docs.astral.sh/uv/
    pause
    exit /b 1
)
echo ✓ uv found:
uv --version
echo.

REM Create virtual environment with Python 3.13
echo [2/5] Creating virtual environment with Python 3.13...
if exist .venv (
    echo Virtual environment already exists at .venv
    set /p replace="Replace it? (y/n): "
    if /i "!replace!"=="y" (
        echo Removing old virtual environment...
        rmdir /s /q .venv
        uv venv --python 3.13
    ) else (
        echo Keeping existing virtual environment
    )
) else (
    uv venv --python 3.13
)
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment ready
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated
echo.

REM Install MCP servers
echo [4/5] Installing MCP servers...
echo Installing:
echo   - mcp-server-git (Git operations)
echo   - mcp-server-shell (Command execution)
echo   - filesystem-operations-mcp (File navigation/search)
echo   - mcp-server-fetch (HTTP fetch)
echo.
uv pip install mcp-server-git mcp-server-shell filesystem-operations-mcp mcp-server-fetch
if errorlevel 1 (
    echo ERROR: Failed to install MCP servers
    pause
    exit /b 1
)
echo ✓ MCP servers installed
echo.

REM Verify installations
echo [5/5] Verifying MCP server installations...
echo.

set /a pass_count=0
set /a total_count=4

echo Testing mcp-server-git...
uv run mcp-server-git --help >nul 2>&1
if errorlevel 1 (
    echo ✗ mcp-server-git test FAILED
) else (
    echo ✓ mcp-server-git OK
    set /a pass_count+=1
)

echo Testing mcp-server-shell...
uv run mcp-server-shell --help >nul 2>&1
if errorlevel 1 (
    echo ✗ mcp-server-shell test FAILED
) else (
    echo ✓ mcp-server-shell OK
    set /a pass_count+=1
)

echo Testing filesystem-operations-mcp...
uv run filesystem-operations-mcp --help >nul 2>&1
if errorlevel 1 (
    echo ✗ filesystem-operations-mcp test FAILED
) else (
    echo ✓ filesystem-operations-mcp OK
    set /a pass_count+=1
)

echo Testing mcp-server-fetch...
uv run mcp-server-fetch --help >nul 2>&1
if errorlevel 1 (
    echo ✗ mcp-server-fetch test FAILED
) else (
    echo ✓ mcp-server-fetch OK
    set /a pass_count+=1
)

echo.
echo ============================================================================
echo Setup Complete! [!pass_count!/!total_count! servers verified]
echo ============================================================================
echo.
echo NEXT STEPS - Configure Claude Desktop:
echo.
echo 1. Open Claude Desktop settings
echo 2. Go to Developer section
echo 3. Click "Edit Config" to open claude_desktop_config.json
echo 4. Add the following configuration:
echo.
echo {
echo   "mcpServers": {
echo     "git": {
echo       "command": "uvx",
echo       "args": ["--python", "3.13", "mcp-server-git"]
echo     },
echo     "shell": {
echo       "command": "uvx",
echo       "args": ["--python", "3.13", "mcp-server-shell", "D:/source/digits/projects"]
echo     },
echo     "filesystem": {
echo       "command": "uvx",
echo       "args": ["--python", "3.13", "filesystem-operations-mcp", "--root-dir", "D:/source/digits/projects"]
echo     },
echo     "fetch": {
echo       "command": "uvx",
echo       "args": ["--python", "3.13", "mcp-server-fetch"]
echo     }
echo   }
echo }
echo.
echo 5. Restart Claude Desktop
echo.
echo ACTIVATE ENVIRONMENT IN FUTURE:
echo   .venv\Scripts\activate.bat
echo.
echo DEACTIVATE:
echo   deactivate
echo.
pause