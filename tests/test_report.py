"""Unit tests for the report module."""

from weather_report.report import (
    find_extremes,
    format_continent_summary,
    format_extremes,
    format_single_report,
    format_summary_table,
    generate_full_report,
)
from weather_report.weather_service import WeatherCondition, WeatherData


def make_weather(
    country: str = "TestLand",
    capital: str = "TestCity",
    continent: str = "TestContinent",
    temp_c: float = 25.0,
    humidity: int = 60,
    wind: float = 15.5,
    condition: WeatherCondition = WeatherCondition.CLEAR,
) -> WeatherData:
    return WeatherData(
        country=country,
        capital=capital,
        continent=continent,
        temperature_celsius=temp_c,
        temperature_fahrenheit=(temp_c * 9 / 5) + 32,
        humidity=humidity,
        wind_speed_kmh=wind,
        condition=condition,
        weather_code=0,
    )


class TestFormatSingleReport:
    def test_contains_country_name(self):
        weather = make_weather(country="India", capital="New Delhi")
        report = format_single_report(weather)
        assert "India" in report

    def test_contains_capital(self):
        weather = make_weather(country="India", capital="New Delhi")
        report = format_single_report(weather)
        assert "New Delhi" in report

    def test_contains_temperature(self):
        weather = make_weather(temp_c=30.0)
        report = format_single_report(weather)
        assert "30.0" in report

    def test_contains_humidity(self):
        weather = make_weather(humidity=75)
        report = format_single_report(weather)
        assert "75%" in report

    def test_contains_wind_speed(self):
        weather = make_weather(wind=20.0)
        report = format_single_report(weather)
        assert "20.0" in report

    def test_contains_condition(self):
        weather = make_weather(condition=WeatherCondition.RAIN)
        report = format_single_report(weather)
        assert "Rain" in report

    def test_contains_continent(self):
        weather = make_weather(continent="Asia")
        report = format_single_report(weather)
        assert "Asia" in report


class TestFormatSummaryTable:
    def test_single_entry(self):
        weather_list = [make_weather(country="India")]
        table = format_summary_table(weather_list)
        assert "India" in table

    def test_header_present(self):
        weather_list = [make_weather()]
        table = format_summary_table(weather_list)
        assert "Country" in table
        assert "Capital" in table
        assert "Temp (C)" in table

    def test_multiple_entries(self):
        weather_list = [
            make_weather(country="India"),
            make_weather(country="Japan"),
            make_weather(country="Germany"),
        ]
        table = format_summary_table(weather_list)
        assert "India" in table
        assert "Japan" in table
        assert "Germany" in table

    def test_empty_list(self):
        table = format_summary_table([])
        assert "Country" in table
        lines = table.strip().split("\n")
        assert len(lines) == 2

    def test_separator_present(self):
        weather_list = [make_weather()]
        table = format_summary_table(weather_list)
        assert "---" in table


class TestFormatContinentSummary:
    def test_single_continent(self):
        weather_list = [
            make_weather(country="India", continent="Asia", temp_c=30.0),
            make_weather(country="Japan", continent="Asia", temp_c=20.0),
        ]
        summary = format_continent_summary(weather_list)
        assert "Asia" in summary
        assert "2 countries" in summary

    def test_multiple_continents(self):
        weather_list = [
            make_weather(continent="Asia", temp_c=30.0),
            make_weather(continent="Europe", temp_c=15.0),
        ]
        summary = format_continent_summary(weather_list)
        assert "Asia" in summary
        assert "Europe" in summary

    def test_avg_temperature_calculated(self):
        weather_list = [
            make_weather(continent="Asia", temp_c=20.0),
            make_weather(continent="Asia", temp_c=30.0),
        ]
        summary = format_continent_summary(weather_list)
        assert "25.0" in summary

    def test_min_max_temperature(self):
        weather_list = [
            make_weather(continent="Europe", temp_c=10.0),
            make_weather(continent="Europe", temp_c=30.0),
        ]
        summary = format_continent_summary(weather_list)
        assert "10.0" in summary
        assert "30.0" in summary


class TestGenerateFullReport:
    def test_contains_header(self):
        weather_list = [make_weather()]
        report = generate_full_report(weather_list)
        assert "WORLD WEATHER REPORT" in report

    def test_contains_country_count(self):
        weather_list = [make_weather(), make_weather(country="Other")]
        report = generate_full_report(weather_list)
        assert "2" in report

    def test_contains_detailed_table(self):
        weather_list = [make_weather(country="India")]
        report = generate_full_report(weather_list)
        assert "DETAILED TABLE" in report
        assert "India" in report

    def test_contains_continent_summary(self):
        weather_list = [make_weather()]
        report = generate_full_report(weather_list)
        assert "CONTINENT SUMMARY" in report

    def test_contains_timestamp(self):
        weather_list = [make_weather()]
        report = generate_full_report(weather_list)
        assert "Generated:" in report

    def test_empty_list(self):
        report = generate_full_report([])
        assert "WORLD WEATHER REPORT" in report
        assert "0" in report


class TestFindExtremes:
    def test_hottest(self):
        weather_list = [
            make_weather(country="Cold", temp_c=-10.0),
            make_weather(country="Hot", temp_c=45.0),
            make_weather(country="Mild", temp_c=20.0),
        ]
        extremes = find_extremes(weather_list)
        assert extremes["hottest"] is not None
        assert extremes["hottest"].country == "Hot"

    def test_coldest(self):
        weather_list = [
            make_weather(country="Cold", temp_c=-10.0),
            make_weather(country="Hot", temp_c=45.0),
        ]
        extremes = find_extremes(weather_list)
        assert extremes["coldest"] is not None
        assert extremes["coldest"].country == "Cold"

    def test_most_humid(self):
        weather_list = [
            make_weather(country="Dry", humidity=10),
            make_weather(country="Humid", humidity=95),
        ]
        extremes = find_extremes(weather_list)
        assert extremes["most_humid"] is not None
        assert extremes["most_humid"].country == "Humid"

    def test_windiest(self):
        weather_list = [
            make_weather(country="Calm", wind=5.0),
            make_weather(country="Windy", wind=80.0),
        ]
        extremes = find_extremes(weather_list)
        assert extremes["windiest"] is not None
        assert extremes["windiest"].country == "Windy"

    def test_empty_list(self):
        extremes = find_extremes([])
        assert extremes["hottest"] is None
        assert extremes["coldest"] is None
        assert extremes["most_humid"] is None
        assert extremes["windiest"] is None

    def test_single_entry(self):
        weather_list = [make_weather(country="Only")]
        extremes = find_extremes(weather_list)
        assert extremes["hottest"] is not None
        assert extremes["hottest"].country == "Only"
        assert extremes["coldest"] is not None
        assert extremes["coldest"].country == "Only"


class TestFormatExtremes:
    def test_contains_hottest(self):
        weather_list = [
            make_weather(country="Hot", temp_c=45.0),
            make_weather(country="Cold", temp_c=-10.0),
        ]
        result = format_extremes(weather_list)
        assert "Hottest" in result
        assert "Hot" in result

    def test_contains_coldest(self):
        weather_list = [
            make_weather(country="Hot", temp_c=45.0),
            make_weather(country="Cold", temp_c=-10.0),
        ]
        result = format_extremes(weather_list)
        assert "Coldest" in result
        assert "Cold" in result

    def test_contains_most_humid(self):
        weather_list = [make_weather(country="Humid", humidity=95)]
        result = format_extremes(weather_list)
        assert "Most Humid" in result
        assert "Humid" in result

    def test_contains_windiest(self):
        weather_list = [make_weather(country="Windy", wind=80.0)]
        result = format_extremes(weather_list)
        assert "Windiest" in result

    def test_empty_list(self):
        result = format_extremes([])
        assert "No data available" in result

    def test_weather_extremes_header(self):
        weather_list = [make_weather()]
        result = format_extremes(weather_list)
        assert "WEATHER EXTREMES" in result
