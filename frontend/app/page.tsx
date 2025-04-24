"use client";
import { TextField, Button, Autocomplete } from "@mui/material"
import React from "react";

const symbols = [
  "AAPL"
]

interface StockData {
  stock_prices: number[][],
  accuracy: number
} // {"stock prices":[[1], [1], [1]], "accuracy": 0.99}

export default function Home() {

  const [stockData, setStockData] = React.useState<StockData | null>(null)

  async function submissionHandle(event:React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); // prevents reload of page 
    const symbol = event.currentTarget['symbol'].value
    const start_date = event.currentTarget['start_date'].value
    const end_date = event.currentTarget['end_date'].value
    // console.log(symbol, start_date, end_date)

    const res = await fetch("/api/prediction", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({symbol, start_date, end_date})
    })
    const data = await res.json()
    console.log(data)
  }

  return (
    <main className="flex flex-col gap-2 items-center w-screen h-screen overflow-auto"> 
      <h1 className="text-4xl text-center font-semibold p-4">Stock Prediction</h1>
      <p className="text-slate-600">
        This is a stock prediction app. It uses machine learning to predict the
        stock prices.
      </p>
      <div className="flex gap-4 w-8/10 mt-4">
        <form className="flex flex-col gap-3 w-4/10" onSubmit={submissionHandle}>
          <Autocomplete
              options={symbols}
              renderInput={(params) => <TextField name="symbol" {...params} label="Stock Symbol" />}/>
          <TextField name="start_date" variant="outlined" label="Start Date: YYYY-MM-DD" />
          <TextField name="end_date" variant="outlined" label="End Date: YYYY-MM-DD" />
          <Button type="submit" variant="contained">Submit</Button>
        </form>
        <div className="bg-red-500 w-full h-52"></div>
      </div>

      <footer className="fixed py-1.5 px-3 rounded-full bottom-2 right-2 bg-slate-700 text-white">The predictions are in no way shape or form any financial advice, bakchodi mat karo paiso ke saath</footer>
    </main>
  )
}
