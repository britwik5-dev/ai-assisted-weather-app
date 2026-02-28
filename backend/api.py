"""
FastAPI REST API for Weather Assistant.
Converts the WeatherAssistant into a web service.
"""

import os
import sys
import logging
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to Python path so we can import main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import WeatherAssistant
from google import genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# Data Models (for request/response validation)
# ──────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str  # User's message (city name or question)


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    user_message: str  # Echo back what the user said
    bot_type: str  # "weather" or "chat"
    
    # Weather data (only populated if bot_type == "weather")
    city: Optional[str] = None
    country: Optional[str] = None
    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    description: Optional[str] = None
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None
    
    # Insights (both types)
    recommendation: Optional[str] = None
    insights: Optional[str] = None
    
    # Error handling
    error: Optional[str] = None


# ──────────────────────────────────────────────────────────────
# FastAPI App Setup
# ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Weather Assistant API",
    description="REST API for the Weather Assistant chatbot",
    version="1.0.0",
)

# Add CORS middleware so the React frontend can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize the WeatherAssistant once (reused for all requests)
try:
    assistant = WeatherAssistant()
    logger.info("WeatherAssistant initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize WeatherAssistant: {e}")
    assistant = None

# ──────────────────────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint - returns welcome message."""
    return {
        "message": "Welcome to the Weather Assistant API!",
        "docs_url": "/docs",
        "endpoints": {
            "chat": "POST /chat - Send a message to the weather assistant"
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for the weather assistant.
    
    Accepts a message (city name or question) and returns either:
    - Weather data with recommendations and insights
    - Conversational response
    """
    
    if not assistant:
        raise HTTPException(
            status_code=500,
            detail="Weather Assistant service is not available"
        )
    
    message = request.message.strip()
    
    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    
    logger.info(f"Received chat message: {message}")
    
    try:
        # ONE single Gemini call that classifies AND responds at the same time
        # This avoids rate limit issues from making multiple API calls
        single_prompt = (
            f"The user said: '{message}'\n\n"
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
        logger.info(f"Gemini classification response: {response_text[:50]}")

        if response_text.startswith("WEATHER:"):
            # Extract city name and fetch real weather data
            city_name = response_text.replace("WEATHER:", "").strip()
            logger.info(f"Fetching weather for city: {city_name}")
            result = assistant.get_weather_insights(city_name)

            if "error" in result:
                return ChatResponse(
                    user_message=message,
                    bot_type="weather",
                    error=result["error"]
                )

            return ChatResponse(
                user_message=message,
                bot_type="weather",
                city=result.get("city"),
                country=result.get("country"),
                temperature=result.get("temperature"),
                feels_like=result.get("feels_like"),
                description=result.get("description"),
                humidity=result.get("humidity"),
                wind_speed=result.get("wind_speed"),
                recommendation=result.get("recommendation"),
                insights=result.get("insights"),
            )

        elif response_text.startswith("CHAT:"):
            # Extract chat response and return it
            chat_reply = response_text.replace("CHAT:", "").strip()
            logger.info(f"Returning chat response")
            return ChatResponse(
                user_message=message,
                bot_type="chat",
                recommendation=chat_reply,
                insights=None,
            )

        else:
            # Gemini returned something unexpected — fallback
            logger.warning(f"Unexpected Gemini response: {response_text[:50]}")
            if len(message.split()) <= 3:
                # Short input — probably a city name, try fetching weather
                result = assistant.get_weather_insights(message)
                if "error" not in result:
                    return ChatResponse(
                        user_message=message,
                        bot_type="weather",
                        city=result.get("city"),
                        country=result.get("country"),
                        temperature=result.get("temperature"),
                        feels_like=result.get("feels_like"),
                        description=result.get("description"),
                        humidity=result.get("humidity"),
                        wind_speed=result.get("wind_speed"),
                        recommendation=result.get("recommendation"),
                        insights=result.get("insights"),
                    )
            return ChatResponse(
                user_message=message,
                bot_type="chat",
                recommendation=response_text,
                insights=None,
            )

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Weather Assistant API",
        "assistant_ready": assistant is not None
    }


# ──────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    
    # Run the server on localhost:8000
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
