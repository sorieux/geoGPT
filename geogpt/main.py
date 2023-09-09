import json
import logging
import sqlite3

import openai
from decouple import config
from fastapi import FastAPI, HTTPException, Body

app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

openai.api_key = config("OPENAI_API_KEY")

# http://download.geonames.org/export/dump/readme.txt
# https://github.com/commodo/geonames-dump-to-sqlite/blob/master/README.md
def get_geoname(city: str, country_code: str):
    logging.info(f"Fetching geoname for city: {city} and country code: {country_code}")

    with sqlite3.connect("geonames.sqlite3") as con:
        cur = con.cursor()

        res = cur.execute(
            "SELECT name, country, longitude, latitude, timezone FROM geoname WHERE LOWER(asciiname)=? AND LOWER(country)=?",
            (city.lower(), country_code.lower()),
        )

        data = res.fetchone()

    if not data:
        logging.warning(f"No data found in the database for city: {city} and country code: {country_code}")
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
            "content": "Return the normalized English name of city and the country code for a given address",
        },
        {"role": "user", "content": address},
    ]

    custom_functions = [
        {
            "name": "extract_city_and_country_code",
            "description": "Get the normalized English name of the city and the country code for a given address as a JSON document with two fields: city and country_code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city associated with the provided address",
                    },
                    "country_code": {
                        "type": "string",
                        "description": "The country code associated with the provided address",
                    },
                },
            },
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        functions=custom_functions,
        function_call="auto",
    )

    logging.debug(f"OpenAI API response: {response}")

    try:
        response_data = json.loads(
            response["choices"][0]["message"]["function_call"]["arguments"]
        )

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
