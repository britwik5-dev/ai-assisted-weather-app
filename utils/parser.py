"""
Weather data parser module.
Handles parsing and validation of weather API responses.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WeatherParser:
    """Parser for weather API responses."""
    
    def parse_weather_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw weather API response into structured format."""
        if not raw_data:
            raise ValueError("Cannot parse empty or None weather data.")

        logger.info("Starting to parse raw weather data...")

        # TODO: Extract city name from raw_data.get('name')
        city = raw_data.get("name")
        # TODO: Extract country from raw_data.get('sys', {}).get('country')
        country = raw_data.get("sys", {}).get("country")
        # TODO: Extract temperature from raw_data.get('main', {}).get('temp')
        main_data = raw_data.get("main", {})
        temperature = main_data.get("temp")
        # TODO: Extract feels_like from raw_data.get('main', {}).get('feels_like')
        feels_like  = main_data.get("feels_like")
        # TODO: Extract humidity from raw_data.get('main', {}).get('humidity')
        humidity    = main_data.get("humidity")
        temp_min    = main_data.get("temp_min")
        temp_max    = main_data.get("temp_max")
        pressure    = main_data.get("pressure")
        # TODO: Extract description from raw_data.get('weather', [])[0].get('description')
        weather_list = raw_data.get("weather", [])
        first_weather  = weather_list[0] if weather_list else {}
        description    = first_weather.get("description")
        weather_main   = first_weather.get("main")
        # TODO: Extract wind_speed from raw_data.get('wind', {}).get('speed')
        wind_data  = raw_data.get("wind", {})
        wind_speed = wind_data.get("speed")
        wind_deg   = wind_data.get("deg")   # wind direction in degrees (optional)
        # TODO: Return dictionary with all extracted data
        parsed = {
            "city":        city,
            "country":     country,
            "temperature": temperature,
            "feels_like":  feels_like,
            "temp_min":    temp_min,
            "temp_max":    temp_max,
            "pressure":    pressure,
            "humidity":    humidity,
            "description": description,
            "weather_main": weather_main,
            "wind_speed":  wind_speed,
            "wind_deg":    wind_deg,
        }

        logger.info(f"Parsed weather data for city: '{city}'")
        return parsed
    
    def validate_weather_data(self, weather_data: Dict[str, Any]) -> bool:
        """Validate that weather data has required fields."""
        # TODO: Check if required fields exist and are not None

        # TODO: Required fields: 'city', 'temperature', 'description', 'humidity', 'wind_speed'
        required_fields = ["city", "temperature", "description", "humidity", "wind_speed"]

        missing = []  # we'll collect any missing field names here
        # TODO: Return True if all fields are present, False otherwise
        for field in required_fields:
            if weather_data.get(field) is None:
                missing.append(field)
                logger.warning(f"Validation failed: missing required field '{field}'")
            
        if missing:
            # Log all missing fields in one message for easy debugging
            logger.error(f"Weather data is missing required fields: {missing}")
            return False

        logger.info("Weather data validation passed — all required fields present.")
        return True
    
    def format_weather_for_llm(self, weather_data: Dict[str, Any]) -> str:
        """Format weather data for LLM prompt."""
        # TODO: Create formatted string with weather information
        # TODO: Include city, country, temperature, feels_like, description, humidity, wind_speed
        # TODO: Add appropriate units (°C, %, m/s)
        # TODO: Return formatted string
        
        city        = weather_data.get("city", "Unknown City")
        country     = weather_data.get("country", "Unknown Country")
        temperature = weather_data.get("temperature", "N/A")
        feels_like  = weather_data.get("feels_like", "N/A")
        description = weather_data.get("description", "N/A")
        humidity    = weather_data.get("humidity", "N/A")
        wind_speed  = weather_data.get("wind_speed", "N/A")
        temp_min    = weather_data.get("temp_min", "N/A")
        temp_max    = weather_data.get("temp_max", "N/A")

        formatted = (
            f"Current Weather Report\n"
            f"======================\n"
            f"Location    : {city}, {country}\n"
            f"Condition   : {description}\n"
            f"Temperature : {temperature}°C (feels like {feels_like}°C)\n"
            f"Range       : {temp_min}°C – {temp_max}°C\n"
            f"Humidity    : {humidity}%\n"
            f"Wind Speed  : {wind_speed} m/s\n"
        )

        logger.info(f"Formatted weather data for LLM prompt (city: {city}).")
        return formatted
