"""
Unit tests for CarbonCalculator using pytest

"""
import pytest
from carbon_tracker.calculator import CarbonCalculator, EmissionResult
from unittest.mock import patch, MagicMock

@patch("src.calculator.get_flight_distance_km")
def test_estimate_flight_distance(mock_distance_func):
    mock_distance_func.return_value = 1200.0

    calc = CarbonCalculator()
    distance = calc.estimate_flight_distance("Berlin", "Madrid")

    assert distance == 1200.0
    mock_distance_func.assert_called_once_with("Berlin", "Madrid")

@pytest.fixture(scope="module")
def calculator():
    """Initialise the calculator once per test module"""
    return CarbonCalculator()


def test_transportation_car_petrol(calculator):
    result = calculator.calculate_transportation("car", "petrol", distance_km=100, passengers=2)
    assert isinstance(result, EmissionResult)
    assert result.co2_kg == pytest.approx(20.2, 0.01)
    assert result.category == "transportation"


def test_transportation_invalid_type(calculator):
    with pytest.raises(ValueError):
        calculator.calculate_transportation("hoverboard", "plasma", 50)


def test_energy_electricity_grid_average(calculator):
    result = calculator.calculate_energy("electricity", "grid_average", amount=250)
    assert result.co2_kg == pytest.approx(114.25, 0.01)
    assert result.subcategory == "electricity"


def test_energy_invalid_unit(calculator):
    with pytest.raises(ValueError):
        calculator.calculate_energy("electricity", "grid_average", amount=100, unit="joules")


def test_food_beef_kg(calculator):
    result = calculator.calculate_food("meat", "beef", amount=0.5, unit="kg")
    assert result.co2_kg == pytest.approx(13.5, 0.01)
    assert result.details["unit"] == "kg"


def test_food_servings_and_local_discount(calculator):
    result = calculator.calculate_food("meat", "beef", amount=2, unit="servings", local=True)
    # 2 servings * 0.15 kg each = 0.3 kg, factor reduced to 22.95
    expected_emissions = 0.3 * (27.0 * 0.85)
    assert result.co2_kg == pytest.approx(expected_emissions, 0.01)
    assert result.details["local"] is True


def test_food_invalid_item(calculator):
    with pytest.raises(ValueError):
        calculator.calculate_food("meat", "unicorn", 1.0)


def test_consumption_smartphone_amortised(calculator):
    result = calculator.calculate_consumption("electronics", "smartphone", quantity=1, lifetime_years=5)
    expected = 70 / 5
    assert result.co2_kg == pytest.approx(expected, 0.01)
    assert result.activity == "smartphone"


def test_consumption_invalid_item(calculator):
    with pytest.raises(ValueError):
        calculator.calculate_consumption("electronics", "telepathy_chip", 1)


def test_waste_landfill(calculator):
    result = calculator.calculate_waste("landfill", amount_kg=10)
    assert result.co2_kg == pytest.approx(5.7, 0.01)
    assert result.subcategory == "landfill"


def test_waste_invalid_method(calculator):
    with pytest.raises(ValueError):
        calculator.calculate_waste("catapult", 3.0)

