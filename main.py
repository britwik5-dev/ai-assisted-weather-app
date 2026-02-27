import os
import json
import logging
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from utils.config import SYSTEM_PROMPT
from utils.parser import WeatherParser
from google import genai

load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class WeatherAPIClient:
    """Client for fetching weather data from OpenWeatherMap API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("WEATHER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No Weather API key provided. Set WEATHER_API_KEY in your .env file."
            )
        # TODO: Set base URL for weather API
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        logger.info("WeatherAPIClient initialized successfully.")
    
    def get_weather(self, city: str) -> Dict[str, Any]:
        """Fetch weather data for a given city."""
        # TODO: Make HTTP GET request to weather API
        params = {
            "q": city,              # city name to search for
            "appid": self.api_key,  # our secret API key for authentication
            "units": "metric",      # return temperature in Celsius (not Fahrenheit)
        }
        try:
            logger.info(f"Fetching weather data for '{city}'...")
            response = requests.get(self.base_url, params=params, timeout=10)

        # TODO: Handle HTTP errors (401, 404, 429, etc.)
            if response.status_code == 401:
                raise ValueError("Invalid Weather API key (401 Unauthorized). Check your WEATHER_API_KEY.")
            elif response.status_code == 404:
                raise ValueError(f"City '{city}' not found (404). Please check the city name.")
            elif response.status_code == 429:
                raise RuntimeError("Weather API rate limit exceeded (429). Please wait and try again.")
            elif response.status_code != 200:
                # Catch any other unexpected status codes
                raise RuntimeError(
                    f"Weather API returned unexpected status {response.status_code}: {response.text}"
                )
        
        # TODO: Handle network errors and timeouts
        except requests.exceptions.Timeout:
            # This runs if the server didn't respond within 10 seconds
            raise RuntimeError(f"Request timed out while fetching weather for '{city}'.")
        except requests.exceptions.ConnectionError:
            # This runs if there's no internet or the server is unreachable
            raise RuntimeError(f"Network connection error for '{city}'. Check your internet connection.")
        except requests.exceptions.RequestException as e:
            # Catch-all for any other requests-related errors
            raise RuntimeError(f"Unexpected network error: {str(e)}")
        # TODO: Return JSON response or raise appropriate exception
        # Parse JSON response separately to distinguish network vs parsing errors
        try:
            data = response.json()
            logger.info(f"Weather data fetched successfully for {city}.")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse weather API response: {e}")
            raise RuntimeError("Invalid JSON received from Weather API.")

        

class LLMClient:
    """Client for calling Gemini API to generate weather insights."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No Gemini API key provided. Set GEMINI_API_KEY in your .env file."
            )
        self.client = genai.Client(api_key=self.api_key)

        logger.info("LLMClient initialized successfully.")
       
    
    def generate_insights(self, weather_data: Dict[str, Any]) -> str:
        """Generate weather insights and recommendations using LLM."""
        # TODO: Format weather data for LLM prompt
        weather_summary = (
            f"City: {weather_data.get('city', 'Unknown')}, "
            f"Country: {weather_data.get('country', 'Unknown')}\n"
            f"Temperature: {weather_data.get('temperature', 'N/A')}°C "
            f"(Feels like: {weather_data.get('feels_like', 'N/A')}°C)\n"
            f"Condition: {weather_data.get('description', 'N/A')}\n"
            f"Humidity: {weather_data.get('humidity', 'N/A')}%\n"
            f"Wind Speed: {weather_data.get('wind_speed', 'N/A')} m/s\n"
        )
        user_prompt = (
            f"Here is the current weather data:\n{weather_summary}\n"
            "Please provide:\n"
            "1. A short, friendly recommendation (1 sentence) labelled 'Recommendation:'.\n"
            "2. A brief insight about the conditions (1-2 sentences) labelled 'Insights:'."
        )
        # TODO: Call Gemini API with system prompt and weather data
        try:
            logger.info("Sending weather data to Gemini for insights...")
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=1024,
                    temperature=0.7,
                ),
            )
            insights = response.text.strip()
        # TODO: Handle LLM API errors
            if not insights:
                raise RuntimeError("Gemini returned an empty response.")
        # TODO: Return generated insights
            logger.info("Insights generated successfully.")
            return insights

        except Exception as e:
            # Catch any error from the Gemini API and re-raise with a clear message
            logger.error(f"LLM API error: {str(e)}")
            raise RuntimeError(f"Failed to generate insights from Gemini: {str(e)}")


class WeatherAssistant:
    """Main assistant that coordinates weather data fetching and insights generation."""
    
    def __init__(self):
        self.weather_client = WeatherAPIClient()  # fetches raw weather from API
        self.llm_client = LLMClient()             # generates AI insights
        self.parser = WeatherParser()             # cleans and validates raw data
        logger.info("WeatherAssistant is ready.")
    
    def get_weather_insights(self, city: str) -> Dict[str, Any]:
        """Get weather data and generate insights for a given city."""
        # TODO: Fetch weather data from API
        try:
            raw_data = self.weather_client.get_weather(city)
        except (ValueError, RuntimeError) as e:
            logger.error(f"Weather fetch failed for '{city}': {e}")
            return {"city": city, "error": str(e)}
        # TODO: Parse and validate weather data
        try:
            parsed = self.parser.parse_weather_data(raw_data)
        except Exception as e:
            logger.error(f"Parsing failed for '{city}': {e}")
            return {"city": city, "error": f"Failed to parse weather data: {str(e)}"}
        # TODO: Generate insights using LLM
        try:
            insights_text = self.llm_client.generate_insights(parsed)
        except RuntimeError as e:
            logger.warning(f"LLM insights failed for '{city}': {e}")
            insights_text = "Insights unavailable at this time."
        
        # ── STEP 4: Split insights into two fields
        # Collapse all whitespace/newlines into clean single spaces first
        # Clean the full response text
        full_text = " ".join(insights_text.split())

        # Remove any "Recommendation:" or "Insights:" labels Gemini may have added
        full_text = full_text.replace("Recommendation:", "").replace("Insights:", "").strip()

        # Split into sentences properly
        import re
        sentences = re.split(r'(?<=[.!?])\s+', full_text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) >= 3:
            recommendation = " ".join(sentences[:2])
            insights       = " ".join(sentences[2:])
        elif len(sentences) == 2:
            recommendation = sentences[0]
            insights       = sentences[1]
        else:
            recommendation = full_text
            insights       = ""

        # TODO: Return structured response
        result = {
            "city": parsed.get("city"),
            "country": parsed.get("country"),
            "temperature": parsed.get("temperature"),
            "feels_like": parsed.get("feels_like"),
            "description": parsed.get("description"),
            "humidity": parsed.get("humidity"),
            "wind_speed": parsed.get("wind_speed"),
            "recommendation": recommendation,
            "insights": insights,
        }

        logger.info(f"Weather insights complete for '{city}'.")
        return result


def main():
    """Interactive chatbot loop for the weather assistant."""

    print("=" * 50)
    print("   Welcome to the Weather Assistant 🌤️")
    print("=" * 50)
    print("Type a city name to get the weather.")
    print("Type 'quit' or 'exit' to stop.\n")

    # Create the assistant once — reused for every city the user asks about
    assistant = WeatherAssistant()

    # Keep looping forever until the user types quit/exit
    # "while True" means "repeat this block endlessly"
    while True:

        # input() pauses the program and waits for the user to type something
        # .strip() removes accidental spaces e.g. "  London  " → "London"
        city = input("🌍 Enter city name: ").strip()

        # If the user typed nothing at all, ask again
        if not city:
            print("  Please enter a city name.\n")
            continue
            # "continue" skips the rest of this loop iteration and goes back to the top

        # If the user wants to quit, break out of the loop
        if city.lower() in ["quit", "exit", "q"]:
            # .lower() converts to lowercase so "Quit", "QUIT", "quit" all work
            print("\nGoodbye! Stay weather-aware! 👋")
            break
            # "break" exits the while loop completely

        print("-" * 50)

        try:
            # ── STEP 1: Ask Gemini if this looks like a city name ────────
            # Before hitting the weather API, we ask Gemini to classify
            # what the user typed. This way we handle casual conversation
            # gracefully instead of getting a confusing 404 error.
            check_prompt = (
                f"The user typed: '{city}'\n"
                "Is the user's ENTIRE input ONLY a city or place name "
                "with the intention of getting a weather report?\n"
                "Examples that are YES: 'London', 'New York', 'Tokyo', 'Paris'\n"
                "Examples that are NO: 'Suggest me a restaurant in Kolkata', "
                "'How are you?', 'What should I wear?', 'Tell me about Paris'\n"
                "Reply with ONLY one word: YES or NO."
            )
            check_response = assistant.llm_client.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=check_prompt,
            )
            is_city = check_response.text.strip().upper().startswith("YES")

            if is_city:
                # ── It looks like a city — fetch weather as normal ───────
                print(f"\nFetching weather for '{city}'...")

                result = assistant.get_weather_insights(city)

                if "error" in result:
                    print(f"  ❌ Error: {result['error']}")
                else:
                    print(f"  📍 City        : {result.get('city', 'N/A')}, {result.get('country', 'N/A')}")
                    print(f"  🌡️  Temperature : {result.get('temperature', 'N/A')}°C")
                    print(f"  🌤️  Description : {result.get('description', 'N/A')}")
                    print(f"  💧 Humidity    : {result.get('humidity', 'N/A')}%")
                    print(f"  💨 Wind Speed  : {result.get('wind_speed', 'N/A')} m/s")
                    print(f"\n  💡 Recommendation:")
                    print(f"     {result.get('recommendation', 'N/A')}")
                    print(f"\n  🔍 Insights:")
                    print(f"     {result.get('insights', 'N/A')}")

            else:
                # ── Not a city — let Gemini reply conversationally ───────
                # We still give a helpful answer but remind the user what
                # this assistant is actually designed for.
                chat_prompt = (
                    f"The user said: '{city}'\n"
                    "You are a friendly assistant who specialises in weather but "
                    "can also help with general questions. "
                    "Answer their question helpfully and fully using your knowledge. "
                    "If their question is DIRECTLY about weather or climate "
                    "(e.g. 'What is humidity?', 'What causes rain?') — answer "
                    "normally with no reminder at the end. "
                    "For ALL OTHER questions — including questions about cities, "
                    "restaurants, people, places, or anything else not directly "
                    "about weather — answer the question fully AND then add a "
                    "short friendly reminder at the end that you are primarily a "
                    "weather assistant and the user can type any city name to get "
                    "a live weather report with personalised recommendations. "
                    "Keep the reminder one sentence, natural and not robotic."
                )
                chat_response = assistant.llm_client.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=chat_prompt,
                )
                print(f"\n  🤖 {chat_response.text.strip()}")

        except Exception as e:
            print(f"  ❌ Unexpected error: {str(e)}")

        print("-" * 50)
        print()


if __name__ == "__main__":
    main()
