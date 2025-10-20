#!/usr/bin/env python3
import json, subprocess, sys, os, traceback

class Shell:
    def __init__(self):
        self.root = os.environ.get('MCP_ROOT_DIR', 'D:/source/digits')

    def send(self, msg):
        print(json.dumps(msg), flush=True)

    def run(self):
        while True:
            try:
                line = sys.stdin.readline()
                if not line: break
                req = json.loads(line)
                rid, method, params = req.get('id'), req.get('method'), req.get('params', {})
                
                if method == 'initialize':
                    self.send({'jsonrpc': '2.0', 'id': rid, 'result': {'protocolVersion': '2025-06-18', 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'shell-exec', 'version': '1.0'}}})
                
                elif method == 'tools/list':
                    self.send({'jsonrpc': '2.0', 'id': rid, 'result': {'tools': [
                        {'name': 'execute_command', 'description': 'Execute shell command', 'inputSchema': {'type': 'object', 'properties': {'command': {'type': 'string', 'description': 'Command to execute'}, 'cwd': {'type': 'string', 'description': 'Working directory'}}, 'required': ['command']}}
                    ]}})
                
                elif method == 'tools/call':
                    tool = params.get('name')
                    args = params.get('arguments', {})
                    cmd = args.get('command')
                    cwd = args.get('cwd', self.root)
                    
                    try:
                        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=300)
                        text = f'Exit Code: {r.returncode}\n\nSTDOUT:\n{r.stdout}\n\nSTDERR:\n{r.stderr}'
                    except subprocess.TimeoutExpired:
                        text = 'Error: Command timeout (5 minutes)'
                    except Exception as e:
                        text = f'Error: {str(e)}'
                    
                    self.send({'jsonrpc': '2.0', 'id': rid, 'result': {'type': 'tool_result', 'content': [{'type': 'text', 'text': text}]}})
                
                elif rid is None:
                    pass
                
                else:
                    self.send({'jsonrpc': '2.0', 'id': rid, 'error': {'code': -32601, 'message': 'Not found'}})
            except Exception as e:
                self.send({'jsonrpc': '2.0', 'error': {'code': -32603, 'message': str(e)}})  

if __name__ == '__main__':
    Shell().run()