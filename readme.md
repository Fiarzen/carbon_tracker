# 🌍 Carbon Tracker Application

A Python-based carbon footprint tracking tool that allows users to calculate and monitor their CO₂ emissions across key areas of daily life.

---

## 🚀 Overview

This application helps individuals understand and reduce their environmental impact by estimating emissions from:

- 🚗 Transportation  
- ⚡ Energy Use  
- 🍽️ Food Consumption  
- 🛍️ General Consumption (e.g. electronics, clothing)  
- ♻️ Waste Disposal  

It uses emission factors from trusted sources like EPA and DEFRA, and can be extended for additional features such as travel distance APIs and database storage.

---

## 🧠 Features

### ✅ Emission Categories

- **Transportation:**  
  Calculate per km CO₂ emissions from various vehicle types and fuels (petrol, diesel, electric, hybrid), public transport, and flights.

- **Energy Use:**  
  Calculate emissions from electricity, heating, and cooling based on source type and energy consumption.

- **Food:**  
  Calculates emissions from meat, dairy, seafood, and plant-based food items. Local sourcing lowers the footprint.

- **Consumption:**  
  Calculates carbon cost of buying electronics, clothing, furniture, etc.

- **Waste:**  
  Estimate emissions from landfill, recycling, composting, and incineration.

### 🌐 Optional Geo Integration

- **Flight Distance Estimation:**  
  Uses the [OpenRouteService](https://openrouteservice.org/) API to calculate approximate great-circle distances between airports or cities.

---

## 💾 Database Setup

Uses PostgreSQL with SQLAlchemy. You should configure your `.env` file like so:

```dotenv
PG_DATABASE=carbon_tracker
PG_USER=your_username
PG_PASSWORD=your_password
PG_HOST=localhost
PG_PORT=5432

Ensure your database.py reads this correctly with:

python
Copy
Edit
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")

🔧 Dependencies
Python 3.10+

sqlalchemy

psycopg2

python-dotenv

openrouteservice (optional)

geopy (if estimating distance manually)

pytest

📌 To Do / Planned
 Frontend integration (web or desktop UI)

 User accounts and tracking over time

 API endpoint for external tools

 Visualisation (e.g. charts, graphs)

 Internationalisation