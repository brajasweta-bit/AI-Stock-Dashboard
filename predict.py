import pickle

def predict_signal(df):

    # Load trained model
    model = pickle.load(open("model.pkl", "rb"))

    features = ["RSI", "MACD", "MA50", "MA200"]

    # Select last row
    latest = df[features].tail(1)

    # If dataframe empty
    if latest.empty:
        return "HOLD", 0.0

    prediction = model.predict(latest)[0]
    probability = model.predict_proba(latest)[0].max()

    if prediction == 2:
        signal = "BUY 📈"
    elif prediction == 0:
        signal = "SELL 📉"
    else:
        signal = "HOLD ⏳"

    return signal, probability