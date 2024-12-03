import yfinance as yf
import pandas as pd
import random
from datetime import datetime, timedelta
import json
import time
import finnhub

API_KEY = 'cppao79r01qn2da2cu00cppao79r01qn2da2cu0g'
finnhub_client = finnhub.Client(api_key=API_KEY)


def fetch_stock_universe():
    csv_files = ['constituents.csv', 'russell_2000_components.csv', 'sp400_companies.csv']  
    tickers = set()
    
    for file in csv_files:
        df = pd.read_csv(file)
        first_column = df.iloc[:, 0]  # Select the first column
        tickers.update(first_column.values)
    
    with open("tickers.json", "r") as f:
        data = json.load(f)
    tickers.update(data["Tickers"])

    # Remove duplicates and clean up
    tickers = list(set(tickers))
    return tickers

def get_random_stock_sample(n=1000):
    # Fetch the stock universe
    tickers = fetch_stock_universe()
    
    # Check if we have enough tickers
    if len(tickers) < n:
        raise ValueError("Not enough tickers in the universe to sample!")
    
    # Randomly select 'n' tickers
    random_sample = random.sample(tickers, n)
    return random_sample


def fetch_analyst_recommendations(ticker):
    # Example function to fetch sentiment data from an API
    # Replace with actual API call and key
    response = finnhub_client.recommendation_trends(ticker)
    most_recent_sentiment = response[0]
    buy_count = most_recent_sentiment['buy']
    strong_buy_count = most_recent_sentiment['strongBuy']
    sell_count = most_recent_sentiment['sell']
    strong_sell_count = most_recent_sentiment['strongSell']
    sentiment_counts = {
        "buy": buy_count,
        "strongBuy": strong_buy_count,
        "sell": sell_count,
        "strongSell": strong_sell_count
    }
    
    max_sentiment = max(sentiment_counts, key=lambda k: (sentiment_counts[k], k))
    return max_sentiment

def insider_sentiment(ticker):
    # Example function to fetch analyst recommendations from an API
    # Replace with actual API call and key
    time.sleep(1)
    response = finnhub_client.stock_insider_sentiment(ticker, '2023-10-01', '2024-10-01')
    data = response['data']
    max_year = 0
    sentiment = None
    for element in data:
        year = element['year']
        month = element['month']
        totaled_year = int(str(year) + str(month))
        if totaled_year > max_year:
            max_year = totaled_year
            sentiment = element['mspr']
    if sentiment  < 0:
        return 'Negative'
    elif sentiment > 0:
        return 'Positive'
    else:
        return 'Neutral'


def classify_growth_or_value(pe_ratio):
    if pe_ratio is None:
        return "Unknown"
    elif pe_ratio < 15:
        return "Value"
    elif pe_ratio >= 15:
        return "Growth"
    else:
        return "Unknown"
    
def classify_market_cap(market_cap):
    if market_cap < 2e9:
        return "Small Cap"
    elif 2e9 <= market_cap < 10e9:
        return "Mid Cap"
    else:
        return "Large Cap"

def classify_volatility(beta):
    if beta is None:
        return "Unknown"
    elif beta < 0.8:
        return "Low Volatility"
    elif 0.8 <= beta < 1.2:
        return "Medium Volatility"
    else:
        return "High Volatility"
    
def fetch_stock_data(selected_tickers):
    # Container for stock data
    data = []
    
    for count, ticker  in enumerate(selected_tickers):
        try:
            print(f"Fetching data for {ticker} ({count+1}/{len(selected_tickers)})")
            # Wait for 1 second
            time.sleep(1.5)
            
            # Fetch stock data
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Fetch historical price data for the last year
            end_date = datetime.today()
            start_date = end_date - timedelta(days=365)
            hist = stock.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
            
            if hist.empty or 'marketCap' not in info:
                continue
            
            # Get the most recent close price
            recent_close_price = hist['Close'].iloc[-1]
            
            # Append stock data
            data.append({
                "Ticker": ticker,
                "Sector": info.get("sector", "Unknown"),  # Categorical
                "Industry": info.get("industry", "Unknown"),  # Categorical
                "Region": "North America",  # Categorical (default)
                "Market Cap Classification": classify_market_cap(info.get("marketCap", 0)),  # Categorical
                "Volatility Classification": classify_volatility(info.get("beta", None)),  # Categorical
                "Growth vs Value": classify_growth_or_value(info.get("trailingPE", None)),  # Categorical
                "P/E Ratio": info.get("trailingPE", None),  # Quantitative
                "Dividend Yield (%)": info.get("dividendYield", 0) * 100,  # Quantitative
                "Beta": info.get("beta", None),  # Quantitative
                "Avg Volume": hist['Volume'].mean(),  # Quantitative
                "Recent Close Price": recent_close_price,  # Quantitative
                "EPS": info.get("trailingEps", None),  # Quantitative
                "Revenue": info.get("totalRevenue", None),  # Quantitative
                "Net Income": info.get("netIncomeToCommon", None),  # Quantitative
                "Debt-to-Equity Ratio": info.get("debtToEquity", None),  # Quantitative
                "ROE": info.get("returnOnEquity", None),  # Quantitative
                "P/B Ratio": info.get("priceToBook", None),  # Quantitative
                "Free Cash Flow": info.get("freeCashflow", None),  # Quantitative
                "Analyst Ratings": fetch_analyst_recommendations(ticker),  # Categorical
                "Insider Transactions": insider_sentiment(ticker)  # Categorical
            })
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    
    return data

# Example usage
csv_files = ['constituents.csv', 'russell_2000_components.csv', 'sp400_companies.csv']  # Replace with your actual file names
# random_sample = get_random_stock_sample(n=1000)


df = pd.read_csv('stock_dataset.csv')
df = df['Ticker']
random_sample = list(df)
stock_data = fetch_stock_data(random_sample)
df = pd.DataFrame(stock_data)
df.to_csv('enhanced_stock_dataset.csv', index=False)
print(df.head())
