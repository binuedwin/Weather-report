"""Weather report generator and formatter module."""

from datetime import datetime, timezone

from weather_report.weather_service import WeatherData


def format_single_report(weather: WeatherData) -> str:
    lines = [
        f"  Country     : {weather.country}",
        f"  Capital     : {weather.capital}",
        f"  Continent   : {weather.continent}",
        f"  Temperature : {weather.temperature_display}",
        f"  Humidity    : {weather.humidity}%",
        f"  Wind Speed  : {weather.wind_speed_kmh:.1f} km/h",
        f"  Condition   : {weather.condition.value}",
    ]
    return "\n".join(lines)


def format_summary_table(weather_list: list[WeatherData]) -> str:
    header = (
        f"{'Country':<40} {'Capital':<25} {'Temp (C)':<10} {'Temp (F)':<10} "
        f"{'Humidity':<10} {'Wind (km/h)':<12} {'Condition':<15}"
    )
    separator = "-" * len(header)
    rows = []
    for w in weather_list:
        row = (
            f"{w.country:<40} {w.capital:<25} {w.temperature_celsius:<10.1f} "
            f"{w.temperature_fahrenheit:<10.1f} {w.humidity:<10} "
            f"{w.wind_speed_kmh:<12.1f} {w.condition.value:<15}"
        )
        rows.append(row)
    return "\n".join([header, separator] + rows)


def format_continent_summary(weather_list: list[WeatherData]) -> str:
    continent_data: dict[str, list[WeatherData]] = {}
    for w in weather_list:
        continent_data.setdefault(w.continent, []).append(w)

    lines = []
    for continent in sorted(continent_data.keys()):
        data = continent_data[continent]
        temps = [w.temperature_celsius for w in data]
        avg_temp = sum(temps) / len(temps)
        min_temp = min(temps)
        max_temp = max(temps)
        avg_humidity = sum(w.humidity for w in data) / len(data)
        lines.append(f"\n  {continent} ({len(data)} countries)")
        lines.append(f"    Avg Temperature : {avg_temp:.1f}°C")
        lines.append(f"    Min Temperature : {min_temp:.1f}°C")
        lines.append(f"    Max Temperature : {max_temp:.1f}°C")
        lines.append(f"    Avg Humidity    : {avg_humidity:.0f}%")

    return "\n".join(lines)


def generate_full_report(weather_list: list[WeatherData]) -> str:
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sections = [
        f"{'=' * 80}",
        "  WORLD WEATHER REPORT",
        f"  Generated: {timestamp}",
        f"  Countries: {len(weather_list)}",
        f"{'=' * 80}",
        "",
        "DETAILED TABLE",
        "-" * 40,
        format_summary_table(weather_list),
        "",
        "CONTINENT SUMMARY",
        "-" * 40,
        format_continent_summary(weather_list),
        "",
        f"{'=' * 80}",
        f"  Report complete. {len(weather_list)} countries processed.",
        f"{'=' * 80}",
    ]
    return "\n".join(sections)


def find_extremes(weather_list: list[WeatherData]) -> dict[str, WeatherData | None]:
    if not weather_list:
        return {
            "hottest": None,
            "coldest": None,
            "most_humid": None,
            "windiest": None,
        }
    return {
        "hottest": max(weather_list, key=lambda w: w.temperature_celsius),
        "coldest": min(weather_list, key=lambda w: w.temperature_celsius),
        "most_humid": max(weather_list, key=lambda w: w.humidity),
        "windiest": max(weather_list, key=lambda w: w.wind_speed_kmh),
    }


def format_extremes(weather_list: list[WeatherData]) -> str:
    extremes = find_extremes(weather_list)
    if not any(extremes.values()):
        return "No data available for extremes."

    lines = ["\n  WEATHER EXTREMES", "  " + "-" * 40]

    hottest = extremes["hottest"]
    if hottest:
        lines.append(
            f"  Hottest     : {hottest.country} ({hottest.capital}) "
            f"- {hottest.temperature_celsius:.1f}°C"
        )

    coldest = extremes["coldest"]
    if coldest:
        lines.append(
            f"  Coldest     : {coldest.country} ({coldest.capital}) "
            f"- {coldest.temperature_celsius:.1f}°C"
        )

    most_humid = extremes["most_humid"]
    if most_humid:
        lines.append(
            f"  Most Humid  : {most_humid.country} ({most_humid.capital}) "
            f"- {most_humid.humidity}%"
        )

    windiest = extremes["windiest"]
    if windiest:
        lines.append(
            f"  Windiest    : {windiest.country} ({windiest.capital}) "
            f"- {windiest.wind_speed_kmh:.1f} km/h"
        )

    return "\n".join(lines)
