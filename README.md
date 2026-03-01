# Jothidam Backend — Deployment Guide

## Overview
Python Flask backend that generates professional Vedic horoscope PDFs and Excel files.

- **PDF**: 4 pages, drawn South Indian Rasi chart + Navamsa chart, planet table, Dasa-Bhukti, Yogas, Lucky info
- **Excel**: 4 sheets — Summary, Planet Positions, Dasa Bhukti, Yogas
- **Languages**: All 8 (EN, TA, HI, TE, KN, ML, MR, BN)

---

## Step 1: Deploy to Render.com (FREE)

### A) Push code to GitHub
```bash
# Create a new GitHub repo called "jothidam-backend"
git init
git add .
git commit -m "Initial backend"
git remote add origin https://github.com/YOUR_USERNAME/jothidam-backend.git
git push -u origin main
```

### B) Create Render Web Service
1. Go to https://render.com → Sign up (free)
2. New → Web Service → Connect GitHub → Select `jothidam-backend`
3. Settings:
   - **Name**: `jothidam-api`
   - **Region**: Singapore (closest to India)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

4. Environment Variables (click "Add Environment Variable"):
   ```
   RAZORPAY_KEY_ID     = rzp_live_XXXXXXXXXXXXXXXX
   RAZORPAY_KEY_SECRET = your_secret_key_here
   FLASK_ENV           = production
   ```

5. Click **Create Web Service**
6. Wait ~3 minutes for first deploy

### C) Your API URL will be:
```
https://jothidam-api.onrender.com
```

---

## Step 2: Update Frontend (horoscopegen.in)

### A) Add backend-client.js to your website
Copy `backend-client.js` to your website's `/js/` folder.

### B) Update index.html
Add before `</body>`:
```html
<!-- Backend API Client -->
<script src="/js/backend-client.js"></script>
```

### C) Update the backend URL in backend-client.js
```javascript
const BACKEND_URL = 'https://jothidam-api.onrender.com'; // ← your Render URL
```

### D) Update your PDF/Excel download buttons to call backend
In your HTML, find the download buttons and update onclick:
```html
<!-- OLD -->
<button onclick="downloadPDF()">Download PDF</button>

<!-- NEW — same function name, now calls backend -->
<button onclick="downloadPDF()">Download PDF</button>
```
No change needed if buttons already call `downloadPDF()` and `downloadExcel()` —
the new backend-client.js overrides these functions.

---

## Step 3: Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python app.py

# Test in another terminal
curl -X POST http://localhost:5000/api/horoscope \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","dob":"1990-07-28","tob":"10:30","pob":"Chennai","lang":"ta","chartStyle":"south"}'

# Download test PDF
curl -X POST http://localhost:5000/api/download/pdf \
  -H "Content-Type: application/json" \
  -d '{"name":"Somaskandan","dob":"1990-07-28","tob":"10:30","pob":"Chennai","lang":"ta"}' \
  -o test.pdf

# Check PDF opened
open test.pdf   # macOS
xdg-open test.pdf  # Linux
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/ping` | Health check |
| POST | `/api/horoscope` | Get horoscope data as JSON |
| POST | `/api/download/pdf` | Download PDF |
| POST | `/api/download/excel` | Download Excel |
| POST | `/api/create-order` | Create Razorpay order |
| POST | `/api/verify-payment` | Verify Razorpay payment |

### Request Body (all endpoints)
```json
{
  "name":       "Somaskandan R",
  "dob":        "1990-07-28",
  "tob":        "10:30",
  "pob":        "Chennai",
  "lang":       "ta",
  "chartStyle": "south"
}
```

### Language Codes
| Code | Language |
|------|----------|
| `en` | English |
| `ta` | Tamil |
| `hi` | Hindi |
| `te` | Telugu |
| `kn` | Kannada |
| `ml` | Malayalam |
| `mr` | Marathi |
| `bn` | Bengali |

---

## File Structure
```
jothidam-backend/
├── app.py              ← Flask API server (main entry point)
├── astro_engine.py     ← Vedic astronomy calculations
├── pdf_generator.py    ← Professional PDF with drawn charts
├── excel_generator.py  ← Formatted Excel workbook
├── requirements.txt    ← Python dependencies
├── backend-client.js   ← Frontend JS to call this API
└── README.md           ← This file
```

---

## Important: Free Tier Note
Render.com free tier **sleeps after 15 minutes** of inactivity.
First request after sleep takes ~30 seconds to wake up.

**Solution**: Use a free uptime monitor (UptimeRobot.com) to ping `/api/ping` every 14 minutes.
This keeps the server warm during business hours.

---

## Environment Variables Reference
```
RAZORPAY_KEY_ID      — Razorpay Key ID (rzp_live_...)
RAZORPAY_KEY_SECRET  — Razorpay Key Secret
FLASK_ENV            — "production" or "development"
PORT                 — Auto-set by Render (don't set manually)
```
