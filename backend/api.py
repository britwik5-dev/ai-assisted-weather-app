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
        # First, check if this looks like a city name
        check_prompt = (
            f"The user typed: '{message}'\n"
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
            # ── Fetch weather data ──────────────────────────────────
            logger.info(f"Detected city name: {message}")
            result = assistant.get_weather_insights(message)
            
            # Check if there was an error
            if "error" in result:
                return ChatResponse(
                    user_message=message,
                    bot_type="weather",
                    error=result["error"]
                )
            
            # Return weather data
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
        
        else:
            # ── Conversational response ─────────────────────────────
            logger.info(f"Treating as general question: {message}")
            chat_prompt = (
                f"The user said: '{message}'\n"
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
            
            return ChatResponse(
                user_message=message,
                bot_type="chat",
                insights=chat_response.text.strip(),
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
