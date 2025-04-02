from datetime import datetime, timedelta
import httpx
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

load_dotenv()


key = os.getenv("KEY")
Base_url = "http://api.weatherapi.com/v1"


async def get_weather(address: str):
    params = {"key": key, "q": address, "aqi": "yes"}

    try:
        # Perform an async request using httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.weatherapi.com/v1/current.json", params=params
            )
            response.raise_for_status()  # Raise an exception for 4xx/5xx responses
            return response.json()
    except httpx.RequestError as err:
        # Handle request error (e.g., network issues, invalid URL)
        return JSONResponse(
            content={"error": f"Request failed: {err}"}, status_code=500
        )
    except httpx.HTTPStatusError as err:
        # Handle specific HTTP errors (e.g., 404, 500)
        return JSONResponse(
            content={"error": f"HTTP error occurred: {err}"}, status_code=500
        )
    except Exception as err:
        # Catch any other exceptions (e.g., JSON parsing errors)
        return JSONResponse(
            content={"error": f"An error occurred: {err}"}, status_code=500
        )


async def get_weather_data(address: str, date: str):
    try:
        today = datetime.today().date()
        fourteen_days_ahead = today + timedelta(days=14)
        three_hundred_days_ahead = today + timedelta(days=300)

        if (
            fourteen_days_ahead
            <= datetime.strptime(date, "%Y/%m/%d").date()
            <= three_hundred_days_ahead
        ):
            params = {"key": key, "q": address, "dt": date}
            # Asynchronous HTTP request with httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{Base_url}/future.json", params=params)

        elif datetime.strptime(date, "%Y/%m/%d").date() > three_hundred_days_ahead:
            return JSONResponse(
                content={"message": "Date is too far in the future"}, status_code=500
            )
            # raise HTTPException(status_code=400, detail="Date is too far in the future")

        elif datetime.strptime(date, "%Y/%m/%d").date() == today:
            params = {
                "key": key,
                "q": address,
                "aqi": "yes",
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{Base_url}/current.json", params=params)

        else:
            params = {
                "key": key,
                "q": address,
                "days": "14",
                "aqi": "no",
                "alerts": "no",
            }
            # Asynchronous HTTP request with httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{Base_url}/forecast.json", params=params)

        # Check if the request was successful
        response.raise_for_status()
        return response.json()

    except httpx.RequestError as err:
        # Handle any request-related errors
        return JSONResponse(
            content={"error": f"Request failed: {err}"}, status_code=500
        )

    except httpx.HTTPStatusError as err:
        # Handle specific HTTP errors
        return JSONResponse(
            content={"error": f"HTTP error occurred: {err}"}, status_code=500
        )
