from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from mcp.server import Server
import mcp.types as types
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename="server.log", filemode="w")
logger = logging.getLogger(__name__)

app = Server("example-server")
sse = SseServerTransport("/messages/")

@app.call_tool()
async def get_red_value(
    name: str, arguments: dict
) -> list[types.TextContent]:
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    if name != "get_red_value":
        logger.error(f"Unknown tool: {name}")
        raise ValueError(f"Unknown tool: {name}")
    if "number" not in arguments:
        logger.error("Missing required argument 'number'")
        raise ValueError("Missing required argument 'number'")
    
    number = arguments["number"]
    logger.info(f"Calculating red value for: {number}")
    return [types.TextContent(type="text", text=f"red value is fun! ${number + 50}")]

@app.call_tool()
async def greet(
    name: str, arguments: dict
) -> list[types.TextContent]:
    """Greet the user with their name.
    
    Args:
        name: The name of the tool
        arguments: Dictionary containing the arguments for the tool
        
    Returns:
        A list containing a greeting message as TextContent
    """
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    if name != "greet":
        logger.error(f"Unknown tool: {name}")
        raise ValueError(f"Unknown tool: {name}")
    if "name" not in arguments:
        logger.error("Missing required argument 'name'")
        raise ValueError("Missing required argument 'name'")
    
    user_name = arguments["name"]
    logger.info(f"Greeting user: {user_name}")
    return [types.TextContent(type="text", text=f"Hello, {user_name}! Welcome to the server.")]

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    logger.debug("Listing available tools.")
    return [
        types.Tool(
            name="get_red_value",  # This should match your function name
            description="Get the red value of a given number",
            inputSchema={
                "type": "object",
                "required": ["number"],
                "properties": {
                    "number": {
                        "type": "integer",
                        "description": "The number to get the red value for",
                    }
                },
            },
        ),
        types.Tool(
            name="greet",
            description="Greet the user with their name",
            inputSchema={
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the user",
                    }
                },
            },
        ),
    ]
        

async def handle_sse(request):
    try:
        logger.debug(f"Handling new SSE connection from: {request.client}")
        logger.info("SSE connection attempt received")
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            logger.info("SSE connection established successfully")
            await app.run(streams[0], streams[1], app.create_initialization_options())
    except Exception as e:
        logger.error(f"Error in SSE connection: {e}", exc_info=True)
        # We still need to handle the error properly here

async def handle_messages(request):
    try:
        logger.info("Message received")
        await sse.handle_post_message(request.scope, request.receive, request._send)
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

middleware = [
    Middleware(CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"])
]

starlette_app = Starlette(
    debug=True,
    middleware=middleware,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ]
)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on port 8000")
    uvicorn.run(starlette_app, host="0.0.0.0", port=8000, log_level="debug")