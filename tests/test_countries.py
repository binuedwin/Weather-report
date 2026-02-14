"""Unit tests for the countries module."""

import pytest

from weather_report.countries import (
    Country,
    get_all_continents,
    get_all_countries,
    get_countries_by_continent,
    get_country_by_name,
)


class TestCountryDataclass:
    def test_country_creation(self):
        country = Country("TestLand", "TestCity", 10.0, 20.0, "TestContinent")
        assert country.name == "TestLand"
        assert country.capital == "TestCity"
        assert country.latitude == 10.0
        assert country.longitude == 20.0
        assert country.continent == "TestContinent"

    def test_country_is_frozen(self):
        country = Country("TestLand", "TestCity", 10.0, 20.0, "TestContinent")
        with pytest.raises(AttributeError):
            country.name = "Changed"

    def test_country_equality(self):
        c1 = Country("TestLand", "TestCity", 10.0, 20.0, "TestContinent")
        c2 = Country("TestLand", "TestCity", 10.0, 20.0, "TestContinent")
        assert c1 == c2

    def test_country_inequality(self):
        c1 = Country("TestLand", "TestCity", 10.0, 20.0, "TestContinent")
        c2 = Country("OtherLand", "OtherCity", 30.0, 40.0, "OtherContinent")
        assert c1 != c2


class TestGetAllCountries:
    def test_returns_list(self):
        countries = get_all_countries()
        assert isinstance(countries, list)

    def test_not_empty(self):
        countries = get_all_countries()
        assert len(countries) > 0

    def test_has_at_least_190_countries(self):
        countries = get_all_countries()
        assert len(countries) >= 190

    def test_all_items_are_country_instances(self):
        countries = get_all_countries()
        for country in countries:
            assert isinstance(country, Country)

    def test_returns_copy(self):
        countries1 = get_all_countries()
        countries2 = get_all_countries()
        assert countries1 is not countries2

    def test_all_countries_have_valid_latitude(self):
        for country in get_all_countries():
            assert -90 <= country.latitude <= 90, f"{country.name} has invalid latitude"

    def test_all_countries_have_valid_longitude(self):
        for country in get_all_countries():
            assert -180 <= country.longitude <= 180, f"{country.name} has invalid longitude"

    def test_all_countries_have_nonempty_fields(self):
        for country in get_all_countries():
            assert country.name, "Country has empty name"
            assert country.capital, f"{country.name} has empty capital"
            assert country.continent, f"{country.name} has empty continent"

    def test_no_duplicate_country_names(self):
        countries = get_all_countries()
        names = [c.name for c in countries]
        assert len(names) == len(set(names))


class TestGetCountryByName:
    def test_find_existing_country(self):
        country = get_country_by_name("India")
        assert country is not None
        assert country.name == "India"
        assert country.capital == "New Delhi"

    def test_find_country_case_insensitive(self):
        country = get_country_by_name("india")
        assert country is not None
        assert country.name == "India"

    def test_find_country_uppercase(self):
        country = get_country_by_name("JAPAN")
        assert country is not None
        assert country.name == "Japan"

    def test_find_nonexistent_country(self):
        country = get_country_by_name("Atlantis")
        assert country is None

    def test_find_empty_string(self):
        country = get_country_by_name("")
        assert country is None

    def test_find_united_states(self):
        country = get_country_by_name("United States")
        assert country is not None
        assert country.capital == "Washington D.C."

    def test_find_united_kingdom(self):
        country = get_country_by_name("United Kingdom")
        assert country is not None
        assert country.capital == "London"

    def test_find_country_with_special_characters(self):
        country = get_country_by_name("Cabo Verde")
        assert country is not None
        assert country.capital == "Praia"


class TestGetCountriesByContinent:
    def test_get_european_countries(self):
        countries = get_countries_by_continent("Europe")
        assert len(countries) > 0
        for c in countries:
            assert c.continent == "Europe"

    def test_get_african_countries(self):
        countries = get_countries_by_continent("Africa")
        assert len(countries) > 0
        for c in countries:
            assert c.continent == "Africa"

    def test_case_insensitive(self):
        countries = get_countries_by_continent("asia")
        assert len(countries) > 0
        for c in countries:
            assert c.continent == "Asia"

    def test_nonexistent_continent(self):
        countries = get_countries_by_continent("Narnia")
        assert countries == []

    def test_all_continents_have_countries(self):
        continents = get_all_continents()
        for continent in continents:
            countries = get_countries_by_continent(continent)
            assert len(countries) > 0, f"{continent} has no countries"

    def test_total_by_continent_equals_all(self):
        total = sum(len(get_countries_by_continent(c)) for c in get_all_continents())
        assert total == len(get_all_countries())


class TestGetAllContinents:
    def test_returns_list(self):
        continents = get_all_continents()
        assert isinstance(continents, list)

    def test_is_sorted(self):
        continents = get_all_continents()
        assert continents == sorted(continents)

    def test_known_continents_present(self):
        continents = get_all_continents()
        expected = ["Africa", "Asia", "Europe", "North America", "Oceania", "South America"]
        for exp in expected:
            assert exp in continents

    def test_no_duplicates(self):
        continents = get_all_continents()
        assert len(continents) == len(set(continents))
