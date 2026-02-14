"""Weather service module for fetching weather data via Open-Meteo API."""

from dataclasses import dataclass
from enum import Enum

import requests

from weather_report.countries import Country

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10


class WeatherCondition(Enum):
    CLEAR = "Clear"
    PARTLY_CLOUDY = "Partly Cloudy"
    OVERCAST = "Overcast"
    FOG = "Fog"
    DRIZZLE = "Drizzle"
    RAIN = "Rain"
    SNOW = "Snow"
    THUNDERSTORM = "Thunderstorm"
    UNKNOWN = "Unknown"


WMO_CODE_MAP: dict[int, WeatherCondition] = {
    0: WeatherCondition.CLEAR,
    1: WeatherCondition.CLEAR,
    2: WeatherCondition.PARTLY_CLOUDY,
    3: WeatherCondition.OVERCAST,
    45: WeatherCondition.FOG,
    48: WeatherCondition.FOG,
    51: WeatherCondition.DRIZZLE,
    53: WeatherCondition.DRIZZLE,
    55: WeatherCondition.DRIZZLE,
    56: WeatherCondition.DRIZZLE,
    57: WeatherCondition.DRIZZLE,
    61: WeatherCondition.RAIN,
    63: WeatherCondition.RAIN,
    65: WeatherCondition.RAIN,
    66: WeatherCondition.RAIN,
    67: WeatherCondition.RAIN,
    71: WeatherCondition.SNOW,
    73: WeatherCondition.SNOW,
    75: WeatherCondition.SNOW,
    77: WeatherCondition.SNOW,
    80: WeatherCondition.RAIN,
    81: WeatherCondition.RAIN,
    82: WeatherCondition.RAIN,
    85: WeatherCondition.SNOW,
    86: WeatherCondition.SNOW,
    95: WeatherCondition.THUNDERSTORM,
    96: WeatherCondition.THUNDERSTORM,
    99: WeatherCondition.THUNDERSTORM,
}


@dataclass
class WeatherData:
    country: str
    capital: str
    continent: str
    temperature_celsius: float
    temperature_fahrenheit: float
    humidity: int
    wind_speed_kmh: float
    condition: WeatherCondition
    weather_code: int

    @property
    def temperature_display(self) -> str:
        return f"{self.temperature_celsius:.1f}°C / {self.temperature_fahrenheit:.1f}°F"


class WeatherServiceError(Exception):
    pass


def celsius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9 / 5) + 32


def interpret_weather_code(code: int) -> WeatherCondition:
    return WMO_CODE_MAP.get(code, WeatherCondition.UNKNOWN)


def fetch_weather(country: Country) -> WeatherData:
    params = {
        "latitude": country.latitude,
        "longitude": country.longitude,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
    }

    try:
        response = requests.get(OPEN_METEO_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        raise WeatherServiceError(
            f"Failed to fetch weather for {country.name} ({country.capital}): {e}"
        ) from e

    try:
        data = response.json()
        current = data["current"]
    except (ValueError, KeyError) as e:
        raise WeatherServiceError(
            f"Invalid response for {country.name} ({country.capital}): {e}"
        ) from e

    temp_c = float(current["temperature_2m"])
    weather_code = int(current["weather_code"])

    return WeatherData(
        country=country.name,
        capital=country.capital,
        continent=country.continent,
        temperature_celsius=temp_c,
        temperature_fahrenheit=celsius_to_fahrenheit(temp_c),
        humidity=int(current["relative_humidity_2m"]),
        wind_speed_kmh=float(current["wind_speed_10m"]),
        condition=interpret_weather_code(weather_code),
        weather_code=weather_code,
    )


def fetch_weather_batch(
    countries: list[Country],
    on_error: str = "skip",
) -> list[WeatherData]:
    results: list[WeatherData] = []
    for country in countries:
        try:
            weather = fetch_weather(country)
            results.append(weather)
        except WeatherServiceError:
            if on_error == "raise":
                raise
    return results
