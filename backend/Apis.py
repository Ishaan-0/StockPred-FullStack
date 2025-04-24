from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta

app = FastAPI()

class Item(BaseModel):
    symbol: str
    start_date: str | None = None
    days: str | None = "3" # no.of days that the user inputs , if no input then default is 3 days

@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/prediction/")
def create_item(item: Item):
    from main import return_prediction
    symbol = item.symbol.upper()
    start_date = item.start_date if item.start_date else datetime.today().strftime("%Y-%m-%d")
    days = item.days
    
    predicted_value = return_prediction(symbol, start_date, days)
    
    return {"stock prices": predicted_value[0].tolist(), "accuracy": predicted_value[1]}
    