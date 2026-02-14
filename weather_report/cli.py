"""Command-line interface for the weather report generator."""

import argparse
import sys

from weather_report.countries import (
    get_all_continents,
    get_all_countries,
    get_countries_by_continent,
    get_country_by_name,
)
from weather_report.report import (
    format_extremes,
    format_single_report,
    generate_full_report,
)
from weather_report.weather_service import (
    WeatherServiceError,
    fetch_weather,
    fetch_weather_batch,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="weather-report",
        description="Generate weather reports for countries around the world.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("all", help="Get weather report for all countries")

    country_parser = subparsers.add_parser("country", help="Get weather for a specific country")
    country_parser.add_argument("name", type=str, help="Country name")

    continent_parser = subparsers.add_parser(
        "continent", help="Get weather for all countries in a continent"
    )
    continent_parser.add_argument("name", type=str, help="Continent name")

    subparsers.add_parser("list-countries", help="List all available countries")
    subparsers.add_parser("list-continents", help="List all continents")

    return parser


def cmd_all() -> int:
    print("Fetching weather data for all countries... This may take a few minutes.\n")
    countries = get_all_countries()
    weather_list = fetch_weather_batch(countries, on_error="skip")
    print(generate_full_report(weather_list))
    print(format_extremes(weather_list))
    return 0


def cmd_country(name: str) -> int:
    country = get_country_by_name(name)
    if not country:
        print(f"Error: Country '{name}' not found.", file=sys.stderr)
        print("Use 'weather-report list-countries' to see available countries.", file=sys.stderr)
        return 1

    try:
        weather = fetch_weather(country)
    except WeatherServiceError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"\n  Weather Report for {country.name}")
    print("  " + "-" * 40)
    print(format_single_report(weather))
    return 0


def cmd_continent(name: str) -> int:
    countries = get_countries_by_continent(name)
    if not countries:
        print(f"Error: Continent '{name}' not found.", file=sys.stderr)
        print("Use 'weather-report list-continents' to see available continents.", file=sys.stderr)
        return 1

    print(f"Fetching weather data for {name} ({len(countries)} countries)...\n")
    weather_list = fetch_weather_batch(countries, on_error="skip")
    print(generate_full_report(weather_list))
    print(format_extremes(weather_list))
    return 0


def cmd_list_countries() -> int:
    countries = get_all_countries()
    print(f"\nAvailable Countries ({len(countries)}):")
    print("-" * 60)
    for c in countries:
        print(f"  {c.name:<40} Capital: {c.capital}")
    return 0


def cmd_list_continents() -> int:
    continents = get_all_continents()
    print("\nAvailable Continents:")
    print("-" * 30)
    for continent in continents:
        countries = get_countries_by_continent(continent)
        print(f"  {continent:<20} ({len(countries)} countries)")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "all": lambda: cmd_all(),
        "country": lambda: cmd_country(args.name),
        "continent": lambda: cmd_continent(args.name),
        "list-countries": lambda: cmd_list_countries(),
        "list-continents": lambda: cmd_list_continents(),
    }

    handler = commands.get(args.command)
    if handler:
        return handler()

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
