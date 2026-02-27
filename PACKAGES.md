# 📦 Package Guide - What Each Package Does

## Python Packages (Backend)

Run: `pip install -r requirements.txt`

### Existing Packages
- **google-genai** - Calls the Gemini API for AI insights
- **python-dotenv** - Loads your `.env` file (API keys)
- **requests** - Makes HTTP requests to OpenWeatherMap API

### New Packages Added

#### **fastapi** ⚡
- **What it does:** Modern web framework for building REST APIs
- **Why we need it:** Converts your WeatherAssistant into a web service that the frontend can call
- **How it works:** Creates HTTP endpoints (like `/chat`) that accept requests and return JSON
- **Example:** When frontend sends `POST /chat`, FastAPI handles it and calls WeatherAssistant

#### **uvicorn[standard]** 🚀
- **What it does:** ASGI server that runs your FastAPI app
- **Why we need it:** Starts the web server so people can access your API
- **How it works:** Runs your API on `http://localhost:8000`
- **Command:** `python backend/api.py` automatically uses uvicorn

#### **pydantic** 📋
- **What it does:** Data validation and modeling
- **Why we need it:** Ensures request/response data is correctly formatted
- **How it works:** Defines models like `ChatRequest` and `ChatResponse` that validate data types
- **Example:** If someone sends invalid data, Pydantic rejects it automatically

#### **python-multipart** 📨
- **What it does:** Parses form data and multipart requests
- **Why we need it:** Allows file uploads and form submissions (if needed later)
- **Default:** FastAPI includes this for comprehensive request handling

---

## Frontend Packages (Node.js/npm)

Run: `npm install` in the `vite-frontend` folder

### Core Framework
#### **react** ⚛️
- **What it does:** JavaScript library for building UIs
- **Why we need it:** Creates interactive components for the chat interface
- **How it works:** Updates the page dynamically without page reloads
- **Example:** When you type a message, React updates the `messages` state and re-renders

#### **react-dom** 🎨
- **What it does:** Renders React components to the webpage
- **Why we need it:** Needed to display React components in the browser
- **How it works:** Mounts your React app to `<div id="root">` in index.html

### Build Tool
#### **vite** ⚡
- **What it does:** Super fast bundler and dev server
- **Why we need it:** Hot Module Replacement (HMR) - instantly reloads changes while developing
- **How it works:** Watches your files, immediately reflects changes in browser
- **Compare:** Much faster than older tools like webpack (instant reload vs 5+ seconds)

#### **@vitejs/plugin-react** ⚙️
- **What it does:** Plugin for Vite to support React
- **Why we need it:** Vite needs to understand JSX syntax (React's HTML-like code)
- **How it works:** Transforms JSX to regular JavaScript automatically

### API Communication
#### **axios** 🌐
- **What it does:** Simple HTTP client for making API requests
- **Why we need it:** Sends messages to the backend API
- **How it works:** Makes `POST /chat` requests and handles responses
- **Example:** `sendMessage("London")` uses axios to call the backend

---

## Full Stack Overview

```
┌─────────────────────────────────────────────────┐
│         Browser (React + Vite)                  │
│  ┌──────────────────────────────────────────┐   │
│  │  ChatInterface Component                 │   │
│  │  (uses axios to call backend)            │   │
│  └──────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │ axios HTTP request
                  ▼
┌─────────────────────────────────────────────────┐
│     Backend (FastAPI + Uvicorn)                 │
│  ┌──────────────────────────────────────────┐   │
│  │  /chat endpoint                          │   │
│  │  (receives message, calls WeatherAssistant)  │
│  └──────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │ Python code
                  ▼
┌─────────────────────────────────────────────────┐
│    Your Original Code (main.py)                 │
│  ┌──────────────────────────────────────────┐   │
│  │  WeatherAssistant                        │   │
│  │  ├─ WeatherAPIClient (requests)          │   │
│  │  ├─ WeatherParser (pydantic)             │   │
│  │  └─ LLMClient (google-genai)             │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## Why These Packages?

| Package | Replaces | Why Better |
|---------|----------|------------|
| FastAPI | Flask | Modern, automatic API docs, faster |
| Vite | Create React App | Instant reloads, tiny build size |
| axios | fetch API | Simpler syntax, better error handling |
| pydantic | manual validation | Auto validation, great error messages |

---

## Size Comparison

```
Python (backend):
  Total: ~500MB (includes all dependencies)
  - google-genai: ~50MB
  - fastapi: ~10MB
  - Other: ~400MB

Node (frontend):
  Total: ~400MB (node_modules/)
  - React: ~50MB
  - Vite: ~80MB
  - Other: ~270MB
```

(These are large because of dependencies, but compiled versions are much smaller)

---

## Advanced: Environment Variables

The `.env` file is created automatically with these variables:

**Backend (`scaffold/.env`):**
```env
WEATHER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```
Loaded by `python-dotenv` in your Python code.

**Frontend (`vite-frontend/.env`):**
```env
VITE_API_URL=http://localhost:8000
```
Loaded by Vite during build. Prefix `VITE_` is required.

---

## Version Info

This project uses:
- Python 3.8+
- Node.js 16+
- React 18.3.1
- FastAPI 0.95+
- Vite 5.2+

These are stable, well-maintained versions.

---

## Next: Understanding the Architecture

Once you understand the packages, read [README.md](./README.md) to learn how they work together!
