# Weather Assistant Web App

A modern web application for the Weather Assistant with a Vite + React frontend and FastAPI backend.

## 📁 Project Structure

```
scaffold/
├── main.py                        # Original WeatherAssistant class
├── prompt.txt                     # System prompt for LLM
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (WEATHER_API_KEY, GEMINI_API_KEY)
├── utils/
│   ├── config.py                 # Load system prompt
│   └── parser.py                 # Parse weather data
├── backend/
│   └── api.py                    # FastAPI server
└── vite-frontend/                # React frontend
    ├── package.json              # Frontend dependencies
    ├── vite.config.js            # Vite configuration
    ├── index.html                # Main HTML file
    ├── .env                      # Frontend environment (API_URL)
    └── src/
        ├── main.jsx              # React entry point
        ├── App.jsx               # Main app component
        ├── App.css               # App styles
        ├── index.css             # Global styles
        ├── api.js                # API client
        └── components/
            ├── ChatInterface.jsx  # Chat UI component
            ├── WeatherCard.jsx    # Weather display
            └── MessageBubble.jsx  # Chat message bubble
        └── styles/
            ├── ChatInterface.css  # Chat styles
            ├── WeatherCard.css    # Weather card styles
            └── MessageBubble.css  # Message bubble styles
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- Node.js 16+ and npm installed
- Your `.env` file with `WEATHER_API_KEY` and `GEMINI_API_KEY`

### Step 1: Install Backend Dependencies

Open PowerShell in the `scaffold` folder and run:

```powershell
pip install -r requirements.txt
```

This installs:
- `fastapi` - API framework
- `uvicorn[standard]` - ASGI server for running FastAPI
- `google-genai` - Gemini API client
- `python-dotenv` - Load environment variables
- `requests` - HTTP client for weather API

### Step 2: Install Frontend Dependencies

Navigate to the frontend folder:

```powershell
cd vite-frontend
npm install
```

This installs:
- `react` & `react-dom` - React framework
- `axios` - HTTP client for calling the backend
- `vite` - Frontend build tool
- `@vitejs/plugin-react` - React support for Vite

### Step 3: Create Frontend Environment File

The frontend needs to know where the backend API is running.

**In `vite-frontend/.env`** (already created):
```
VITE_API_URL=http://localhost:8000
```

This tells the frontend to call your backend at `http://localhost:8000`.

---

## 🎯 How to Run Both Servers

You need **TWO PowerShell windows** open (one for backend, one for frontend).

### Option A: Run Both Servers Manually (Recommended for Learning)

**Window 1 - Start the FastAPI Backend:**

Navigate to the `scaffold` folder, then:

```powershell
cd vite-frontend  # Make sure you're in the right directory
cd ..             # Go back to scaffold root
python backend/api.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ Backend is ready! Leave this window open.

---

**Window 2 - Start the React Frontend:**

Navigate to the `scaffold/vite-frontend` folder, then:

```powershell
npm run dev
```

You should see:
```
  VITE v5.0.0  ready in 123 ms

  ➜  Local:   http://127.0.0.1:5173/
  ➜  Press h to show help
```

✅ Frontend is ready! Open **http://127.0.0.1:5173/** in your browser.

---

### Option B: Run Both in One Command (Advanced)

If you want to run both servers in one terminal window, install `concurrently`:

```powershell
npm install -g concurrently
```

Then from the `scaffold` folder, create a script to start both:

```powershell
# This is a PowerShell one-liner to start both
Start-Job -ScriptBlock { cd backend; python api.py } ; npm --prefix vite-frontend run dev
```

---

## 🌐 How It Works

### Architecture Flow

```
User Browser
    ↓
[React Frontend] (http://localhost:5173)
    ↓ (axios HTTP request)
[FastAPI Backend] (http://localhost:8000)
    ↓
[WeatherAssistant class]
    ├─→ WeatherAPIClient (fetches OpenWeatherMap)
    ├─→ WeatherParser (parses raw data)
    └─→ LLMClient (calls Gemini API)
    ↓
[JSON Response]
    ↓
[React displays Weather Card & Chat]
```

### API Endpoints

**Backend API endpoints:**

#### `POST /chat`
Send a message to the weather assistant.

**Request:**
```json
{
  "message": "What's the weather in London?"
}
```

**Response (Weather):**
```json
{
  "user_message": "What's the weather in London?",
  "bot_type": "weather",
  "city": "London",
  "country": "GB",
  "temperature": 12.5,
  "feels_like": 11.2,
  "description": "partly cloudy",
  "humidity": 65,
  "wind_speed": 5.2,
  "recommendation": "Carry a light jacket...",
  "insights": "It's a pleasant day..."
}
```

**Response (Chat):**
```json
{
  "user_message": "How are you?",
  "bot_type": "chat",
  "insights": "I'm doing great! I'm a weather assistant. You can ask me about weather in any city...",
  "error": null
}
```

#### `GET /health`
Check if the backend is running.

**Response:**
```json
{
  "status": "ok",
  "service": "Weather Assistant API",
  "assistant_ready": true
}
```

#### `GET /`
Welcome endpoint with documentation link.

---

## 🎨 Frontend Features

### Chat Interface
- Modern WhatsApp-style chat UI
- Messages appear on the right for user, left for bot
- Auto-scrolls to latest message
- Loading spinner while waiting for response

### Weather Card
- Displays city, country, temperature
- Shows "feels like", humidity, wind speed with icons
- Blue gradient background
- Personalized recommendations
- Weather insights

### Dark Theme
- Gradient dark blue background
- Cyan/turquoise accents
- Easy on the eyes
- Smooth animations

### Responsive Design
- Works on desktop, tablet, mobile
- Messages wrap properly
- Touch-friendly buttons
- Adaptive layout

---

## 🔧 Troubleshooting

### Problem: "Backend is not running"

**Solution:** Make sure you started the backend server in Window 1.

```powershell
# In Window 1, from scaffold folder:
python backend/api.py
```

---

### Problem: "Cannot fetch from API" or CORS error

**Solution:** The backend's CORS middleware might need adjustment.

**Edit `backend/api.py` line 54:**

```python
# Current (allows all origins):
allow_origins=["*"],

# For production, restrict to:
allow_origins=["http://localhost:5173"],
```

---

### Problem: "Module not found: google-genai"

**Solution:** Install Python dependencies again:

```powershell
pip install -r requirements.txt
```

---

### Problem: "npm: command not found"

**Solution:** Node.js is not installed. Download and install from https://nodejs.org/

---

### Problem: Frontend won't load in browser

**Solution:** Check if Vite started successfully:

```powershell
cd vite-frontend
npm run dev
```

Make sure you see `Local: http://127.0.0.1:5173/`

---

## 📦 Environment Variables

You need a `.env` file in the **root folder** with:

```env
WEATHER_API_KEY=your_openweathermap_key
GEMINI_API_KEY=your_gemini_api_key
```

The backend reads from this automatically using `python-dotenv`.

The frontend reads `VITE_API_URL` from `vite-frontend/.env`.

---

## 🔄 Workflow Example

1. **Open browser:** http://127.0.0.1:5173/
2. **Type in chat:** "London"
3. **Frontend sends HTTP POST** to `http://localhost:8000/chat`
4. **Backend:**
   - Asks Gemini if "London" is a city name → YES
   - Calls OpenWeatherMap API
   - Calls Gemini for recommendations
   - Returns JSON with weather data
5. **Frontend displays:**
   - User message bubble on right
   - Beautiful weather card with all details
   - Recommendation and insights

---

## 📝 What Each File Does

| File | Purpose |
|------|---------|
| `backend/api.py` | FastAPI server that wraps WeatherAssistant |
| `vite-frontend/src/App.jsx` | Main React app component |
| `vite-frontend/src/components/ChatInterface.jsx` | Chat UI logic and state |
| `vite-frontend/src/components/WeatherCard.jsx` | Weather display component |
| `vite-frontend/src/components/MessageBubble.jsx` | Chat message component |
| `vite-frontend/src/api.js` | axios client for backend requests |
| `vite-frontend/src/styles/*.css` | Component styling |
| `main.py` | Original Python WeatherAssistant class |

---

## 🎓 Learning Notes

### Backend (`backend/api.py`)
- Uses **FastAPI** - a modern Python web framework
- **CORS middleware** allows frontend from any origin to call it
- **Pydantic models** validate request/response data
- Wraps your existing `WeatherAssistant` class without modifying it

### Frontend (`vite-frontend/`)
- **React** - component-based UI library
- **Vite** - super fast build tool (instant dev reload)
- **Axios** - easy HTTP client
- **CSS Grid/Flexbox** - responsive layout
- **CSS animations** - smooth transitions

---

## 🚀 Production Deployment

When you're ready to go live:

1. **Build frontend:** `npm run build` in `vite-frontend/`
2. **Serve compiled files** from the backend (add static file serving)
3. **Use environment variables** for API URL (not hardcoded)
4. **Get SSL certificate** (HTTPS)
5. **Deploy to Heroku/AWS/DigitalOcean** etc.

---

## ❓ Questions?

If anything isn't clear:
1. Check the folder structure matches the diagram above
2. Make sure both servers are running (check both PowerShell windows)
3. Check browser console (F12 → Console tab) for errors
4. Check PowerShell window for error messages

Good luck! 🌤️
