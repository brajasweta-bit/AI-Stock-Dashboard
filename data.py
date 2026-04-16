import yfinance as yf

def get_stock_data(stock, period="1y"):

    df = yf.download(stock, period=period)

    df = df[['Open','High','Low','Close','Volume']]

    df.dropna(inplace=True)

    return df