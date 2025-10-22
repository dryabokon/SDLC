from mcp.server.fastmcp import FastMCP
app = FastMCP("demo-fastmcp")
#---------------------------------------------------------------------------------------------------------------------
@app.tool(description="Echoes back the same text you send.")
def echo(message: str) -> str:
    return f"Echo: {message}"
#---------------------------------------------------------------------------------------------------------------------
@app.tool(description="Adds two numbers and returns the sum.")
def add(a: float, b: float) -> float:
    return a + b
#---------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run()
