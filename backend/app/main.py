import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error as mse
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Input
from datetime import datetime, timedelta

# Download historical stock price data from Yahoo Finance
def download_stock_data(symbol, user_input_date):
    end_date = user_input_date
    # Get 1 year of data for better training
    start_date = end_date - timedelta(days=90)

    # Handle weekends by moving to the last trading day
    if end_date.weekday() == 5:  # Saturday
        end_date = end_date - timedelta(days=1)
    elif end_date.weekday() == 6:  # Sunday
        end_date = end_date - timedelta(days=2)

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    print(f"Downloading data from {start_date_str} to {end_date_str}")
    data = yf.download(symbol, start=start_date_str, end=end_date_str)
    print(f"Downloaded {len(data)} data points")

    # Check if we have enough data
    if len(data) < 30:
        raise ValueError(f"Not enough data points. Got only {len(data)} rows.")

    return data

# Prepare data for the neural network
def prepare_data(data, look_back=10):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data.values.reshape(-1, 1))

    X, y = [], []
    for i in range(len(scaled_data) - look_back):
        X.append(scaled_data[i:(i + look_back), 0])
        y.append(scaled_data[i + look_back, 0])

    X = np.array(X)
    y = np.array(y)

    # Reshape X to be [samples, time steps, features]
    X = X.reshape(X.shape[0], X.shape[1], 1)

    return X, y, scaler

# Build and train the neural network model
def build_model(input_shape):
    model = Sequential()
    # Use Input layer to avoid warning
    model.add(Input(shape=(input_shape, 1)))
    model.add(LSTM(128, activation="tanh", return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(64, activation="tanh", return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(32, activation="tanh"))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model

# Fixed predict_future_days function with proper dimension handling
def predict_future_days(model, recent_data, look_back, future_days, scaler):
    predicted_prices = []
    # Make a copy of the data to avoid modifying the original
    current_sequence = recent_data[-look_back:].copy()

    for _ in range(future_days):
        # Reshape for prediction (add batch and feature dimensions)
        x_input = current_sequence.reshape(1, look_back, 1)

        # Predict the next value
        next_val = model.predict(x_input, verbose=0)[0, 0]

        # Store the predicted value (after inverse scaling)
        predicted_price = scaler.inverse_transform(np.array([[next_val]]))[0, 0]
        predicted_prices.append(predicted_price)

        # Update the sequence by removing the first element and adding the prediction
        current_sequence = np.append(current_sequence[1:], next_val)

    return [round(float(price), 2) for price in predicted_prices]

def return_prediction(stock_symbol, user_input_date, no_of_days):
    # Download stock data
    data = download_stock_data(stock_symbol, user_input_date)

    # Store historical data for return
    historical_data = data["Close"].to_dict()[stock_symbol]
    hist_data = []
    for key, value in historical_data.items():
        hist_data.append({"date": key.strftime("%Y-%m-%d"), "price": value})
    # print(hist_data)

    # Prepare data for the neural network
    look_back = 15  # Reduced from 20 to ensure enough samples
    X, y, scaler = prepare_data(data["Close"], look_back=look_back)

    print(f"Shape of X: {X.shape}, Shape of y: {y.shape}")

    # Ensure we have enough samples
    if len(X) < 5:  # Arbitrary minimum number of samples
        raise ValueError(f"Not enough samples after preprocessing. Got only {len(X)} samples.")

    # Split data - use a small test size if data is limited
    test_size = min(0.2, 1/len(X))
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, shuffle=False
    )

    # Build and train the model
    model = build_model(input_shape=look_back)
    model.fit(X_train, y_train, epochs=15, batch_size=32, verbose=1)

    # Evaluate the model
    predicted = model.predict(X_test)
    mse_value = mse(y_test, predicted)
    accuracy = (1 - mse_value) * 100

    # Prepare data for future prediction
    scaled_data = scaler.transform(data["Close"].values.reshape(-1, 1)).flatten()

    # Predict future stock prices
    future_prices = predict_future_days(model, scaled_data, look_back, no_of_days, scaler)

    return future_prices, accuracy, hist_data

# Example usage
if __name__ == "__main__":
    user_date = datetime.today()
    future_days = 3
    stock_symbol = "AAPL"

    try:
        predicted_prices, accuracy, historical_data = return_prediction(stock_symbol, user_date, future_days)
        print(f"Historical data points: {len(historical_data)}")
        print(f"Predicted Prices for the next {future_days} days: {predicted_prices}")
        print(f"Model Accuracy: {accuracy:.2f}%")
    except Exception as e:
        import traceback
        print(f"Error occurred: {e}")
        traceback.print_exc()  # Print full stack trace for debugging
