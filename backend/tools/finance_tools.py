import yfinance as yf

def get_financial_data(ticker: str):
    """"
    Fetches financial data for a given stock ticker
    """

    try:
        company = yf.Ticker(ticker)
        info = company.info
        summary = {
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "market_cap": info.get("marketCap"),
            "revenue": info.get("totalRevenue"),
            "margin": info.get("profitMargins")
        }
        return str(summary)
    except Exception as e:
        return f"Could not find financial data for {ticker}: {e}"