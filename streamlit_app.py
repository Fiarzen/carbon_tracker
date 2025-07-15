import streamlit as st
from carbon_tracker.calculator import CarbonCalculator

# Initialize calculator
calc = CarbonCalculator()

st.title("🌍 Carbon Footprint Calculator")

activity_type = st.selectbox("Select an activity category", ["Transportation", "Energy", "Food"])

if activity_type == "Transportation":
    st.header("🚗 Transportation")
    transport_type = st.selectbox("Type of transport", ["car", "motorcycle", "public_transport"])
    if transport_type == "car":
        fuel = st.selectbox("Fuel type", ["petrol", "diesel", "hybrid", "electric"])
    elif transport_type == "motorcycle":
        fuel = "petrol"
    else:
        fuel = st.selectbox("Mode", ["bus", "train", "subway", "tram"])
    
    distance = st.number_input("Distance (km)", min_value=0.0)
    passengers = st.number_input("Number of passengers", min_value=1, value=1)
    
    if st.button("Calculate transportation impact"):
        result = calc.calculate_transportation(transport_type, fuel, distance, passengers)
        st.success(f"Estimated CO₂ emissions: {result.co2_kg} kg")
        st.json(result.details)

elif activity_type == "Energy":
    st.header("⚡ Energy Use")
    energy_type = st.selectbox("Type", ["electricity", "heating", "cooling"])
    source = st.selectbox("Source", list(calc.get_category_factors("energy")[energy_type].keys()))
    amount = st.number_input("Consumption amount", min_value=0.0)
    unit = st.selectbox("Unit", ["kWh", "MWh"])
    
    if st.button("Calculate energy impact"):
        result = calc.calculate_energy(energy_type, source, amount, unit)
        st.success(f"Estimated CO₂ emissions: {result.co2_kg} kg")
        st.json(result.details)

elif activity_type == "Food":
    st.header("🥩 Food")
    food_type = st.selectbox("Category", list(calc.get_category_factors("food").keys()))
    food_item = st.selectbox("Item", list(calc.get_category_factors("food")[food_type].keys()))
    amount = st.number_input("Amount", min_value=0.0)
    unit = st.selectbox("Unit", ["kg", "g", "servings"])
    local = st.checkbox("Is this locally produced?", value=False)
    
    if st.button("Calculate food impact"):
        result = calc.calculate_food(food_type, food_item, amount, unit, local)
        st.success(f"Estimated CO₂ emissions: {result.co2_kg} kg")
        st.json(result.details)
