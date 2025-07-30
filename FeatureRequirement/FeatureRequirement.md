# Project Intoduction
    We want to build the Kite trading recommendation app, the app is not a typical trading app. the objective is not for the app to place trades but it's look at the portfolio current situation and then combine it with market conditions, news and other extenal factors to identify the profitable opportunities and make profits while managing the risk/reward equation, ROI, margin and cash management, and portfolio diversification.

    This app is for trading in Indian stock markets.


# App components and architecture
    I want this app to have below key component/engines:
    1. MCP Server for interacting with Kite to get below data:
        - Portfolio information (margins, cash etc) and current positions, option chain and other trading related live data.
        - API's to get stock news, financial results and web search access.
    2. Market analyst agent: 
        - This is an LLM based engine which can use MCP server to research and form a sentiment/mood (how likely is it for something to go up or down). This agent needs to take the role of a seasoned professional equity research analyst with years of experience in financial markets.
        - It needs to be able to do the research for either a requsted stock, sector (nifty, banking, auto, IT etc) or whole market and base it's research on having a short term (less than 1 month) and medium term (1-3 months) time horizon. 
        - It should always consider wider market sentiment, stock specific and sector sentiment while forming the overall sentiment/mood.
        - while researching for any specific stock please looks at their
            - quarterly financial results and analyse them to see trend and immidiate effect also compare it to market/street expectations as this highly impacts stock movement in following few days after the results are announced. 
            - Do a web search to find relevant news on the stock, sector or news that might impact overall market.
            - consider other factors that equity analysts do for making an openion.
        - Self access your sentiment openion to improve iteratively. 
        - when returning your sentiment/mood analysis response be very clear and provide short summary and also include how confident your are in your openion/sentiment. 
        
        Here is example response for icicibank, please use this example as a template:

        --------------------------------------------
        Short-Term View (<1 Month)
            •	Sentiment: 🟢 Cautiously Positive
            •	Target Price Range: ₹1,520 – ₹1,550
            •	Time Frame: Next 2–4 weeks
            •	Confidence Score: 8.5 / 10

        Key Drivers:
            •	Momentum from strong Q1 FY26 earnings
            •	Technical breakout above ₹1,500 with strong support at ₹1,470
            •	High institutional interest and analyst upgrades
            •	No major policy/credit events expected in next few weeks

        Risks:
            •	Profit-taking around ₹1,550
            •	Limited upside without fresh news flow
            •	Global risk sentiment or Nifty volatility could create drag

        Summary: Short-term setup is favorable with limited downside; modest upside expected if market stays stable.

        ⸻

        Mid-Term View (1–3 Months)
            •	Sentiment: 🟢 Moderately Positive
            •	Target Price Range: ₹1,570 – ₹1,620
            •	Time Frame: August to October 2025
            •	Confidence Score: 7.5 / 10

        Key Drivers:
            •	Broad-based loan growth and healthy deposits
            •	Resilient asset quality (Net NPA at 0.41%)
            •	Analyst bullishness and sector strength in private banks
            •	Potential festive-season demand revival by late Q2 FY26

        Risks:
            •	Net Interest Margin (NIM) pressure from slow deposit repricing
            •	Rising retail credit risks, esp. in unsecured segments
            •	Global macro shocks or risk-off sentiment
            •	Limited catalysts unless new growth triggers emerge

        Summary: ICICI Bank has strong fundamentals and sector leadership, supporting steady gains. However, macro and NIM headwinds may cap upside beyond 7–8% in this horizon.
                
        ------------------------------------
    
    3. Orchestraton and UI Engine:
        this needs to loadup UI on application start and pull all the info and display metrics and portfolio details on the app. It needs to show below things..
            - Sector wise, industry wise gouping of postions with measures like, total margin, no of positions, exposure %, total ROI (premium collected divide by margin used).
            - Position wise view of premium collected, ROI, margin used, risk (how far is spot price from current price), risk/reward (premium collected / risk), classify in risk groups.
            - Ability to get latest analysis by market analyst agent for each positions underlying stock on demand.
            - Also ability to get latest sector and market wise latest analysis by analyst agent, also on demand.
        
        It should also provide input mechanism for..
            - User ro provide custom prompts, this should then be passed to market analyst agent when it doing the analysis.
            - mechanishm to set search, filter cirteria for 





    

