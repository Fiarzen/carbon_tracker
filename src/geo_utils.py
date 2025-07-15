import streamlit as st
import openrouteservice
from geopy.geocoders import Nominatim


client = openrouteservice.Client(key=st.secrets["ORS_API_KEY"])
geolocator = Nominatim(user_agent="carbon-tracker")

def geocode_city(city_name: str) -> list[float]:
    location = geolocator.geocode(city_name)
    if not location:
        raise ValueError(f"Could not geocode location: {city_name}")
    return [location.longitude, location.latitude]

def get_flight_distance_km(origin: str, destination: str) -> float:
    coords = [geocode_city(origin), geocode_city(destination)]
    response = client.directions(coords, profile='driving-car', format='geojson')
    distance_m = response["features"][0]["properties"]["segments"][0]["distance"]
    return distance_m / 1000 
