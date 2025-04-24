from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
import uvicorn
import numpy as np
from typing import List, Optional, Union, Dict, Any

app = FastAPI()

class Item(BaseModel):
    symbol: str
    start_date: Optional[str] = None
    days: int = 3  # no.of days that the user inputs, if no input then default is 3 days

class PredictionResponse(BaseModel):
    stock_prices: List[float]
    accuracy: float

class ErrorResponse(BaseModel):
    error: str

@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/prediction/", response_model=Union[PredictionResponse, ErrorResponse])
def create_item(item: Item):
    from main import return_prediction
    symbol = item.symbol.upper()

    # Convert string date to datetime if provided
    if item.start_date:
        try:
            start_date = datetime.strptime(item.start_date, "%Y-%m-%d")
        except ValueError:
            return ErrorResponse(error="Invalid date format. Please use YYYY-MM-DD.")
    else:
        start_date = datetime.today()

    # Make sure days is an integer
    days = item.days

    # Call prediction function and handle potential None return
    try:
        predicted_value = return_prediction(symbol, start_date, days)
    except Exception as e:
        return ErrorResponse(error=f"Error during prediction: {str(e)}")

    if predicted_value is None or predicted_value[0] is None:
        return ErrorResponse(error="Could not generate prediction. Not enough data for the selected stock.")

    # Convert numpy values to Python native types
    stock_prices = []
    if predicted_value[0] is not None:
        if isinstance(predicted_value[0], np.ndarray):
            stock_prices = [float(price) for price in predicted_value[0]]
        elif isinstance(predicted_value[0], list):
            stock_prices = [float(price) if isinstance(price, np.number) else float(price) for price in predicted_value[0]]
        else:
            stock_prices = [float(predicted_value[0])]
    
    # Convert accuracy to a Python float
    if predicted_value[1] is not None:
        if isinstance(predicted_value[1], (np.number, np.float32, np.float64)):
            accuracy = float(predicted_value[1])
        else:
            accuracy = float(predicted_value[1])
    else:
        accuracy = 0.0

    return PredictionResponse(stock_prices=stock_prices, accuracy=accuracy)

# Add this part to run the server when the file is executed directly
if __name__ == "__main__":
    print("Starting FastAPI server on http://127.0.0.1:8000")
    print("Access the API documentation at http://127.0.0.1:8000/docs")
    uvicorn.run("Apis:app", host="127.0.0.1", port=8000, reload=True)
