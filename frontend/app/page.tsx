"use client";
import { TextField, Button, Autocomplete } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";
import { DatePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import dayjs from "dayjs";
import React, { useEffect } from "react";

const symbols = ["AAPL"];

interface StockData {
  historical_data: number[];
  stock_prices: number[];
  accuracy: number;
} // {"historical_data": [1, 1, 1] , "stock_prices":[1, 1, 1], "accuracy": 0.99}

export default function Home() {
  const [stockData, setStockData] = React.useState<StockData | null>(null);

  async function submissionHandle(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); // prevents reload of page
    const symbol = event.currentTarget["symbol"].value;
    const start_date = dayjs(event.currentTarget["start_date"].value).format(
      "YYYY-MM-DD",
    );
    const end_date = dayjs(event.currentTarget["end_date"].value).format(
      "YYYY-MM-DD",
    );
    console.log(symbol, start_date, end_date);

    const days = Math.floor(
      (new Date(end_date).getTime() - new Date(start_date).getTime()) /
        (1000 * 60 * 60 * 24),
    );

    const res = await fetch("/api/prediction", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ symbol, start_date, days }),
    });
    const data = await res.json();
    const parsedData = JSON.parse(data);
    setStockData(parsedData);
  }

  // useEffect(() => {
  //   if (stockData) {
  //     const parsedData =
  //       typeof stockData === "string" ? JSON.parse(stockData) : stockData;
  //     console.log("historical_data:", parsedData.historical_data);
  //   }
  // }, [stockData]);

  return (
    <main className="flex flex-col gap-2 items-center w-screen h-screen overflow-auto">
      <h1 className="text-4xl text-center font-semibold p-4">
        Stock Prediction
      </h1>
      <p className="text-slate-600">
        This is a stock prediction app. It uses machine learning to predict the
        stock prices.
      </p>
      <div className="flex gap-4 w-8/10 mt-4">
        <form
          className="flex flex-col gap-3 w-4/10"
          onSubmit={submissionHandle}
        >
          <TextField
            name="symbol"
            variant="outlined"
            required
            label="Stock Symbol"
          />
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DatePicker
              label="Start Date"
              name="start_date"
              defaultValue={dayjs()}
            />
            <DatePicker
              label="End Date"
              name="end_date"
              defaultValue={dayjs().add(4, "day")}
            />
          </LocalizationProvider>
          <Button type="submit" variant="contained">
            Submit
          </Button>
        </form>
        <div>
          {stockData && (
            <LineChart
              xAxis={[
                { data: stockData.historical_data.map((d, i) => i) },
                { data: stockData.stock_prices.map((d, i) => i) },
              ]}
              series={[
                { data: stockData.historical_data },
                { data: stockData.stock_prices },
              ]}
              height={300}
              width={600}
            />
          )}
        </div>
      </div>

      <footer className="fixed py-1.5 px-3 rounded-full bottom-2 right-2 bg-slate-700 text-white">
        The predictions are in no way shape or form any financial advice,
        bakchodi mat karo paiso ke saath
      </footer>
    </main>
  );
}
