from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import requests

app = FastAPI()

# CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/route-cost")
def route_cost(data: dict):

    origin = data["origin"]
    destination = data["destination"]

    url = "https://maps.googleapis.com/maps/api/directions/json"

    r = requests.get(url, params={
        "origin": origin,
        "destination": destination,
        "key": GOOGLE_API_KEY
    })

    route = r.json()["routes"][0]["legs"][0]

    km = route["distance"]["value"] / 1000
    time_h = route["duration"]["value"] / 3600

    speed = km / time_h

    if speed <= 90:
        fuel_rate = 4
    elif speed <= 110:
        fuel_rate = 5
    else:
        fuel_rate = 6

    fuel_l = (km * fuel_rate) / 100
    fuel_price = 63.5

    return {
        "km": km,
        "time_min": time_h * 60,
        "fuel_l": fuel_l,
        "fuel_tl": fuel_l * fuel_price
    }