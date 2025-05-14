"use client";
import ClientDatePicker from "@/components/ClientDataPicker";
import { TextField, Button, Autocomplete } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";
import { DatePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import dayjs from "dayjs";
import { useEffect, useState } from "react";

interface StockData {
  historical_data: { date: string; price: number }[];
  predicted_data: number[];
  accuracy: number;
  error?: string;
} // {"historical_data": [{date: "2024-04-1", price: 1}, {date: "2024-04-2", price: 2}, {date: "2024-04-3", price: 3}] , "predicted_data" : [1, 1, 1], "accuracy": 0.99}

export default function Home() {
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [start_date, setStartDate] = useState(dayjs());
  const [end_date, setEndDate] = useState(dayjs().add(10, "day"));
  const [datesArr, setDates] = useState<string[]>([]);
  const [pred_data, setPredData] = useState<(null | number)[]>([]);
  const [buttonDisable, setButtonDisable] = useState(false);

  async function submissionHandle(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); // prevents reload of page
    setButtonDisable(true);
    const symbol = event.currentTarget["symbol"].value;
    const start_date = event.currentTarget["start_date"].value;
    const end_date = event.currentTarget["end_date"].value;
    console.log(symbol, start_date, end_date);

    const days = Math.floor(
      (new Date(end_date).getTime() - new Date(start_date).getTime()) /
        (1000 * 60 * 60 * 24),
    );

    fetch("/api/prediction", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ symbol, start_date, days }),
    })
      .then((res) => res.json())
      .then((data) => {
        const parsedData = JSON.parse(data);
        setStockData(parsedData);
        setButtonDisable(false);
      });
  }

  useEffect(() => {
    if (stockData && !stockData.error) {
      const dates: string[] = [];
      const pred: (number | null)[] = [];
      const hist = stockData?.historical_data;
      const current_date = start_date;
      hist.map((p, i) => {
        if (i === hist.length - 1) {
          dates.push(current_date.format("YYYY-MM-DD"));
          pred.push(p.price);
        } else {
          dates.push(p.date);
          pred.push(null);
        }
      });
      const predicted_data = stockData?.predicted_data;
      predicted_data.map((p, i) => {
        dates.push(current_date.add(i, "day").format("YYYY-MM-DD"));
        pred.push(p);
      });
      setDates(dates);
      setPredData(pred);
    }
  }, [stockData]);

  useEffect(() => {
    console.log(datesArr);
  }, [datesArr]);

  return (
    <main className="flex flex-col py-8 gap-2 items-center w-screen h-screen overflow-auto">
      <h1 className="text-4xl text-center font-semibold">Stock Prediction</h1>
      <p className="text-slate-600">
        This is a stock prediction app. It uses machine learning to predict the
        stock prices.
      </p>
      <form className="grid grid-cols-2 gap-3 py-4" onSubmit={submissionHandle}>
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <TextField
            name="symbol"
            variant="outlined"
            required
            label="Stock Symbol"
          />
          <ClientDatePicker
            label="Start Date"
            name="start_date"
            format="YYYY-MM-DD"
            value={start_date}
            onChange={(newValue) => setStartDate(dayjs(newValue))}
          />
          <ClientDatePicker
            label="End Date"
            name="end_date"
            format="YYYY-MM-DD"
            value={end_date}
            onChange={(newValue) => setEndDate(dayjs(newValue))}
          />
          <Button type="submit" variant="contained" disabled={buttonDisable}>
            Submit
          </Button>
        </LocalizationProvider>
      </form>
      {buttonDisable ? (
        "Loading..."
      ) : stockData ? (
        datesArr.length > 0 && pred_data ? (
          <>
            <LineChart
              xAxis={[
                {
                  data: datesArr.map((d) => dayjs(d)),
                  valueFormatter: (value) => dayjs(value).format("YYYY-MM-DD"),
                },
              ]}
              series={[
                {
                  data: stockData.historical_data.map((d) => d.price),
                  showMark: false,
                },
                { data: pred_data.map((d) => d), showMark: false },
              ]}
              height={500}
              width={1000}
            />
            <p>
              <b>Accuracy of Model:</b> {stockData.accuracy.toLocaleString()}%
            </p>
          </>
        ) : (
          "An error occurred, please try again later."
        )
      ) : (
        ""
      )}

      <footer className="fixed py-1.5 px-3 rounded-full bottom-2 right-2 bg-slate-700 text-white text-xs">
        The predictions are in no way shape or form any financial advice.
      </footer>
    </main>
  );
}
