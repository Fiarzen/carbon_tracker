from unittest.mock import patch
from src import geo_utils

@patch("src.geo_utils.client.directions")
@patch("src.geo_utils.geocode_city")
def test_get_flight_distance_km(mock_geocode, mock_directions):
    mock_geocode.side_effect = [[13.405, 52.52], [-3.703, 40.416]]  # Berlin → Madrid
    mock_directions.return_value = {
        "features": [{
            "properties": {
                "segments": [{"distance": 2000000}]  # 2000 km
            }
        }]
    }

    dist = geo_utils.get_flight_distance_km("Berlin", "Madrid")
    assert dist == 2000.0