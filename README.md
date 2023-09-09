# GeoGPT

GeoGPT is an application that provides the latitude, longitude, and timezone for any address in the world for cities with more than 500 residents. 
It leverages OpenAI's GPT models to interpret and standardize addresses. 
Data from geonames.org is then utilized to furnish latitude, longitude, and timezone details.

## Setup & Installation

1. **Dependencies**

   Install the required dependencies using `poetry`:
   ```bash
   poetry install
   ```

2. **API Key**

   Create a `.env` file and set your OpenAI API key within it:
   ``` env
   OPENAI_API_KEY=your_key_here
   ```

3. **Create geonames.sqlite3 SQLite3 database**

   Fetch the `cities500.txt` file from Geoname at [this link](http://download.geonames.org/export/dump/), which provides details of all cities with a population greater than 500.
   
   1. Open the SQLite shell:
      ``` bash
      sqlite3 geonames.sqlite3
      ```
   2. Create the `geoname` SQL table:
      ``` sql
      CREATE TABLE geoname (
         geonameid INTEGER PRIMARY KEY,
         name TEXT,
         asciiname TEXT,
         alternatenames TEXT,
         latitude REAL,
         longitude REAL,
         feature_class TEXT,
         feature_code TEXT,
         country_code TEXT,
         cc2 TEXT,
         admin1_code TEXT,
         admin2_code TEXT,
         admin3_code TEXT,
         admin4_code TEXT,
         population INTEGER,
         elevation INTEGER,
         dem INTEGER,
         timezone TEXT,
         modification_date TEXT
      );
      ```
   3. Set the field separator:
      ``` SQL
      .separator "\t"
      ```
   4. Import the `cities500.txt` file into the `geoname` table:
      ``` SQL
      .import cities500.txt geoname
      ```

4. **Running the Application**

   Execute the FastAPI application using `uvicorn`:
   ```bash
   poetry run uvicorn geogpt.main:app --reload
   ```

## Usage

Submit an address to the endpoint, and the application will return details about the location, including its normalized name, country, longitude, latitude, and timezone.

## Contributing

Contributions are welcome! Please fork the repository and open a pull request with your changes. Alternatively, open an issue to discuss suggestions or report bugs.
