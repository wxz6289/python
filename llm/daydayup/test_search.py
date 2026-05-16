"""Test the search tool functionality."""

import asyncio
from dotenv import load_dotenv

load_dotenv()

from src.simple_agent.graph import search_tool


async def test_search():
    """Test the search tool with a sample query."""
    print("Testing MySearchTool...")
    print("=" * 60)
    
    # Test query
    query = "Python programming language"
    print(f"\nQuery: {query}\n")
    
    # Run the search
    result = search_tool.run(query)
    print("Search Results:")
    print("-" * 60)
    print(result)
    print("-" * 60)
    
    print("\n✅ Search tool test completed!")


if __name__ == "__main__":
    asyncio.run(test_search())
