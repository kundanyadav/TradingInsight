"""
Simplified MCP Client for connecting to the kiteMCP server.
"""

import asyncio
from typing import Dict, Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """Simplified client for connecting to the kiteMCP server."""
    
    def __init__(self):
        """Initialize the MCP client."""
        self.session: Optional[ClientSession] = None
        self.tools: List[Dict] = []
        self.prompts: List[Dict] = []
        self.resources: List[Dict] = []
    
    async def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            # For stdio transport, we need to start the server process
            server_params = StdioServerParameters(
                command="python",
                args=["../MCPServer/mcp_server.py"]
            )
            
            self.session = await stdio_client(server_params)
            
            # Initialize the session
            await self.session.initialize()
            
            # Get available tools, prompts, and resources
            await self._discover_capabilities()
            
            print("✅ Connected to kiteMCP server successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to MCP server: {e}")
            return False
    
    async def _discover_capabilities(self):
        """Discover available tools, prompts, and resources."""
        try:
            # Get tools
            tools_response = await self.session.list_tools()
            self.tools = tools_response.tools
            
            # Get prompts
            prompts_response = await self.session.list_prompts()
            self.prompts = prompts_response.prompts
            
            # Get resources
            resources_response = await self.session.list_resources()
            self.resources = resources_response.resources
            
            print(f"📋 Discovered {len(self.tools)} tools, {len(self.prompts)} prompts, {len(self.resources)} resources")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not discover all capabilities: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            # Find the tool
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if not tool:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            # Call the tool
            result = await self.session.call_tool(tool_name, arguments or {})
            return result.content
            
        except Exception as e:
            print(f"❌ Error calling tool '{tool_name}': {e}")
            return {"error": str(e)}
    
    async def get_prompt(self, prompt_name: str, arguments: Dict[str, Any] = None) -> str:
        """Get a prompt from the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            # Find the prompt
            prompt = next((p for p in self.prompts if p.name == prompt_name), None)
            if not prompt:
                raise ValueError(f"Prompt '{prompt_name}' not found")
            
            # Get the prompt
            result = await self.session.read_prompt(prompt_name, arguments or {})
            return result.content
            
        except Exception as e:
            print(f"❌ Error getting prompt '{prompt_name}': {e}")
            return f"Error: {str(e)}"
    
    async def get_resource(self, resource_uri: str) -> str:
        """Get a resource from the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            # Find the resource
            resource = next((r for r in self.resources if r.uri == resource_uri), None)
            if not resource:
                raise ValueError(f"Resource '{resource_uri}' not found")
            
            # Get the resource
            result = await self.session.read_resource(resource_uri)
            return result.contents
            
        except Exception as e:
            print(f"❌ Error getting resource '{resource_uri}': {e}")
            return f"Error: {str(e)}"
    
    # Portfolio methods
    async def get_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio positions."""
        return await self.call_tool("get_portfolio")
    
    async def get_market_indicators(self, symbol: str) -> Dict[str, Any]:
        """Get market indicators for a symbol."""
        return await self.call_tool("get_market_indicators", {"symbol": symbol})
    
    async def get_option_chain(self, symbol: str) -> Dict[str, Any]:
        """Get option chain data for a symbol."""
        return await self.call_tool("get_option_chain", {"symbol": symbol})
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get latest quote for a symbol."""
        return await self.call_tool("get_quote", {"symbol": symbol})
    
    async def get_news(self, symbol: str) -> Dict[str, Any]:
        """Get news for a symbol."""
        return await self.call_tool("get_news", {"symbol": symbol})
    
    async def get_sentiment(self, symbol: str = None) -> Dict[str, Any]:
        """Get market sentiment."""
        return await self.call_tool("get_sentiment", {"symbol": symbol})
    
    # Prompt methods
    async def get_portfolio_analysis_prompt(self, symbol: str = None, timeframe: str = "1d") -> str:
        """Get portfolio analysis prompt."""
        return await self.get_prompt("portfolio_analysis", {
            "symbol": symbol,
            "timeframe": timeframe
        })
    
    async def get_market_sentiment_prompt(self, symbol: str, indicator: str = "EMA") -> str:
        """Get market sentiment prompt."""
        return await self.get_prompt("market_sentiment", {
            "symbol": symbol,
            "indicator": indicator
        })
    
    async def get_options_strategy_prompt(self, symbol: str, strategy_type: str = "neutral") -> str:
        """Get options strategy prompt."""
        return await self.get_prompt("options_strategy", {
            "symbol": symbol,
            "strategy_type": strategy_type
        })
    
    async def get_risk_assessment_prompt(self, portfolio_value: float = None) -> str:
        """Get risk assessment prompt."""
        return await self.get_prompt("risk_assessment", {
            "portfolio_value": portfolio_value
        })
    
    # Resource methods
    async def get_nifty50_data(self) -> str:
        """Get NIFTY 50 market data."""
        return await self.get_resource("market://nifty50")
    
    async def get_banknifty_data(self) -> str:
        """Get Bank NIFTY market data."""
        return await self.get_resource("market://banknifty")
    
    async def get_options_basics(self) -> str:
        """Get options trading basics."""
        return await self.get_resource("knowledge://options_basics")
    
    async def get_greeks_knowledge(self) -> str:
        """Get options Greeks knowledge."""
        return await self.get_resource("knowledge://greeks")
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool.name for tool in self.tools]
    
    def get_available_prompts(self) -> List[str]:
        """Get list of available prompt names."""
        return [prompt.name for prompt in self.prompts]
    
    def get_available_resources(self) -> List[str]:
        """Get list of available resource URIs."""
        return [resource.uri for resource in self.resources]
    
    async def close(self):
        """Close the MCP client connection."""
        if self.session:
            await self.session.close()
            print("🔌 Disconnected from kiteMCP server")


# Convenience function for creating and connecting to MCP client
async def create_mcp_client() -> MCPClient:
    """Create and connect to an MCP client."""
    client = MCPClient()
    success = await client.connect()
    if not success:
        raise RuntimeError("Failed to connect to MCP server")
    return client


# Example usage
async def main():
    """Example usage of the MCP client."""
    try:
        client = await create_mcp_client()
        
        # Get portfolio
        portfolio = await client.get_portfolio()
        print("Portfolio:", portfolio)
        
        # Get market indicators
        indicators = await client.get_market_indicators("NIFTY")
        print("Indicators:", indicators)
        
        # Get a prompt
        prompt = await client.get_portfolio_analysis_prompt()
        print("Prompt:", prompt[:100] + "...")
        
        # Get a resource
        resource = await client.get_nifty50_data()
        print("Resource:", resource[:100] + "...")
        
        await client.close()
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 