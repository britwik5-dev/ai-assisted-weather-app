# 🚀 Quick Start Guide for Beginners

## What You Need

Before starting, make sure you have:

1. **Python 3.8+** - Download from https://www.python.org/downloads/
2. **Node.js 16+** - Download from https://nodejs.org/
3. **Your .env file** with API keys (should already exist in the root folder)

---

## 5 Steps to Get Running

### Step 1: Install Python Dependencies (2 minutes)

Open **PowerShell** in the `scaffold` folder and type:

```powershell
pip install -r requirements.txt
```

Wait for it to finish. You'll see a lot of text - that's normal.

---

### Step 2: Install Frontend Dependencies (3 minutes)

Still in PowerShell, type:

```powershell
cd vite-frontend
npm install
```

Wait for it to finish. You should see `added XXX packages`.

---

### Step 3: Start the Backend Server

**Open a NEW PowerShell window** in the `scaffold` folder and type:

```powershell
python backend/api.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

✅ **Leave this window open!** Don't close it.

---

### Step 4: Start the Frontend Server

**In your FIRST PowerShell window** (where you installed npm), type:

```powershell
npm run dev
```

You should see:
```
  ➜  Local:   http://127.0.0.1:5173/
```

✅ **Leave this window open too!**

---

### Step 5: Open in Browser

Open your web browser and go to:

```
http://127.0.0.1:5173/
```

You should see a beautiful dark-themed chat interface!

---

## 🤔 What if Something Goes Wrong?

### "Backend is not running"
→ Check your second PowerShell window. Did you run `python backend/api.py`?

### "Module not found: google-genai"
→ Run Step 1 again: `pip install -r requirements.txt`

### "command not found: npm"
→ Node.js isn't installed. Download from https://nodejs.org/

### "Address already in use"
→ Another app is using port 8000 or 5173. Close other Python/Node apps.

---

## 💬 How to Use

1. Type a **city name**: "London", "New York", "Tokyo"
2. Press **Enter** or click the send button
3. Wait for the weather card to appear
4. You can also ask questions: "How are you?", "What's humidity?"

---

## 📚 Next Steps

Once it's working, read the [**README.md**](./README.md) to understand:
- How the architecture works
- What each file does
- How to troubleshoot
- How to deploy to the internet

---

## ✅ You're Done!

You now have a working weather assistant with:
- ✨ Modern dark theme
- 💬 Chat interface
- 🌤️ Weather cards with icons
- 📱 Responsive design
- ⚡ Super fast frontend (Vite)
- 🐍 Fast backend (FastAPI)

Have fun! 🚀
