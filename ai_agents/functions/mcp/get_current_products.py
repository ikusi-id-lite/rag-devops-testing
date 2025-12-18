import os
from typing import List
from fastmcp import Client, FastMCP

async def get_current_products() -> List[str]:
  MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/sse")
  client = Client(MCP_SERVER_URL)

  async with client:
    await client.ping()

    result = await client.call_tool("get_current_products")

  return result.structured_content['result']
