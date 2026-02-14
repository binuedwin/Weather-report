"""Unit tests for the FastAPI REST API."""

from fastapi.testclient import TestClient

from weather_report.api import app

client = TestClient(app)


class TestRootEndpoint:
    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_message(self):
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "World Geography API" in data["message"]

    def test_root_contains_docs_link(self):
        response = client.get("/")
        data = response.json()
        assert "docs" in data


class TestCountriesEndpoint:
    def test_list_all_countries(self):
        response = client.get("/countries")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "countries" in data
        assert data["count"] >= 190

    def test_country_has_required_fields(self):
        response = client.get("/countries")
        data = response.json()
        country = data["countries"][0]
        assert "name" in country
        assert "capital" in country
        assert "continent" in country
        assert "latitude" in country
        assert "longitude" in country

    def test_filter_by_continent(self):
        response = client.get("/countries?continent=Europe")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
        for c in data["countries"]:
            assert c["continent"] == "Europe"

    def test_filter_by_invalid_continent(self):
        response = client.get("/countries?continent=Narnia")
        assert response.status_code == 404

    def test_get_single_country(self):
        response = client.get("/countries/India")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "India"
        assert data["capital"] == "New Delhi"
        assert "cities" in data
        assert "regions" in data

    def test_get_nonexistent_country(self):
        response = client.get("/countries/Atlantis")
        assert response.status_code == 404

    def test_country_detail_includes_cities(self):
        response = client.get("/countries/Japan")
        data = response.json()
        assert len(data["cities"]) > 0
        city_names = [c["name"] for c in data["cities"]]
        assert "Tokyo" in city_names

    def test_country_detail_includes_regions(self):
        response = client.get("/countries/United States")
        data = response.json()
        assert len(data["regions"]) > 0


class TestCitiesEndpoint:
    def test_list_all_cities(self):
        response = client.get("/cities")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "cities" in data
        assert data["count"] > 0

    def test_city_has_required_fields(self):
        response = client.get("/cities")
        data = response.json()
        city = data["cities"][0]
        assert "name" in city
        assert "country" in city
        assert "region" in city
        assert "latitude" in city
        assert "longitude" in city
        assert "is_capital" in city

    def test_filter_by_country(self):
        response = client.get("/cities?country=India")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
        for c in data["cities"]:
            assert c["country"] == "India"

    def test_filter_by_invalid_country(self):
        response = client.get("/cities?country=Atlantis")
        assert response.status_code == 404

    def test_capitals_only(self):
        response = client.get("/cities?capitals_only=true")
        assert response.status_code == 200
        data = response.json()
        for c in data["cities"]:
            assert c["is_capital"] is True

    def test_get_single_city(self):
        response = client.get("/cities/Tokyo")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Tokyo"
        assert data["country"] == "Japan"

    def test_get_nonexistent_city(self):
        response = client.get("/cities/NoSuchCity")
        assert response.status_code == 404

    def test_get_london(self):
        response = client.get("/cities/London")
        data = response.json()
        assert data["country"] == "United Kingdom"
        assert data["is_capital"] is True


class TestRegionsEndpoint:
    def test_list_all_regions(self):
        response = client.get("/regions")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "regions" in data
        assert data["count"] > 0

    def test_region_has_required_fields(self):
        response = client.get("/regions")
        data = response.json()
        region = data["regions"][0]
        assert "name" in region
        assert "country" in region
        assert "continent" in region

    def test_filter_by_country(self):
        response = client.get("/regions?country=India")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
        for r in data["regions"]:
            assert r["country"] == "India"

    def test_filter_by_continent(self):
        response = client.get("/regions?continent=Europe")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
        for r in data["regions"]:
            assert r["continent"] == "Europe"

    def test_filter_by_invalid_country(self):
        response = client.get("/regions?country=Atlantis")
        assert response.status_code == 404

    def test_filter_by_invalid_continent(self):
        response = client.get("/regions?continent=Narnia")
        assert response.status_code == 404


class TestContinentsEndpoint:
    def test_list_continents(self):
        response = client.get("/continents")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "continents" in data
        assert data["count"] >= 6

    def test_continent_has_required_fields(self):
        response = client.get("/continents")
        data = response.json()
        continent = data["continents"][0]
        assert "name" in continent
        assert "country_count" in continent
        assert "region_count" in continent

    def test_known_continents_present(self):
        response = client.get("/continents")
        data = response.json()
        names = [c["name"] for c in data["continents"]]
        assert "Africa" in names
        assert "Asia" in names
        assert "Europe" in names
