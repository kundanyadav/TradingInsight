"""
news.py - Fetch and aggregate market news and macroeconomic data for the MCPClient app.
"""

import os
import requests
from typing import List, Dict, Any

NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # Add to your .env if using a paid news API

# Example free news sources (can be extended)
NEWS_SOURCES = [
    "https://newsapi.org/v2/top-headlines?country=in&category=business",
    "https://newsapi.org/v2/top-headlines?country=us&category=business",
]

MACRO_INDICATORS = {
    "India": [
        ("GDP Growth", "https://tradingeconomics.com/india/gdp-growth-annual"),
        ("Inflation", "https://tradingeconomics.com/india/inflation-cpi"),
        ("Unemployment", "https://tradingeconomics.com/india/unemployment-rate"),
        ("Interest Rate", "https://tradingeconomics.com/india/interest-rate"),
    ],
    "USA": [
        ("GDP Growth", "https://tradingeconomics.com/united-states/gdp-growth-annual"),
        ("Inflation", "https://tradingeconomics.com/united-states/inflation-cpi"),
        ("Unemployment", "https://tradingeconomics.com/united-states/unemployment-rate"),
        ("Interest Rate", "https://tradingeconomics.com/united-states/interest-rate"),
    ],
}


def fetch_news(country: str = "in", category: str = "business", max_articles: int = 10) -> List[Dict[str, Any]]:
    """Fetch top business news headlines for a country using NewsAPI."""
    if not NEWS_API_KEY:
        return [{"title": "No NEWS_API_KEY set. Please add to .env for live news."}]
    url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={NEWS_API_KEY}"
    try:
        resp = requests.get(url)
        data = resp.json()
        articles = data.get("articles", [])[:max_articles]
        return [{
            "title": a.get("title"),
            "url": a.get("url"),
            "source": a.get("source", {}).get("name"),
            "publishedAt": a.get("publishedAt"),
            "description": a.get("description"),
        } for a in articles]
    except Exception as e:
        return [{"title": f"Error fetching news: {e}"}]


def fetch_macro_indicators(country: str = "India") -> List[Dict[str, str]]:
    """Return macroeconomic indicator links for a country."""
    indicators = MACRO_INDICATORS.get(country, [])
    return [{"name": name, "url": url} for name, url in indicators]


def aggregate_news_and_macro(country: str = "India") -> Dict[str, Any]:
    """Aggregate news headlines and macro indicators for dashboard display."""
    news = fetch_news(country="in" if country == "India" else "us")
    macro = fetch_macro_indicators(country)
    return {
        "country": country,
        "news": news,
        "macro_indicators": macro
    }


if __name__ == "__main__":
    # Test fetching news and macro data
    print("India News & Macro:")
    print(aggregate_news_and_macro("India"))
    print("\nUSA News & Macro:")
    print(aggregate_news_and_macro("USA")) 