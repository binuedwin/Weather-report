"""Unit tests for the weather service module."""

from unittest.mock import MagicMock, patch

import pytest

from weather_report.countries import Country
from weather_report.weather_service import (
    WeatherCondition,
    WeatherData,
    WeatherServiceError,
    celsius_to_fahrenheit,
    fetch_weather,
    fetch_weather_batch,
    interpret_weather_code,
)

SAMPLE_COUNTRY = Country("TestLand", "TestCity", 10.0, 20.0, "TestContinent")

SAMPLE_API_RESPONSE = {
    "current": {
        "temperature_2m": 25.0,
        "relative_humidity_2m": 60,
        "weather_code": 0,
        "wind_speed_10m": 15.5,
    }
}


class TestCelsiusToFahrenheit:
    def test_zero(self):
        assert celsius_to_fahrenheit(0) == 32.0

    def test_hundred(self):
        assert celsius_to_fahrenheit(100) == 212.0

    def test_negative(self):
        assert celsius_to_fahrenheit(-40) == -40.0

    def test_room_temperature(self):
        result = celsius_to_fahrenheit(25)
        assert abs(result - 77.0) < 0.01

    def test_body_temperature(self):
        result = celsius_to_fahrenheit(37)
        assert abs(result - 98.6) < 0.01

    def test_freezing_point(self):
        assert celsius_to_fahrenheit(0) == 32.0


class TestInterpretWeatherCode:
    def test_clear_sky(self):
        assert interpret_weather_code(0) == WeatherCondition.CLEAR

    def test_mainly_clear(self):
        assert interpret_weather_code(1) == WeatherCondition.CLEAR

    def test_partly_cloudy(self):
        assert interpret_weather_code(2) == WeatherCondition.PARTLY_CLOUDY

    def test_overcast(self):
        assert interpret_weather_code(3) == WeatherCondition.OVERCAST

    def test_fog(self):
        assert interpret_weather_code(45) == WeatherCondition.FOG
        assert interpret_weather_code(48) == WeatherCondition.FOG

    def test_drizzle(self):
        for code in [51, 53, 55, 56, 57]:
            assert interpret_weather_code(code) == WeatherCondition.DRIZZLE

    def test_rain(self):
        for code in [61, 63, 65, 66, 67, 80, 81, 82]:
            assert interpret_weather_code(code) == WeatherCondition.RAIN

    def test_snow(self):
        for code in [71, 73, 75, 77, 85, 86]:
            assert interpret_weather_code(code) == WeatherCondition.SNOW

    def test_thunderstorm(self):
        for code in [95, 96, 99]:
            assert interpret_weather_code(code) == WeatherCondition.THUNDERSTORM

    def test_unknown_code(self):
        assert interpret_weather_code(999) == WeatherCondition.UNKNOWN

    def test_negative_code(self):
        assert interpret_weather_code(-1) == WeatherCondition.UNKNOWN


class TestWeatherData:
    def test_creation(self):
        data = WeatherData(
            country="TestLand",
            capital="TestCity",
            continent="TestContinent",
            temperature_celsius=25.0,
            temperature_fahrenheit=77.0,
            humidity=60,
            wind_speed_kmh=15.5,
            condition=WeatherCondition.CLEAR,
            weather_code=0,
        )
        assert data.country == "TestLand"
        assert data.temperature_celsius == 25.0
        assert data.humidity == 60

    def test_temperature_display(self):
        data = WeatherData(
            country="TestLand",
            capital="TestCity",
            continent="TestContinent",
            temperature_celsius=25.0,
            temperature_fahrenheit=77.0,
            humidity=60,
            wind_speed_kmh=15.5,
            condition=WeatherCondition.CLEAR,
            weather_code=0,
        )
        assert data.temperature_display == "25.0°C / 77.0°F"

    def test_temperature_display_negative(self):
        data = WeatherData(
            country="TestLand",
            capital="TestCity",
            continent="TestContinent",
            temperature_celsius=-10.5,
            temperature_fahrenheit=13.1,
            humidity=80,
            wind_speed_kmh=20.0,
            condition=WeatherCondition.SNOW,
            weather_code=71,
        )
        assert data.temperature_display == "-10.5°C / 13.1°F"


class TestFetchWeather:
    @patch("weather_report.weather_service.requests.get")
    def test_successful_fetch(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_API_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_weather(SAMPLE_COUNTRY)

        assert result.country == "TestLand"
        assert result.capital == "TestCity"
        assert result.temperature_celsius == 25.0
        assert abs(result.temperature_fahrenheit - 77.0) < 0.01
        assert result.humidity == 60
        assert result.wind_speed_kmh == 15.5
        assert result.condition == WeatherCondition.CLEAR

    @patch("weather_report.weather_service.requests.get")
    def test_api_call_parameters(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_API_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        fetch_weather(SAMPLE_COUNTRY)

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args.kwargs["params"]["latitude"] == 10.0
        assert call_args.kwargs["params"]["longitude"] == 20.0

    @patch("weather_report.weather_service.requests.get")
    def test_network_error_raises(self, mock_get):
        from requests.exceptions import ConnectionError

        mock_get.side_effect = ConnectionError("Network error")

        with pytest.raises(WeatherServiceError) as exc_info:
            fetch_weather(SAMPLE_COUNTRY)
        assert "TestLand" in str(exc_info.value)

    @patch("weather_report.weather_service.requests.get")
    def test_http_error_raises(self, mock_get):
        from requests.exceptions import HTTPError

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")
        mock_get.return_value = mock_response

        with pytest.raises(WeatherServiceError):
            fetch_weather(SAMPLE_COUNTRY)

    @patch("weather_report.weather_service.requests.get")
    def test_invalid_json_raises(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        with pytest.raises(WeatherServiceError):
            fetch_weather(SAMPLE_COUNTRY)

    @patch("weather_report.weather_service.requests.get")
    def test_missing_key_raises(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"unexpected": "data"}
        mock_get.return_value = mock_response

        with pytest.raises(WeatherServiceError):
            fetch_weather(SAMPLE_COUNTRY)

    @patch("weather_report.weather_service.requests.get")
    def test_rain_condition(self, mock_get):
        rain_response = {
            "current": {
                "temperature_2m": 15.0,
                "relative_humidity_2m": 90,
                "weather_code": 63,
                "wind_speed_10m": 25.0,
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = rain_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_weather(SAMPLE_COUNTRY)
        assert result.condition == WeatherCondition.RAIN

    @patch("weather_report.weather_service.requests.get")
    def test_snow_condition(self, mock_get):
        snow_response = {
            "current": {
                "temperature_2m": -5.0,
                "relative_humidity_2m": 85,
                "weather_code": 73,
                "wind_speed_10m": 10.0,
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = snow_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_weather(SAMPLE_COUNTRY)
        assert result.condition == WeatherCondition.SNOW
        assert result.temperature_celsius == -5.0


class TestFetchWeatherBatch:
    @patch("weather_report.weather_service.fetch_weather")
    def test_batch_success(self, mock_fetch):
        mock_fetch.return_value = WeatherData(
            country="TestLand",
            capital="TestCity",
            continent="TestContinent",
            temperature_celsius=25.0,
            temperature_fahrenheit=77.0,
            humidity=60,
            wind_speed_kmh=15.5,
            condition=WeatherCondition.CLEAR,
            weather_code=0,
        )

        countries = [SAMPLE_COUNTRY, SAMPLE_COUNTRY]
        results = fetch_weather_batch(countries)
        assert len(results) == 2

    @patch("weather_report.weather_service.fetch_weather")
    def test_batch_skip_errors(self, mock_fetch):
        mock_fetch.side_effect = [
            WeatherData(
                country="TestLand",
                capital="TestCity",
                continent="TestContinent",
                temperature_celsius=25.0,
                temperature_fahrenheit=77.0,
                humidity=60,
                wind_speed_kmh=15.5,
                condition=WeatherCondition.CLEAR,
                weather_code=0,
            ),
            WeatherServiceError("API error"),
        ]

        countries = [SAMPLE_COUNTRY, SAMPLE_COUNTRY]
        results = fetch_weather_batch(countries, on_error="skip")
        assert len(results) == 1

    @patch("weather_report.weather_service.fetch_weather")
    def test_batch_raise_errors(self, mock_fetch):
        mock_fetch.side_effect = WeatherServiceError("API error")

        countries = [SAMPLE_COUNTRY]
        with pytest.raises(WeatherServiceError):
            fetch_weather_batch(countries, on_error="raise")

    @patch("weather_report.weather_service.fetch_weather")
    def test_batch_empty_list(self, mock_fetch):
        results = fetch_weather_batch([])
        assert results == []
        mock_fetch.assert_not_called()


class TestWeatherConditionEnum:
    def test_all_conditions_have_string_values(self):
        for condition in WeatherCondition:
            assert isinstance(condition.value, str)
            assert len(condition.value) > 0

    def test_condition_values_unique(self):
        values = [c.value for c in WeatherCondition]
        assert len(values) == len(set(values))
