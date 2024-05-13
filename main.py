import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt


# Download historical stock price data from Yahoo Finance
def download_stock_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data


# Prepare data for the neural network
def prepare_data(data, look_back=1):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data.values.reshape(-1, 1))

    X, y = [], []
    for i in range(len(scaled_data) - look_back):
        X.append(scaled_data[i : (i + look_back), 0])
        y.append(scaled_data[i + look_back, 0])

    return np.array(X), np.array(y)


# Build and train the neural network model
def build_model(input_shape):
    model = Sequential()
    model.add(Dense(64, input_shape=(input_shape,), activation="relu"))
    model.add(Dense(32, activation="relu"))
    model.add(Dense(1, activation="linear"))
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


# Plot actual vs predicted prices
def plot_predictions(actual, predicted):
    plt.plot(actual, label="Actual", color="blue")
    plt.plot(predicted, label="Predicted", color="red")
    plt.xlabel("Time")
    plt.ylabel("Close Price")
    plt.title("Stock Price Prediction with Neural Network")
    plt.legend()
    plt.show()

if __name__ == "main":
    # Define stock symbol and date range
    stock_symbol = "AAPL"  # Example: Apple
    start_date = "2020-01-01"
    end_date = "2021-01-01"

    # Download stock price data
    data = download_stock_data(stock_symbol, start_date, end_date)

    # Prepare data for the neural network
    X, y = prepare_data(data["Close"], look_back=10)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Build and train the neural network model
    model = build_model(input_shape=X_train.shape[1])
    model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=1)

    # Evaluate the model
    loss = model.evaluate(X_test, y_test)
    print("Test Loss:", loss)

    # Make predictions
    predicted = model.predict(X_test)

    # Plot actual vs predicted prices
    plot_predictions(y_test, predicted)
