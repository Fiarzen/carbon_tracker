from calculator import CarbonCalculator
from database import create_database_if_not_exists
from database import create_tables, save_emission_result
import sys

def main():
    create_tables()
    print("🌍 Welcome to the Carbon Tracker CLI")
    # Example: Transportation emissions
    transport_type = input("Enter transport mode (e.g. car, bus, flight): ").strip().lower()
    distance = float(input("Enter distance travelled (in km): "))
    fuel_type = input("Enter fuel type (if applicable, e.g. petrol, diesel, electric): ").strip().lower()

    calculator = CarbonCalculator()
    result = calculator.calculate_transportation(transport_type=transport_type, distance_km=distance, fuel_type=fuel_type)

    print(f"\nEstimated emissions: {result.co2_kg:.2f} kg CO₂")
    print(f"Details: {result.details}")

    # Optional: Setup database and save results
    save = input("\nWould you like to save this result to the database? (y/n): ").strip().lower()
    if save == "y":
        create_database_if_not_exists()
        result_id = save_emission_result(result)
        print(f"Saved with ID {result_id}")
        print("✅ Saved to database.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)