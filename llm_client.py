"""
Simplified LLM Client for handling different language model providers.
"""

import os
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class LLMClient:
    """Simplified client for handling different LLM providers."""
    
    def __init__(self, provider: str = None, model: str = None):
        """Initialize the LLM client."""
        self.provider = provider or os.getenv("LLM_MODEL", "openai")
        self.model = model or os.getenv("MODEL_NAME", "gpt-4")
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM based on the selected provider."""
        api_key = None
        
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            self.llm = ChatOpenAI(
                api_key=api_key,
                model=self.model,
                temperature=0.1,
                max_tokens=4000
            )
            
        elif self.provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
            
            self.llm = ChatOpenAI(
                api_key=api_key,
                model=self.model,
                temperature=0.1,
                max_tokens=4000,
                base_url="https://api.deepseek.com/v1"  # Adjust based on actual API
            )
            
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def generate_response(self, prompt: str, system_message: str = None) -> str:
        """Generate a response using the LLM."""
        if not self.llm:
            raise RuntimeError("LLM not initialized")
        
        try:
            messages = []
            
            if system_message:
                messages.append(SystemMessage(content=system_message))
            
            messages.append(HumanMessage(content=prompt))
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            print(f"❌ Error generating LLM response: {e}")
            return f"Error: {str(e)}"
    
    async def analyze_portfolio(self, portfolio_data: Dict, market_conditions: Dict) -> str:
        """Analyze portfolio data using LLM."""
        system_message = """You are an expert options trading analyst. 
        Provide detailed, actionable analysis with specific recommendations."""
        
        prompt = f"""
        Analyze the following portfolio and market data:
        
        PORTFOLIO DATA:
        {portfolio_data}
        
        MARKET CONDITIONS:
        {market_conditions}
        
        Provide analysis covering:
        1. Risk assessment
        2. Position recommendations
        3. Entry/exit points
        4. Risk management strategies
        """
        
        return await self.generate_response(prompt, system_message)
    
    async def analyze_market_sentiment(self, symbol: str, technical_data: Dict, 
                                     market_data: Dict, news_data: Dict) -> str:
        """Analyze market sentiment for a symbol."""
        system_message = """You are a technical analyst specializing in market sentiment analysis.
        Provide clear, data-driven insights for trading decisions."""
        
        prompt = f"""
        Analyze market sentiment for {symbol}:
        
        TECHNICAL DATA:
        {technical_data}
        
        MARKET DATA:
        {market_data}
        
        NEWS DATA:
        {news_data}
        
        Provide:
        1. Sentiment assessment (Bullish/Bearish/Neutral)
        2. Key support/resistance levels
        3. Entry/exit recommendations
        4. Risk assessment
        """
        
        return await self.generate_response(prompt, system_message)
    
    async def generate_options_strategies(self, symbol: str, market_conditions: Dict, 
                                        options_data: Dict, risk_tolerance: str) -> str:
        """Generate options trading strategies."""
        system_message = """You are an options trading strategist. 
        Generate specific, actionable options strategies with clear risk/reward profiles."""
        
        prompt = f"""
        Generate options strategies for {symbol}:
        
        MARKET CONDITIONS:
        {market_conditions}
        
        OPTIONS DATA:
        {options_data}
        
        RISK TOLERANCE:
        {risk_tolerance}
        
        Provide:
        1. Specific strategy recommendations
        2. Entry/exit points
        3. Risk/reward ratios
        4. Position sizing
        5. Hedging suggestions
        """
        
        return await self.generate_response(prompt, system_message)
    
    async def assess_risk(self, portfolio_data: Dict, market_conditions: Dict, 
                         risk_parameters: Dict) -> str:
        """Assess portfolio risk."""
        system_message = """You are a risk management specialist.
        Provide comprehensive risk assessment with specific mitigation strategies."""
        
        prompt = f"""
        Assess portfolio risk:
        
        PORTFOLIO DATA:
        {portfolio_data}
        
        MARKET CONDITIONS:
        {market_conditions}
        
        RISK PARAMETERS:
        {risk_parameters}
        
        Provide:
        1. Current risk exposure
        2. Risk factors and their impact
        3. Mitigation strategies
        4. Compliance assessment
        5. Immediate actions needed
        """
        
        return await self.generate_response(prompt, system_message)
    
    async def generate_full_context_recommendations(self, prompt: str, system_message: str = None) -> str:
        """Generate recommendations using a full context prompt (news, positions, greeks, technicals, option chains, feedback, etc.)."""
        return await self.generate_response(prompt, system_message)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current LLM model."""
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": 0.1,
            "max_tokens": 4000
        }


# Convenience function for creating LLM client
def create_llm_client(provider: str = None, model: str = None) -> LLMClient:
    """Create an LLM client with the specified configuration."""
    return LLMClient(provider=provider, model=model)


# Example usage
async def main():
    """Example usage of the LLM client."""
    try:
        client = create_llm_client()
        
        # Test basic response generation
        response = await client.generate_response(
            "What are the key factors to consider when trading options?",
            "You are an options trading expert."
        )
        print("Response:", response)
        
        # Test portfolio analysis
        portfolio_data = {"positions": [{"symbol": "NIFTY", "quantity": 100}]}
        market_conditions = {"trend": "bullish", "volatility": "high"}
        
        analysis = await client.analyze_portfolio(portfolio_data, market_conditions)
        print("Analysis:", analysis)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 