from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    symbol: str
    start_date: str | None = None
    end_date: str | None = None

@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/prediction/")
async def create_item(item: Item):
    from main import return_prediction
    symbol = item.symbol
    start_date = item.start_date if item.start_date else "2020-01-01"
    end_date = item.end_date if item.end_date else "2021-01-01"
    
    predicted_value = return_prediction(symbol, start_date, end_date)
    
    return {"stock prices": predicted_value[0].tolist(), "accuracy": predicted_value[1]}
    