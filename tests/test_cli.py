"""Unit tests for the CLI module."""

from unittest.mock import patch

from weather_report.cli import (
    build_parser,
    cmd_continent,
    cmd_country,
    cmd_list_continents,
    cmd_list_countries,
)
from weather_report.weather_service import WeatherCondition, WeatherData, WeatherServiceError

SAMPLE_WEATHER = WeatherData(
    country="India",
    capital="New Delhi",
    continent="Asia",
    temperature_celsius=35.0,
    temperature_fahrenheit=95.0,
    humidity=50,
    wind_speed_kmh=12.0,
    condition=WeatherCondition.CLEAR,
    weather_code=0,
)


class TestBuildParser:
    def test_parser_creation(self):
        parser = build_parser()
        assert parser is not None

    def test_parse_all_command(self):
        parser = build_parser()
        args = parser.parse_args(["all"])
        assert args.command == "all"

    def test_parse_country_command(self):
        parser = build_parser()
        args = parser.parse_args(["country", "India"])
        assert args.command == "country"
        assert args.name == "India"

    def test_parse_continent_command(self):
        parser = build_parser()
        args = parser.parse_args(["continent", "Asia"])
        assert args.command == "continent"
        assert args.name == "Asia"

    def test_parse_list_countries(self):
        parser = build_parser()
        args = parser.parse_args(["list-countries"])
        assert args.command == "list-countries"

    def test_parse_list_continents(self):
        parser = build_parser()
        args = parser.parse_args(["list-continents"])
        assert args.command == "list-continents"

    def test_no_command(self):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.command is None


class TestCmdCountry:
    @patch("weather_report.cli.fetch_weather")
    def test_valid_country(self, mock_fetch, capsys):
        mock_fetch.return_value = SAMPLE_WEATHER
        result = cmd_country("India")
        assert result == 0
        captured = capsys.readouterr()
        assert "India" in captured.out

    def test_invalid_country(self, capsys):
        result = cmd_country("Atlantis")
        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err

    @patch("weather_report.cli.fetch_weather")
    def test_api_error(self, mock_fetch, capsys):
        mock_fetch.side_effect = WeatherServiceError("API failed")
        result = cmd_country("India")
        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err


class TestCmdContinent:
    @patch("weather_report.cli.fetch_weather_batch")
    def test_valid_continent(self, mock_batch, capsys):
        mock_batch.return_value = [SAMPLE_WEATHER]
        result = cmd_continent("Asia")
        assert result == 0
        captured = capsys.readouterr()
        assert "Asia" in captured.out

    def test_invalid_continent(self, capsys):
        result = cmd_continent("Narnia")
        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err


class TestCmdListCountries:
    def test_list_countries(self, capsys):
        result = cmd_list_countries()
        assert result == 0
        captured = capsys.readouterr()
        assert "India" in captured.out
        assert "Japan" in captured.out


class TestCmdListContinents:
    def test_list_continents(self, capsys):
        result = cmd_list_continents()
        assert result == 0
        captured = capsys.readouterr()
        assert "Africa" in captured.out
        assert "Asia" in captured.out
        assert "Europe" in captured.out
