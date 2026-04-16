import ta
import pandas as pd

def add_indicators(df):

    # Flatten multi-index columns if they exist
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Force convert columns to 1D Series
    df["Close"] = pd.Series(df["Close"]).squeeze()
    df["Open"] = pd.Series(df["Open"]).squeeze()
    df["High"] = pd.Series(df["High"]).squeeze()
    df["Low"] = pd.Series(df["Low"]).squeeze()
    df["Volume"] = pd.Series(df["Volume"]).squeeze() 

    # Moving averages
    df["MA50"] = df["Close"].rolling(50).mean()
    df["MA200"] = df["Close"].rolling(200).mean()

    # RSI
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()

    # MACD
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()

    # Remove NaN rows
    df = df.dropna()

    return df