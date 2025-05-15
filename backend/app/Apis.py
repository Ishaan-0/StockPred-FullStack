from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime
import uvicorn
import numpy as np
from typing import List, Optional, Union, Dict, Any
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    symbol: str
    start_date: Optional[str] = None
    days: int = 3  # no.of days that the user inputs, if no input then default is 3 days

class PredictionResponse(BaseModel):
    historical_data: List[Dict[str, Union[str, float]]]
    predicted_data: List[float]
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

    if predicted_value[2] is not None:
        hist_data = predicted_value[2]
    else:
        hist_data = []

    return PredictionResponse(predicted_data=stock_prices, accuracy=accuracy, historical_data=hist_data)

# Add this part to run the server when the file is executed directly
if __name__ == "__main__":
    print("Starting FastAPI server on http://127.0.0.1:8000")
    print("Access the API documentation at http://127.0.0.1:8000/docs")
    uvicorn.run("Apis:app", host="0.0.0.0", port=8000, reload=True)
