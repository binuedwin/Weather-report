"""Unit tests for the cities module."""

from weather_report.cities import (
    City,
    Region,
    get_all_cities,
    get_all_regions,
    get_capital_cities,
    get_cities_by_country,
    get_city_by_name,
    get_regions_by_continent,
    get_regions_by_country,
)


class TestCityDataclass:
    def test_city_creation(self):
        city = City("TestCity", "TestCountry", "TestRegion", 10.0, 20.0, True)
        assert city.name == "TestCity"
        assert city.country == "TestCountry"
        assert city.region == "TestRegion"
        assert city.latitude == 10.0
        assert city.longitude == 20.0
        assert city.is_capital is True

    def test_city_is_frozen(self):
        city = City("TestCity", "TestCountry", "TestRegion", 10.0, 20.0, False)
        import pytest

        with pytest.raises(AttributeError):
            city.name = "Changed"

    def test_city_equality(self):
        c1 = City("TestCity", "TestCountry", "TestRegion", 10.0, 20.0, True)
        c2 = City("TestCity", "TestCountry", "TestRegion", 10.0, 20.0, True)
        assert c1 == c2


class TestRegionDataclass:
    def test_region_creation(self):
        region = Region("TestRegion", "TestCountry", "TestContinent")
        assert region.name == "TestRegion"
        assert region.country == "TestCountry"
        assert region.continent == "TestContinent"

    def test_region_is_frozen(self):
        region = Region("TestRegion", "TestCountry", "TestContinent")
        import pytest

        with pytest.raises(AttributeError):
            region.name = "Changed"


class TestGetAllCities:
    def test_returns_list(self):
        cities = get_all_cities()
        assert isinstance(cities, list)

    def test_not_empty(self):
        cities = get_all_cities()
        assert len(cities) > 0

    def test_all_items_are_city_instances(self):
        for city in get_all_cities():
            assert isinstance(city, City)

    def test_returns_copy(self):
        c1 = get_all_cities()
        c2 = get_all_cities()
        assert c1 is not c2

    def test_all_cities_have_valid_latitude(self):
        for city in get_all_cities():
            assert -90 <= city.latitude <= 90, f"{city.name} has invalid latitude"

    def test_all_cities_have_valid_longitude(self):
        for city in get_all_cities():
            assert -180 <= city.longitude <= 180, f"{city.name} has invalid longitude"

    def test_all_cities_have_nonempty_fields(self):
        for city in get_all_cities():
            assert city.name
            assert city.country
            assert city.region


class TestGetCitiesByCountry:
    def test_find_indian_cities(self):
        cities = get_cities_by_country("India")
        assert len(cities) > 0
        for c in cities:
            assert c.country == "India"

    def test_case_insensitive(self):
        cities = get_cities_by_country("india")
        assert len(cities) > 0

    def test_nonexistent_country(self):
        cities = get_cities_by_country("Atlantis")
        assert cities == []

    def test_us_cities(self):
        cities = get_cities_by_country("United States")
        assert len(cities) >= 5


class TestGetCapitalCities:
    def test_returns_only_capitals(self):
        capitals = get_capital_cities()
        for c in capitals:
            assert c.is_capital is True

    def test_not_empty(self):
        capitals = get_capital_cities()
        assert len(capitals) > 0

    def test_known_capitals_present(self):
        capitals = get_capital_cities()
        capital_names = [c.name for c in capitals]
        assert "Tokyo" in capital_names
        assert "London" in capital_names
        assert "New Delhi" in capital_names


class TestGetCityByName:
    def test_find_existing_city(self):
        city = get_city_by_name("Tokyo")
        assert city is not None
        assert city.country == "Japan"

    def test_case_insensitive(self):
        city = get_city_by_name("tokyo")
        assert city is not None
        assert city.name == "Tokyo"

    def test_nonexistent_city(self):
        city = get_city_by_name("NoSuchCity")
        assert city is None

    def test_find_london(self):
        city = get_city_by_name("London")
        assert city is not None
        assert city.country == "United Kingdom"
        assert city.is_capital is True


class TestGetAllRegions:
    def test_returns_list(self):
        regions = get_all_regions()
        assert isinstance(regions, list)

    def test_not_empty(self):
        regions = get_all_regions()
        assert len(regions) > 0

    def test_all_items_are_region_instances(self):
        for region in get_all_regions():
            assert isinstance(region, Region)

    def test_returns_copy(self):
        r1 = get_all_regions()
        r2 = get_all_regions()
        assert r1 is not r2


class TestGetRegionsByCountry:
    def test_find_us_regions(self):
        regions = get_regions_by_country("United States")
        assert len(regions) > 0
        for r in regions:
            assert r.country == "United States"

    def test_case_insensitive(self):
        regions = get_regions_by_country("united states")
        assert len(regions) > 0

    def test_nonexistent_country(self):
        regions = get_regions_by_country("Atlantis")
        assert regions == []

    def test_india_regions(self):
        regions = get_regions_by_country("India")
        assert len(regions) >= 5


class TestGetRegionsByContinent:
    def test_european_regions(self):
        regions = get_regions_by_continent("Europe")
        assert len(regions) > 0
        for r in regions:
            assert r.continent == "Europe"

    def test_case_insensitive(self):
        regions = get_regions_by_continent("europe")
        assert len(regions) > 0

    def test_nonexistent_continent(self):
        regions = get_regions_by_continent("Narnia")
        assert regions == []

    def test_asian_regions(self):
        regions = get_regions_by_continent("Asia")
        assert len(regions) > 0
