import os
import time
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
            "Write exactly 5 sentences about this weather following these rules:\n"
            "1. Each sentence MUST be complete and end with a period.\n"
            "2. Each sentence must be maximum 25 words.\n"
            "3. Sentence 1: What to wear or carry today.\n"
            "4. Sentence 2: Overall feel of the weather and comfort level.\n"
            "5. Sentence 3: Best activities suited for this weather.\n"
            "6. Sentence 4: Any health or safety tips for these conditions.\n"
            "7. Sentence 5: What to expect as the day progresses.\n"
            "Do not use labels, bullet points, numbers, or markdown like ** or *.\n"
            "Write in a warm, friendly tone as if talking to a friend."
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
            recommendation = sentences[0]        # first sentence only
            insights       = " ".join(sentences[1:])  # ALL remaining sentences
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
        city = input("🌍 Enter city name: ").strip()

        if not city:
            print("  Please enter a city name.\n")
            continue

        if city.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye! Stay weather-aware! 👋")
            break

        print("-" * 50)

        try:
            # ONE Gemini call that classifies AND responds in one shot
            single_prompt = (
                f"The user said: '{city}'\n\n"
                "If this is asking about weather for a city, respond with:\n"
                "WEATHER: <city name>\n\n"
                "If this is anything else, respond with:\n"
                "CHAT: <your helpful response>\n\n"
                "Important rules for CHAT responses:\n"
                "- Never use ** or * for bold text\n"
                "- Never use bullet points like * or -\n"
                "- Write in plain, friendly sentences only\n\n"
                "Examples:\n"
                "User: Kolkata                               WEATHER: Kolkata\n"
                "User: what is the weather like in Kolkata?  WEATHER: Kolkata\n"
                "User: how is weather in Delhi?              WEATHER: Delhi\n"
                "User: is it raining in Mumbai?              WEATHER: Mumbai\n"
                "User: New York                              WEATHER: New York\n"
                "User: how are you?                          CHAT: I'm doing great! I'm your weather assistant — type any city name for a live forecast!\n"
                "User: suggest restaurants in Kolkata        CHAT: Here are some great restaurants in Kolkata...\n"
                "User: who is Elon Musk?                     CHAT: Elon Musk is a billionaire entrepreneur...\n"
            )
            single_response = assistant.llm_client.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=single_prompt,
                config=genai.types.GenerateContentConfig(
                    max_output_tokens=300,
                    temperature=0.0,
                ),
            )
            response_text = (single_response.text or "").strip()

            if response_text.startswith("WEATHER:"):
                # It's a weather request — extract city name
                city = response_text.replace("WEATHER:", "").strip()
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

            elif response_text.startswith("CHAT:"):
                # It's a general question — show Gemini's response
                chat_reply = response_text.replace("CHAT:", "").strip()
                print(f"\n  🤖 {chat_reply}")

            else:
                # Gemini returned something unexpected — fallback
                if len(city.split()) <= 3:
                    # Short input — probably a city name, try fetching weather
                    result = assistant.get_weather_insights(city)
                    if "error" not in result:
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
                        print(f"  ❌ Error: {result['error']}")
                else:
                    print(f"\n  🤖 {response_text}")

        except Exception as e:
            print(f"  ❌ Unexpected error: {str(e)}")

        print("-" * 50)
        print()


if __name__ == "__main__":
    main()
