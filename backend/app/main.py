import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error as mse
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Input 
from datetime import datetime, timedelta
import pandas as pd

# Download historical stock price data from Yahoo Finance
def download_stock_data(symbol, user_input_date):
    end_date = user_input_date
    # Get more data for better training (increased from 90 to 365 days)
    start_date = end_date - timedelta(days=365)

    # Handle weekends by moving to the last trading day
    if end_date.weekday() == 5:  # Saturday
        end_date = end_date - timedelta(days=1)
    elif end_date.weekday() == 6:  # Sunday
        end_date = end_date - timedelta(days=2)

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    print(f"Downloading data from {start_date_str} to {end_date_str}")
    
    try:
        data = yf.download(symbol, start=start_date_str, end=end_date_str)
        print(f"Downloaded {len(data)} data points")
        
        # Check if data is empty
        if data.empty:
            raise ValueError(f"No data found for symbol {symbol}")
        
        # Check if we have enough data
        if len(data) < 50:  # Increased minimum requirement
            raise ValueError(f"Not enough data points. Got only {len(data)} rows. Need at least 50.")
            
        return data
        
    except Exception as e:
        print(f"Error downloading data: {e}")
        raise

# Prepare data for the neural network
def prepare_data(data, look_back=10):
    try:
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

        print(f"Prepared data - X shape: {X.shape}, y shape: {y.shape}")
        return X, y, scaler
        
    except Exception as e:
        print(f"Error preparing data: {e}")
        raise

# Build and train the neural network model
def build_model(input_shape):
    try:
        model = Sequential()
        # Use Input layer to avoid warning
        model.add(Input(shape=(input_shape, 1)))
        model.add(LSTM(64, activation="tanh", return_sequences=True))  # Reduced complexity
        model.add(Dropout(0.2))
        model.add(LSTM(32, activation="tanh"))
        model.add(Dropout(0.2))
        model.add(Dense(1))
        model.compile(optimizer="adam", loss="mean_squared_error")
        return model
    except Exception as e:
        print(f"Error building model: {e}")
        raise

# Fixed predict_future_days function with proper dimension handling
def predict_future_days(model, recent_data, look_back, future_days, scaler):
    try:
        predicted_prices = []
        # Make a copy of the data to avoid modifying the original
        current_sequence = recent_data[-look_back:].copy()

        for day in range(future_days):
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
    except Exception as e:
        print(f"Error predicting future days: {e}")
        raise

def return_prediction(stock_symbol, user_input_date, no_of_days):
    try:
        print(f"Starting prediction for {stock_symbol} from {user_input_date} for {no_of_days} days")
        
        # Download stock data
        data = download_stock_data(stock_symbol, user_input_date)

        # FIXED: Store historical data for return - corrected the data processing
        hist_data = []
        try:
            # Convert the Close prices to a proper format
            close_prices = data["Close"]
            for date, price in close_prices.items():
                hist_data.append({
                    "date": date.strftime("%Y-%m-%d"), 
                    "price": round(float(price), 2)
                })
        except Exception as e:
            print(f"Error processing historical data: {e}")
            # Fallback method
            for i, (date, row) in enumerate(data.iterrows()):
                hist_data.append({
                    "date": date.strftime("%Y-%m-%d"), 
                    "price": round(float(row["Close"]), 2)
                })

        print(f"Processed {len(hist_data)} historical data points")

        # Prepare data for the neural network
        look_back = 20  # Increased look_back window
        X, y, scaler = prepare_data(data["Close"], look_back=look_back)

        print(f"Shape of X: {X.shape}, Shape of y: {y.shape}")

        # Ensure we have enough samples
        if len(X) < 10:  # Minimum samples required
            raise ValueError(f"Not enough samples after preprocessing. Got only {len(X)} samples. Need at least 10.")

        # Split data - use a reasonable test size
        test_size = max(0.1, min(0.3, 5/len(X)))  # At least 10%, at most 30%, minimum 5 samples
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, shuffle=False
        )

        print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")

        # Build and train the model
        model = build_model(input_shape=look_back)
        
        # Reduced epochs and added validation split
        history = model.fit(
            X_train, y_train, 
            epochs=20,  # Increased epochs
            batch_size=16,  # Reduced batch size
            validation_split=0.1, 
            verbose=1
        )

        # Evaluate the model
        predicted = model.predict(X_test, verbose=0)
        mse_value = mse(y_test, predicted)
        
        # Calculate accuracy as percentage (using MAPE - Mean Absolute Percentage Error approach)
        # Convert back to original scale for better accuracy calculation
        y_test_original = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
        predicted_original = scaler.inverse_transform(predicted.reshape(-1, 1)).flatten()
        
        # Calculate MAPE
        mape = np.mean(np.abs((y_test_original - predicted_original) / y_test_original)) * 100
        accuracy = max(0, 100 - mape)  # Convert to accuracy percentage
        
        print(f"Model MSE: {mse_value:.6f}, Accuracy: {accuracy:.2f}%")

        # Prepare data for future prediction
        scaled_data = scaler.transform(data["Close"].values.reshape(-1, 1)).flatten()

        # Predict future stock prices
        future_prices = predict_future_days(model, scaled_data, look_back, no_of_days, scaler)
        
        print(f"Predicted prices: {future_prices}")

        # Validate results
        if not future_prices or all(price <= 0 for price in future_prices):
            raise ValueError("Generated invalid predictions (zero or negative values)")

        return future_prices, round(accuracy, 2), hist_data

    except Exception as e:
        print(f"Error in return_prediction: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

# Example usage
if __name__ == "__main__":
    user_date = datetime.today()
    future_days = 3
    stock_symbol = "AAPL"

    try:
        predicted_prices, accuracy, historical_data = return_prediction(stock_symbol, user_date, future_days)
        if predicted_prices is not None:
            print(f"Historical data points: {len(historical_data)}")
            print(f"Predicted Prices for the next {future_days} days: {predicted_prices}")
            print(f"Model Accuracy: {accuracy}%")
        else:
            print("Prediction failed")
    except Exception as e:
        import traceback
        print(f"Error occurred: {e}")
        traceback.print_exc()