from geogpt.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

expected_result = {
    "name": "Saint-Remy-en-Bouzemont-Saint-Genest-et-Isson",
    "country": "FR",
    "longitude": 4.65,
    "latitude": 48.63333,
    "timezone": "Europe/Paris",
}

def test_get_geoname_from_address():
    address = "6 Rte de Drosnay, 51290 Saint-Remy-en-Bouzemont-Saint-Genest-et-Isson"
    response = client.get(f"/{address}")

    assert response.status_code == 200

    assert response.json() == expected_result

def test_get_geoname_from_address_alterate():
    address = "6 Rte de Drosay, 51290 Saint-Rmy-en-Bouzmont-Saint-Genet-et-Ison"
    response = client.get(f"/{address}")

    assert response.status_code == 200

    assert response.json() == expected_result
