import json
import logging
import sqlite3

import openai
from decouple import config
from fastapi import FastAPI, HTTPException, Body

app = FastAPI()
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

openai.api_key = config("OPENAI_API_KEY")


def get_geoname(city: str, country_code: str):
    logging.info(f"Fetching geoname for city: {city} and country code: {country_code}")

    with sqlite3.connect("geonames.sqlite3") as con:
        cur = con.cursor()

        res = cur.execute(
            "SELECT name, country_code, longitude, latitude, timezone FROM geoname WHERE LOWER(asciiname)=? AND LOWER(country_code)=?",
            (city.lower(), country_code.lower()),
        )

        data = res.fetchone()

    if not data:
        logging.warning(
            f"No data found in the database for city: {city} and country code: {country_code}"
        )
        raise HTTPException(status_code=404, detail="Data not found in the database")

    name, country, longitude, latitude, timezone = data

    return {
        "name": name,
        "country": country,
        "longitude": longitude,
        "latitude": latitude,
        "timezone": timezone,
    }


def get_city_country(address: str):
    messages = [
        {
            "role": "system",
            "content": "Determine the city and country code from a possibly misspelled address. Return in JSON format: city and country_code",
        },
        {"role": "user", "content": address},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
    )

    logging.debug(f"OpenAI API response: {response}")

    try:
        response_data = json.loads(response["choices"][0]["message"]["content"])

        city = response_data["city"]
        country_code = response_data["country_code"]
    except (KeyError, json.JSONDecodeError):
        logging.error(f"Failed to parse OpenAI response")
        raise HTTPException(status_code=500, detail="Failed to parse OpenAI response")

    return city, country_code


@app.get("/{address}")
def main(address: str):
    city, country_code = get_city_country(address)
    res = get_geoname(city, country_code)
    return res
