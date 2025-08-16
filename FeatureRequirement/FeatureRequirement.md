# Project Intoduction
    We want to build the Kite trading recommendation app, the app is not a typical trading app. the objective is not for the app to place trades but it's look at the portfolio current situation and then combine it with market conditions, news and other extenal factors to identify the profitable opportunities and make profits while managing the risk/reward equation, ROI, margin and cash management, and portfolio diversification.

    This app is for trading in Indian stock markets.


# Application components and architecture
    I want this app to have below key component/engines:
    1. MCP Server for interacting with Kite to get below data:
        - Portfolio information (margins, cash etc) and current positions, option chain and other trading related live data.
        - API's to get stock news, financial results and web search access.
    2. Market analyst agent: 
        - This is an LLM based engine which can use MCP server to research and form a sentiment/mood (how likely is it for something to go up or down). 
        - This agent needs to take the role of a seasoned professional equity research analyst with years of experience in financial markets.
        - It needs to be able to do the research for either a requsted stock, sector (nifty, banking, auto, IT etc) or whole market and base it's research on having a short term (less than 1 month) and medium term (1-3 months) time horizon. 
        - It should always consider wider market sentiment, stock specific and sector sentiment while forming the overall sentiment/mood.
        - while researching for any specific stock please looks at their
            - quarterly financial results and analyse them to see trend and immidiate effect also compare it to market/street expectations as this highly impacts stock movement in following few days after the results are announced. 
            - Do a web search to find relevant news on the stock, sector or news that might impact overall market.
            - look at intrinsic value if the stock and determin if it's overvalued or undervalued.
            - research social media for sentiments and analyst ratings.
            - consider other factors that equity analysts do for making an openion.
        - Self access your sentiment openion to improve iteratively. 
        - when returning your sentiment/mood analysis response be very clear and provide short summary and also include how confident your are in your openion/sentiment. 
        
        Here is example response for icicibank, please use this example as a template:

        --------------------------------------------
        Short-Term View (<1 Month)
            •	Sentiment: Cautiously Positive
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
            •	Sentiment: Moderately Positive
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
        This needs to loadup UI on application start and pull all the info and display metrics and portfolio details on the app. It needs to show below things..
            - Sector, industry wise gouping of postions with measures like, total margin, no of positions, exposure %, total ROI (premium collected divide by margin used).
            - Position wise view of premium collected, ROM (return on margin deployed as percentage of margin used), margin used, SSR (spot price minus strike price as percentage of spot price, bigger the number                           better it is), Risk indicator (indicator in 1-10 scale showing the risk based on analysis by market analyst agent, 1-minimum risk, 10-maximum risk), reward risk ratio (premium collected divide by RI),                        classify in risk groups.
            - Ability to get latest analysis by market analyst agent for each positions underlying stock on demand.
            - Also ability to get latest sector and market wise latest analysis by analyst agent, also on demand.
        
        It should also provide input mechanism for..
            - User ro provide custom prompts, this should then be passed to market analyst agent when it doing the analysis.
            - Mechanishm to set filter constraints when scouting for new opportunites. e.g. strike safety ratio (SSR) , minimum premium, minimum ROM, RI (risk indicator).
            - The stocks scope list, No agent (market analysis agent or recommendation agent) should analyse any stock that's not on this list or make any recommendation about those stocks.
            - Any other input that you feel might be important or useful.

        When requested by user (on demand) this engine should also collate all the portfolio info, indicators, market analyst agent response, user input and then formulate a detailed prompt for recommendation engine and             attach all the relevant portfolio data that LLM recommendation might need. Show this prompt on UI for user to review, once confirmed by user then the prompt should be passed to recommendation agent and once the              response is received then parse it into easy to digest action point and reasoning behind recommendation that user can take and show on UI.

    4. Recommendation Agent:
        This agent would be passed all the relevant info and detailed prompt to work with but can also directy call MCP server, read the info on UI or call market analyst agent for further analysis and reseach but the              objective is to find new options trading opportunites (trades). These can be additinal trades if the avabilable margin allows or a recommedation to swap an existing trade if the new trade is likely to be more               profitable, less risky to beneficial in other ways. 
        the agent must consider below when forming recommendations (so include these in prompt to agent).
        - This agent needs to play the role of an experienced investment fund manager and financial advisor in options trading and equity markets and has qualification in investment and risk management strategies.
        - The agent must look at option chain of the shortlisted stock (stocks in scope list in UI) to find the best option trades considering ROM, premium, SSR, RI etc. compare these to existing position to understand if            it's worth switching or taking additional new position.
        - Please provide clear actionable recommendations, whether trades or otherwise (recommendation that are not about trades but about balancing portfolio or reducing risk, improving ROI etc).
        - Self review the recommendations and improve iteratively if needed until satisfied.
        - Score your recommendation based on how confident you feel about your recommendation being profitable.
        - Please provide full reasoning and explain why something is being recommendation and what factors have you considered to arrive at the conclusion.

        Sample recommendation examples:
        example 1:
        -----------------------------------------------------------------
        Recomendation type: new trade (possible values : new trade, swap trade, hedge trade)
        Trade details: take a new position by Selling 1 lot of ICICIBANK AUG 1460 PE in option price range of 16.05 - 17.10 ({stock} {month} {strike price} {put/call} suggested price range of option)
        Confidence: 8.5/10 
        Trade driver : 
            - ICICI Bank posted strong financial performane {details of key financial numbers} and postivie sentiment in short to medium term as suggested by market analyst agent.
            - Currently the portfolio has relatively less exposure to private banking sector so this will diversify the risk.
            - The trade is offering good ROM at 17.3% also has SSR of 5.1%  offering good reward to risk.
            - Indian banking sector to benefit from interest rate cuts expected by RBI in next meeting so overall positive sentiments for banking sector.
        -----------------------------------------------------------------
        
        example 2:
        -----------------------------------------------------------------
        Recomendation type: swap trade (possible values : new trade, swap trade, hedge trade)
        Trade details: take a new position by Selling 1 lot of ICICIBANK AUG 1460 PE in option price range of 16.05 - 17.10 ({stock} {month} {strike price} {put/call} suggested price range of option) and square off 1 lot           in existing open postion HDFCBANK AUG 2000 PE at the buying option price range of 50-51.00
        Confidence: 8/10 
        Trade driver : 
            - ICICI Bank posted strong financial performane {details of key financial numbers} and postivie sentiment in short to medium term as suggested by market analyst agent.
            - Currently the portfolio has relatively less exposure to private banking sector so this will diversify the risk.
            - The new trade postion in ICICIBANK is offering good ROM at 17.3% also has SSR of 5.1% offering good reward to risk which is better than HDFCBANK ROM at 9.1%, SSR at 1.1%.
            - HDFCBANK postion is already at profit and doesn't have much option premium (theta decay) remaining in it for the given risk.
            - Indian banking sector to benefit from interest rate cuts expected by RBI in next meeting so overall positive sentiments for banking sector.
        -----------------------------------------------------------------


# Addiitional Resources to use by Market analyst agent and Recommendation agent

    Financial results: 
        - https://www.screener.in/
    Stock intrinsic value : 
        - https://www.smart-investing.in/
        - https://simplywall.st/
    Analyst ratings, key indicators and market mood:
        - https://www.tickertape.in/stocks
        - https://www.tickertape.in/market-mood-index
    FII activity:
        - https://web.stockedge.com/fii-activity
    KiteConnect (MCP server used KiteConnect python SDK):
        - https://kite.trade/docs/pykiteconnect/v4/

# Tech stack to use
    pydanticAI, langgraph, streamlit, python 
    

        
    
        





    

