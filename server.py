# from mcp.server.sse import SseServerTransport
# from starlette.applications import Starlette
# from starlette.routing import Route
# from mcp.server import Server

# app = Server("example-server")
# sse = SseServerTransport("/messages/")

# @app.call_tool()
# async def add_numbers(a: int, b: int) -> str:
#     """Add two numbers together and return the result.
    
#     Args:
#         a: First number
#         b: Second number
        
#     Returns:
#         The sum of the two numbers
#     """
#     return f"addition is fun! ${a + b}"

# async def handle_sse(scope, receive, send):
#     async with sse.connect_sse(scope, receive, send) as streams:
#         await app.run(streams[0], streams[1], app.create_initialization_options())

# async def handle_messages(scope, receive, send):
#     await sse.handle_post_message(scope, receive, send)

# starlette_app = Starlette(
#     debug=True,
#     routes=[
#         Route("/sse", endpoint=handle_sse),
#         Route("/messages/", endpoint=handle_messages, methods=["POST"]),
#     ]
# )

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(starlette_app, host="0.0.0.0", port=8000)



from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route,Mount
from mcp.server import Server
import mcp.types as types
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG,filename="server.log", filemode="w",)
logger = logging.getLogger(__name__)

app = Server("example-server")
sse = SseServerTransport("/messages/")

@app.call_tool()
async def get_red_value(a: int) -> str:
    """get the red value of a given integer.
    
    Args:
        a: number
        
    Returns:
        A message with the red value of the number
    """
    # logger.info(f"Adding numbers: {a} + {b}")
    return f"red value is is fun! ${a + 50}"

@app.call_tool()
async def greet(name: str) -> str:
    """Greet the user with their name.
    
    Args:
        name: The name of the user
        
    Returns:
        A greeting message
    """
    logger.info(f"Greeting user: {name}")
    return f"Hello pissu kollooo, {name}!"

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    logger.debug("Listing available tools.")
    return [
        types.Tool(
            name="get_red_value",  # This should match your function name
            description="Get the red value of a given integer",
            inputSchema={
                "type": "object",
                "required": ["a"],
                "properties": {
                    "a": {
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
        await sse.handle_post_message(request.scope,request.receive, request._send)
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
        # Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on port 8000")
    uvicorn.run(starlette_app, host="0.0.0.0", port=8000, log_level="debug")