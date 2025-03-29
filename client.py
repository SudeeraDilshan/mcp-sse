import asyncio
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from agent import Agent
from mcp.client.session import ClientSession
import traceback

async def main():
    try:
        async with sse_client("http://localhost:8000/sse") as streams:
         async with ClientSession(streams[0], streams[1]) as session:
             await session.initialize()
             # Here you can add more client-side logic as needed
             # For example: await session.send_request("someMethod", {})
             mcp_tools = await load_mcp_tools(session)
            #  print(f"Loaded MCP tools: {mcp_tools}")
             agent = Agent(mcp_tools=mcp_tools)  # Initialize the agent with MCP tools
             await agent.run_interactive()
             
    except Exception as e:
        traceback.print_exc()
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(main())