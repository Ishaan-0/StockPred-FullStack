import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    const data = await request.json() // extract data from request
    
    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    const raw = JSON.stringify({
        "symbol": data.symbol,
        "start_date": data.start_date,
        "end_date": data.end_date
    });

    const requestOptions = {
        method: "POST",
        headers: myHeaders,
        body: raw
    };

    const res = await fetch("http://127.0.0.1:8000/prediction", requestOptions)
    const fetchData = await res.text() // data from ml model in text
    return NextResponse.json(fetchData); // sent to frontend as json
    
}