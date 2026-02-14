"""FastAPI REST API for countries, cities, and regions data."""

from fastapi import FastAPI, HTTPException, Query

from weather_report.cities import (
    get_all_cities,
    get_all_regions,
    get_capital_cities,
    get_cities_by_country,
    get_city_by_name,
    get_regions_by_continent,
    get_regions_by_country,
)
from weather_report.countries import (
    get_all_continents,
    get_all_countries,
    get_countries_by_continent,
    get_country_by_name,
)

app = FastAPI(
    title="World Geography API",
    description="API to get countries, cities, and regions across the world.",
    version="1.0.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "World Geography API",
        "docs": "/docs",
        "endpoints": "/countries, /cities, /regions",
    }


@app.get("/countries")
def list_countries(
    continent: str | None = Query(None, description="Filter by continent name"),
) -> dict[str, object]:
    if continent:
        countries = get_countries_by_continent(continent)
        if not countries:
            raise HTTPException(status_code=404, detail=f"Continent '{continent}' not found")
    else:
        countries = get_all_countries()
    return {
        "count": len(countries),
        "countries": [
            {
                "name": c.name,
                "capital": c.capital,
                "continent": c.continent,
                "latitude": c.latitude,
                "longitude": c.longitude,
            }
            for c in countries
        ],
    }


@app.get("/countries/{country_name}")
def get_country(country_name: str) -> dict[str, object]:
    country = get_country_by_name(country_name)
    if not country:
        raise HTTPException(status_code=404, detail=f"Country '{country_name}' not found")
    cities = get_cities_by_country(country_name)
    regions = get_regions_by_country(country_name)
    return {
        "name": country.name,
        "capital": country.capital,
        "continent": country.continent,
        "latitude": country.latitude,
        "longitude": country.longitude,
        "cities": [
            {"name": c.name, "region": c.region, "is_capital": c.is_capital} for c in cities
        ],
        "regions": [{"name": r.name} for r in regions],
    }


@app.get("/cities")
def list_cities(
    country: str | None = Query(None, description="Filter by country name"),
    capitals_only: bool = Query(False, description="Only return capital cities"),
) -> dict[str, object]:
    if country:
        cities = get_cities_by_country(country)
        if not cities:
            raise HTTPException(
                status_code=404, detail=f"No cities found for country '{country}'"
            )
    elif capitals_only:
        cities = get_capital_cities()
    else:
        cities = get_all_cities()
    return {
        "count": len(cities),
        "cities": [
            {
                "name": c.name,
                "country": c.country,
                "region": c.region,
                "latitude": c.latitude,
                "longitude": c.longitude,
                "is_capital": c.is_capital,
            }
            for c in cities
        ],
    }


@app.get("/cities/{city_name}")
def get_city(city_name: str) -> dict[str, object]:
    city = get_city_by_name(city_name)
    if not city:
        raise HTTPException(status_code=404, detail=f"City '{city_name}' not found")
    return {
        "name": city.name,
        "country": city.country,
        "region": city.region,
        "latitude": city.latitude,
        "longitude": city.longitude,
        "is_capital": city.is_capital,
    }


@app.get("/regions")
def list_regions(
    country: str | None = Query(None, description="Filter by country name"),
    continent: str | None = Query(None, description="Filter by continent name"),
) -> dict[str, object]:
    if country:
        regions = get_regions_by_country(country)
        if not regions:
            raise HTTPException(
                status_code=404, detail=f"No regions found for country '{country}'"
            )
    elif continent:
        regions = get_regions_by_continent(continent)
        if not regions:
            raise HTTPException(
                status_code=404, detail=f"No regions found for continent '{continent}'"
            )
    else:
        regions = get_all_regions()
    return {
        "count": len(regions),
        "regions": [
            {
                "name": r.name,
                "country": r.country,
                "continent": r.continent,
            }
            for r in regions
        ],
    }


@app.get("/continents")
def list_continents() -> dict[str, object]:
    continents = get_all_continents()
    result = []
    for continent in continents:
        countries = get_countries_by_continent(continent)
        regions = get_regions_by_continent(continent)
        result.append({
            "name": continent,
            "country_count": len(countries),
            "region_count": len(regions),
        })
    return {"count": len(result), "continents": result}
