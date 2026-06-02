import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    async with streamable_http_client("http://127.0.0.1:8000/mcp/") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("tools:", [t.name for t in tools.tools])

            result = await session.call_tool("add", {"a": 1, "b": 2})
            print("add(1,2):", result)


asyncio.run(main())
