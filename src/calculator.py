"""
Carbon Footprint Calculator Engine

This module handles all emission factor calculations and conversions
from activities to CO2 equivalent emissions.
"""
import json
from typing import Dict, Union, Optional
from dataclasses import dataclass
from pathlib import Path
from src.geo_utils import get_flight_distance_km


@dataclass
class EmissionResult:
    """Result of an emission calculation"""
    co2_kg: float
    category: str
    subcategory: str
    activity: str
    details: Dict[str, Union[str, float]]


class CarbonCalculator:
    """Main calculation engine for carbon emissions"""
    
    def __init__(self, emission_factors_path: str = "data/emission_factors.json"):
        """Initialize calculator with emission factors data"""
        self.emission_factors = self._load_emission_factors(emission_factors_path)
    
    def _load_emission_factors(self, path: str) -> Dict:
        """Load emission factors from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default emission factors if file doesn't exist
            default_factors = self._create_default_emission_factors()
            self._save_emission_factors(path, default_factors)
            return default_factors
    
    def _create_default_emission_factors(self) -> Dict:
        """Create default emission factors based on EPA and DEFRA data"""
        return {
            "transportation": {
                "car": {
                    "petrol": 0.404,  # kg CO2 per km
                    "diesel": 0.448,
                    "hybrid": 0.253,
                    "electric": 0.089
                },
                "motorcycle": {
                    "petrol": 0.103
                },
                "public_transport": {
                    "bus": 0.089,  # kg CO2 per km per passenger
                    "train": 0.041,
                    "subway": 0.038,
                    "tram": 0.029
                },
                "flight": {
                    "domestic_short": 0.255,  # kg CO2 per km
                    "domestic_long": 0.195,
                    "international": 0.150
                },
                "other": {
                    "walking": 0.0,
                    "cycling": 0.0,
                    "scooter": 0.02
                }
            },
            "energy": {
                "electricity": {
                    "grid_average": 0.457,  # kg CO2 per kWh
                    "renewable": 0.024,
                    "coal": 0.820,
                    "natural_gas": 0.350
                },
                "heating": {
                    "natural_gas": 0.185,  # kg CO2 per kWh
                    "heating_oil": 0.245,
                    "propane": 0.214,
                    "electric": 0.457
                },
                "cooling": {
                    "electric": 0.457  # kg CO2 per kWh
                }
            },
            "food": {
                "meat": {
                    "beef": 27.0,  # kg CO2 per kg food
                    "lamb": 24.5,
                    "pork": 7.6,
                    "chicken": 9.9,
                    "turkey": 12.1
                },
                "dairy": {
                    "milk": 3.2,  # kg CO2 per liter
                    "cheese": 13.5,  # kg CO2 per kg
                    "yogurt": 2.2,
                    "butter": 23.8
                },
                "seafood": {
                    "fish_farmed": 13.6,  # kg CO2 per kg
                    "fish_wild": 5.4,
                    "shellfish": 11.3
                },
                "plant_based": {
                    "vegetables": 2.0,  # kg CO2 per kg
                    "fruits": 1.1,
                    "grains": 2.5,
                    "legumes": 0.9,
                    "nuts": 2.3
                },
                "processed": {
                    "bread": 0.9,  # kg CO2 per kg
                    "pasta": 1.4,
                    "rice": 2.7,
                    "coffee": 28.5,  # kg CO2 per kg beans
                    "tea": 6.3
                }
            },
            "consumption": {
                "clothing": {
                    "cotton_shirt": 8.0,  # kg CO2 per item
                    "jeans": 33.4,
                    "shoes": 12.5,
                    "synthetic_garment": 5.5
                },
                "electronics": {
                    "smartphone": 70.0,  # kg CO2 per item
                    "laptop": 300.0,
                    "tablet": 130.0,
                    "tv": 500.0
                },
                "household": {
                    "furniture_item": 150.0,  # kg CO2 per average item
                    "appliance_small": 45.0,
                    "appliance_large": 200.0
                }
            },
            "waste": {
                "landfill": 0.57,  # kg CO2 per kg waste
                "recycling": 0.21,
                "composting": 0.05,
                "incineration": 0.35
            }
        }
    
    def _save_emission_factors(self, path: str, factors: Dict):
        """Save emission factors to JSON file"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(factors, f, indent=2)
    
    def calculate_transportation(
        self, transport_type: str, fuel_type: str,
        distance_km: float, passengers: int = 1,
    ) -> EmissionResult:
        """Calculate emissions from transportation"""
        try:
            factor = self.emission_factors["transportation"][transport_type][fuel_type]
            co2_kg = (factor * distance_km) / passengers         
            return EmissionResult(
                co2_kg=round(co2_kg, 3),
                category="transportation",
                subcategory=transport_type,
                activity=f"{transport_type}_{fuel_type}",
                details={
                    "distance_km": distance_km,
                    "fuel_type": fuel_type,
                    "passengers": passengers,
                    "emission_factor": factor
                }
            )
        except KeyError as e:
            raise ValueError(f"Unknown transportation type or fuel: {e}")
    
    def calculate_energy(self, energy_type: str, source: str, 
                        amount: float, unit: str = "kwh") -> EmissionResult:
        """Calculate emissions from energy consumption"""
        try:
            factor = self.emission_factors["energy"][energy_type][source]
            
            # Convert units if necessary
            if unit.lower() == "mwh":
                amount *= 1000  # Convert MWh to kWh
            elif unit.lower() not in ["kwh", "kw"]:
                raise ValueError(f"Unsupported energy unit: {unit}")
            
            co2_kg = factor * amount
            
            return EmissionResult(
                co2_kg=round(co2_kg, 3),
                category="energy",
                subcategory=energy_type,
                activity=f"{energy_type}_{source}",
                details={
                    "amount": amount,
                    "unit": unit,
                    "source": source,
                    "emission_factor": factor
                }
            )
        except KeyError as e:
            raise ValueError(f"Unknown energy type or source: {e}")
    
    def calculate_food(self, food_type: str, food_item: str, 
                      amount: float, unit: str = "kg", local: bool = False) -> EmissionResult:
        """Calculate emissions from food consumption"""
        try:
            factor = self.emission_factors["food"][food_type][food_item]
            
            # Convert units if necessary
            if unit.lower() == "g":
                amount /= 1000  # Convert grams to kg
            elif unit.lower() == "servings":
                # Approximate serving sizes
                serving_weights = {"beef": 0.15, "chicken": 0.12, "milk": 0.25}
                amount *= serving_weights.get(food_item, 0.1)
            
            # Apply local food discount (typically 10-20% less emissions)
            if local:
                factor *= 0.85
            
            co2_kg = factor * amount
            
            return EmissionResult(
                co2_kg=round(co2_kg, 3),
                category="food",
                subcategory=food_type,
                activity=food_item,
                details={
                    "amount": amount,
                    "unit": unit,
                    "local": local,
                    "emission_factor": factor
                }
            )
        except KeyError as e:
            raise ValueError(f"Unknown food type or item: {e}")
    
    def calculate_consumption(self, item_type: str, item: str, 
                            quantity: int = 1, lifetime_years: Optional[float] = None) -> EmissionResult:
        """Calculate emissions from consumption/purchases"""
        try:
            factor = self.emission_factors["consumption"][item_type][item]
            
            # If lifetime is provided, amortise emissions over the lifetime
            if lifetime_years:
                factor /= lifetime_years
            
            co2_kg = factor * quantity
            
            return EmissionResult(
                co2_kg=round(co2_kg, 3),
                category="consumption",
                subcategory=item_type,
                activity=item,
                details={
                    "quantity": quantity,
                    "lifetime_years": lifetime_years,
                    "emission_factor": factor
                }
            )
        except KeyError as e:
            raise ValueError(f"Unknown consumption item: {e}")
    
    def calculate_waste(self, disposal_method: str, amount_kg: float) -> EmissionResult:
        """Calculate emissions from waste disposal"""
        try:
            factor = self.emission_factors["waste"][disposal_method]
            co2_kg = factor * amount_kg
            
            return EmissionResult(
                co2_kg=round(co2_kg, 3),
                category="waste",
                subcategory=disposal_method,
                activity=disposal_method,
                details={
                    "amount_kg": amount_kg,
                    "disposal_method": disposal_method,
                    "emission_factor": factor
                }
            )
        except KeyError as e:
            raise ValueError(f"Unknown waste disposal method: {e}")
    
    def get_category_factors(self, category: str) -> Dict:
        """Get all emission factors for a specific category"""
        return self.emission_factors.get(category, {})
        
    def estimate_flight_distance(self, origin: str, destination: str) -> float:
        return get_flight_distance_km(origin, destination)
            



# Example usage and testing functions
if __name__ == "__main__":
    # Initialize calculator
    calc = CarbonCalculator()
    
    # Test transportation calculation
    car_trip = calc.calculate_transportation("car", "petrol", 50.0)
    print(f"Car trip: {car_trip.co2_kg} kg CO2")
    
    # Test energy calculation
    electricity = calc.calculate_energy("electricity", "grid_average", 300.0)
    print(f"Electricity: {electricity.co2_kg} kg CO2")
    
    # Test food calculation
    beef_meal = calc.calculate_food("meat", "beef", 0.2, "kg")
    print(f"Beef meal: {beef_meal.co2_kg} kg CO2")
    
    # Test consumption calculation
    smartphone = calc.calculate_consumption("electronics", "smartphone", 1, 3.0)
    print(f"Smartphone (amortized): {smartphone.co2_kg} kg CO2")
    
    # Test waste calculation
    waste = calc.calculate_waste("landfill", 5.0)
    print(f"Waste: {waste.co2_kg} kg CO2")