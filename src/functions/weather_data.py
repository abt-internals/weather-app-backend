from datetime import datetime, timedelta
import requests
import os 
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()


key=os.getenv("key")
Base_url="http://api.weatherapi.com/v1"

async def get_weather(address:str):

    params={
            "key":key,
            "q":address,
            "aqi":"yes"
    }

    try:
            response=requests.get(f"{Base_url}/current.json",params=params)
            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as err:
            return {"error":err}
    

async def get_weather_data(address: str, date: str):
    try:
        today = datetime.today().date()
        fourteen_days_ahead = today + timedelta(days=14)
        three_hundred_days_ahead = today + timedelta(days=300)

        if fourteen_days_ahead <= datetime.strptime(date, "%Y/%m/%d").date() <= three_hundred_days_ahead:
            params = {
                "key": key,
                "q": address,
                "dt": date
            }
            response = requests.get(f"{Base_url}/future.json", params=params)

        elif datetime.strptime(date, "%Y/%m/%d").date()>three_hundred_days_ahead:
              
              raise HTTPException(status_code=400, detail="Email is already present in database")
        
        else:
            params = {
                "key": key,
                "q": address,
                "days": "14",
                "aqi": "no",
                "alerts": "no"
            }
            response = requests.get(f"{Base_url}/forecast.json", params=params)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as err:
        return {"error": str(err)}
