import streamlit as st
from src.calculator import CarbonCalculator
from src.database import create_database_if_not_exists, SessionLocal
from src.models import DBResult
from src.database import engine, Base

# Initialize DB and calculator
create_database_if_not_exists()
Base.metadata.create_all(bind=engine)
calculator = CarbonCalculator()

st.set_page_config(page_title="Carbon Tracker", page_icon="🌱")
st.title("🌱 Carbon Emissions Tracker")

category = st.sidebar.selectbox("Choose Activity Category", [
    "transportation", "energy", "food", "consumption", "waste"
])

def save_to_db(result):
    with SessionLocal() as session:
        db_result = DBResult(
            activity=result.activity,
            co2_kg=result.co2_kg
        )
        session.add(db_result)
        session.commit()

if category == "transportation":
    st.header("🚗 Transportation")
    transport_type = st.selectbox("Type", ["car", "flight", "public_transport"])
    
    if transport_type == "car":
        fuel_type = st.selectbox("Fuel", ["petrol", "diesel", "hybrid", "electric"])
        distance = st.number_input("Distance (km)", min_value=0.0)
        passengers = st.number_input("Passengers", min_value=1, value=1)

        if st.button("Calculate Emissions"):
            result = calculator.calculate_transportation("car", fuel_type, distance, passengers)
            st.success(f"{result.co2_kg} kg CO₂")
            st.json(result.details)
            save_to_db(result)

    elif transport_type == "flight":
        origin = st.text_input("Origin City")
        destination = st.text_input("Destination City")
        if st.button("Calculate Flight Emissions"):
            distance = calculator.estimate_flight_distance(origin, destination)
            # Choose a flight factor based on distance
            flight_class = (
                "domestic_short" if distance < 1000 else
                "domestic_long" if distance < 3000 else
                "international"
            )
            factor = calculator.emission_factors["transportation"]["flight"][flight_class]
            co2_kg = round(factor * distance, 3)
            result = calculator.calculate_transportation("flight", flight_class, distance)
            st.success(f"{co2_kg} kg CO₂ for {distance:.2f} km")
            st.json(result.details)
            save_to_db(result)

elif category == "energy":
    st.header("⚡ Energy Use")
    energy_type = st.selectbox("Type", ["electricity", "heating", "cooling"])
    source = st.selectbox("Source", list(calculator.emission_factors["energy"][energy_type].keys()))
    amount = st.number_input("Amount", min_value=0.0)
    unit = st.selectbox("Unit", ["kwh", "mwh"])

    if st.button("Calculate Energy Emissions"):
        result = calculator.calculate_energy(energy_type, source, amount, unit)
        st.success(f"{result.co2_kg} kg CO₂")
        st.json(result.details)
        save_to_db(result)

elif category == "food":
    st.header("🍔 Food Consumption")
    food_type = st.selectbox("Food Group", list(calculator.emission_factors["food"].keys()))
    food_item = st.selectbox("Food Item", list(calculator.emission_factors["food"][food_type].keys()))
    amount = st.number_input("Amount", min_value=0.0)
    unit = st.selectbox("Unit", ["kg", "g", "servings"])
    local = st.checkbox("Locally Produced? (Less emissions)", value=False)

    if st.button("Calculate Food Emissions"):
        result = calculator.calculate_food(food_type, food_item, amount, unit, local)
        st.success(f"{result.co2_kg} kg CO₂")
        st.json(result.details)
        save_to_db(result)

elif category == "consumption":
    st.header("🛍️ Consumption & Purchases")
    item_type = st.selectbox("Category", list(calculator.emission_factors["consumption"].keys()))
    item = st.selectbox("Item", list(calculator.emission_factors["consumption"][item_type].keys()))
    quantity = st.number_input("Quantity", min_value=1, value=1)
    lifetime = st.number_input("Expected Lifetime (years)", min_value=0.0, value=0.0)

    if st.button("Calculate Consumption Emissions"):
        result = calculator.calculate_consumption(item_type, item, quantity, lifetime or None)
        st.success(f"{result.co2_kg} kg CO₂")
        st.json(result.details)
        save_to_db(result)

elif category == "waste":
    st.header("🗑️ Waste Disposal")
    method = st.selectbox("Disposal Method", list(calculator.emission_factors["waste"].keys()))
    amount_kg = st.number_input("Amount (kg)", min_value=0.0)

    if st.button("Calculate Waste Emissions"):
        result = calculator.calculate_waste(method, amount_kg)
        st.success(f"{result.co2_kg} kg CO₂")
        st.json(result.details)
        save_to_db(result)

# Optional: Show recent results
st.sidebar.markdown("---")
if st.sidebar.checkbox("Show Recent Emission Logs"):
    with SessionLocal() as session:
        records = session.query(DBResult).order_by(DBResult.id.desc()).limit(10).all()
        for r in records:
            st.sidebar.write(f"{r.activity}: {r.emissions_kg:.2f} kg")
