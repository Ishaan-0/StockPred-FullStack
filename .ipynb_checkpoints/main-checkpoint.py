import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Download historical stock price data from Yahoo Finance
def download_stock_data(symbol):
    end_date = datetime.today()
    if end_date.weekday() == 5:
        end_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif end_date.weekday() == 6:
        end_date = (datetime.today() - timedelta(days=2)).strftime("%Y-%m-%d")
    data = yf.download(symbol, start="2020/01/01", end=end_date)
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
    model.add(LSTM(Dense(128, input_shape=(input_shape,), activation="tanh")))
    model.add(Dropout(0.2))
    model.add(LSTM(Dense(64, activation="tanh")))
    model.add(Dropout(0.2))
    model.add(LSTM(Dense(32, activation="tanh")))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation="tanh"))
    model.compile(optimizer="adam", loss="mean_absolute_error")
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



def return_prediction(stock_symbol):
    data = download_stock_data(stock_symbol)

    # Prepare data for the neural network
    X, y = prepare_data(data["Close"], look_back=10)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Build and train the neural network model
    model = build_model(input_shape=X_train.shape[1])
    model.fit(X_train, y_train, epochs=64, batch_size=32, verbose=1)

    # Evaluate the model
    


    # Make predictions
    predicted = model.predict(X_test)
    mse = mean_squared_error(y_test, predicted)
    accuracy = (1 - mse) * 100
    return (predicted, accuracy)

predicted_value = return_prediction("AAPL")
print(predicted_value)
