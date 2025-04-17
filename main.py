import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error 
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Input
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Download historical stock price data from Yahoo Finance
def download_stock_data(symbol, user_input_date):
    end_date = user_input_date
    start_date = end_date - timedelta(days = 30) # taking 30 days as start to account for weekends 
    if end_date.weekday() == 5:
        end_date = (end_date - timedelta(days=1)).strftime("%Y-%m-%d")
    elif end_date.weekday() == 6:
        end_date = (end_date - timedelta(days=2)).strftime("%Y-%m-%d")
    data = yf.download(symbol, start=start_date, end=end_date)
    return data


# Prepare data for the neural network
def prepare_data(data, look_back=3):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data.values.reshape(-1, 1))

    X, y = [], []
    for i in range(len(scaled_data) - look_back):
        X.append(scaled_data[i : (i + look_back), 0])
        y.append(scaled_data[i + look_back, 0])

    return np.array(X), np.array(y), scaler


# Build and train the neural network model
def build_model(input_shape):
    model = Sequential()
    model.add(Input(shape = (input_shape, 1)))
    model.add(LSTM(128, input_shape=(input_shape, 1), activation="tanh", return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(64, activation="tanh", return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(32, activation="tanh"))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation="linear"))
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


# Plot actual vs predicted prices
'''def plot_predictions(actual, predicted):
    plt.plot(actual, label="Actual", color="blue")
    plt.plot(predicted, label="Predicted", color="red")
    plt.xlabel("Time")
    plt.ylabel("Close Price")
    plt.title("Stock Price Prediction with Neural Network")
    plt.legend()
    plt.show()'''


def predict_future_days(model, recent_data, look_back, future_days, scaler):
    predicted_prices = []

    for _ in range(future_days):
        input_data = np.array(recent_data[-look_back:]).reshape(1, look_back, 1)
        predicted_scaled = model.predict(input_data, verbose=0)
        predicted_price = scaler.inverse_transform(predicted_scaled.reshape(-1, 1))[0, 0]
        predicted_prices.append(predicted_price)

        # Update recent_data with the predicted scaled value
        scaled_price = scaler.transform(np.array([[predicted_price]]))[0, 0]
        recent_data = np.append(recent_data, scaled_price)

    return predicted_prices


def return_prediction(stock_symbol, user_input_date, no_of_days):
    data = download_stock_data(stock_symbol, user_input_date)

    # Prepare data for the neural network
    look_back = 10
    X, y, scaler = prepare_data(data["Close"], look_back=look_back)
    if X.shape[0] == 0:
        raise ValueError("Not enough data to create sequences. Try increasing the date range or reducing `look_back`.")

    X = X.reshape(X.shape[0], X.shape[1], 1)  # Reshape for LSTM input
    print(f"Shape of X: {X.shape}")
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Build and train the neural network model
    model = build_model(input_shape=look_back)
    model.fit(X_train, y_train, epochs=15, batch_size=32, verbose=1)

    # Evaluate the model
    predicted = model.predict(X_test)
    mse = mean_squared_error(y_test, predicted)
    accuracy = (1 - mse) * 100
    
    #Predict future stock prices
    recent_data = scaler.transform(data["Close"].values.reshape(-1, 1)).flatten()
    future_prices = predict_future_days(model, recent_data, look_back, no_of_days, scaler)
    
    return (future_prices, accuracy)

# Example 
if __name__ == "__main__":
    user_date = datetime.today()
    future_days = 3

    predicted_prices, accuracy = return_prediction("AAPL", user_date, future_days)
    print(f"Predicted Prices for the next {future_days} days: {predicted_prices}")
    print(f"Accuracy: {accuracy:.2f}%")
