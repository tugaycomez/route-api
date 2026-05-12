from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import requests

app = FastAPI()

# CORS (frontend için zorunlu)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
FUEL_PRICE = 63.5


@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/route-cost")
def route_cost(data: dict):

    origin = data.get("origin")
    destination = data.get("destination")

    if not origin or not destination:
        return {"error": "origin or destination missing"}

    url = "https://maps.googleapis.com/maps/api/directions/json"

    response = requests.get(url, params={
        "origin": origin,
        "destination": destination,
        "alternatives": "true",
        "key": GOOGLE_API_KEY
    })

    json_data = response.json()

    routes = json_data.get("routes", [])

    if len(routes) == 0:
        return {"error": "no routes found", "google_response": json_data}

    result = []

    for i, route in enumerate(routes[:3]):

        leg = route["legs"][0]

        km = leg["distance"]["value"] / 1000
        time_h = leg["duration"]["value"] / 3600

        speed = km / time_h if time_h > 0 else 0

        if speed <= 90:
            fuel_rate = 4
        elif speed <= 110:
            fuel_rate = 5
        else:
            fuel_rate = 6

        fuel_l = (km * fuel_rate) / 100
        fuel_cost = fuel_l * FUEL_PRICE

        result.append({
            "route": f"Rota {i+1}",
            "km": round(km, 1),
            "time_min": round(time_h * 60, 0),
            "fuel_l": round(fuel_l, 1),
            "fuel_tl": round(fuel_cost, 0),
            "total": round(fuel_cost, 0)
        })

    return {
        "origin": origin,
        "destination": destination,
        "routes": result
    }
