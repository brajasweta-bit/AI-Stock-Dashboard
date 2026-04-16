from data import get_stock_data
from indicators import add_indicators
from sklearn.ensemble import RandomForestClassifier
import pickle

df = get_stock_data("AAPL")

df = add_indicators(df)

# convert Close column to 1D
close = df['Close'].squeeze()

df['Future'] = close.shift(-5)  # predict 5 days ahead

df['Return'] = (df['Future'] - close) / close

df['Target'] = 1  # HOLD default

df.loc[df['Return'] > 0.02, 'Target'] = 2   # BUY if >2% increase
df.loc[df['Return'] < -0.02, 'Target'] = 0  # SELL if >2% drop

X = df[['RSI','MA50','MA200','MACD']]
y = df['Target']

model = RandomForestClassifier()

model.fit(X, y)

pickle.dump(model, open("model.pkl","wb"))

print("Model trained successfully")