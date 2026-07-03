# 🌾 Amar Krishi (আমার কৃষি)
### Digital Farming Assistance Platform — Final Semester University Project

Amar Krishi is a bilingual (Bangla / English), AI-assisted web platform that helps Bangladeshi
farmers make better decisions on crop selection, disease detection, weather alerts, market
prices, and farm finances — all through a simple, low-literacy-friendly interface.

---

## 1. Features

| Module | Description |
|---|---|
| 🔐 Authentication | Register, login, forgot password, remember-me, hashed passwords, session auth |
| 📊 Dashboard | Weather, disease alerts, market summary, crop status, quick actions, income/expense |
| 🌱 Crop Advisory | Recommends crops by soil type, district, season, water availability |
| 🦠 AI Disease Detection | Upload a leaf photo → get disease name, symptoms, treatment, medicine (placeholder AI, swappable with a real TensorFlow/Teachable Machine model) |
| ☁️ Weather & Alerts | Temperature, humidity, wind, rain probability, flood/heat/storm/frost alerts, irrigation timing |
| 💰 Market Prices | Live price table + Chart.js 7-day trend, search/filter/sort |
| 💸 Expense Tracker | Income vs expense logging with doughnut chart summary |
| 🌐 Bilingual UI | Every static string comes from `translations.py`; instant switch, no reload-breaking |
| 🧑‍🌾 Profile & Settings | Edit profile, change language, notification preferences |
| 🤖 AI Assistant, Forum, Expert Consultation, Subsidy/Loans, Pest/Yield Prediction, Fertilizer, Irrigation | Demo UI modules ready to be wired to real services/models |

---

## 2. Technology Stack

- **Frontend:** HTML5, CSS3 (custom, no framework), Vanilla JavaScript, Chart.js, Font Awesome, Google Fonts (Poppins / Hind Siliguri)
- **Backend:** Python 3, Flask, Flask-SQLAlchemy
- **Database:** MySQL (schema in `database/schema.sql`) — MongoDB optional for AI prediction logs
- **Image Processing:** OpenCV / TensorFlow placeholder hook in `routes/main_routes.py`

---

## 3. Folder Structure

```
AmarKrishi/
├── app.py                  # Flask entry point
├── config.py                # App + DB configuration
├── translations.py          # EN/BN translation dictionary
├── requirements.txt
├── README.md
├── database/
│   └── schema.sql           # Full MySQL schema + sample data
├── models/
│   └── models.py            # SQLAlchemy ORM models
├── routes/
│   ├── auth_routes.py       # Login / Register / Logout
│   └── main_routes.py       # Dashboard + all feature modules
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   ├── images/
│   └── uploads/             # Disease-detection leaf images
└── templates/
    ├── layouts/base.html    # Sidebar + topbar shared shell
    ├── login.html / register.html / forgot_password.html
    ├── dashboard.html
    ├── crop.html / disease.html / market.html / weather.html
    ├── profile.html / settings.html / expense.html
    └── feature_placeholder.html
```

---

## 4. Installation Guide

### Prerequisites
- Python 3.10+
- MySQL Server 8.0+
- pip

### Steps

```bash
# 1. Clone / unzip the project
cd AmarKrishi

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables (or edit config.py directly)
export SECRET_KEY="your-secret-key"
export MYSQL_USER="root"
export MYSQL_PASSWORD="your-password"
export MYSQL_DB="amar_krishi"

# 5. Set up the database (see section 5 below)

# 6. Run the app
python app.py
```

Visit **http://localhost:5000** — you'll be redirected to `/login`.
Register a new farmer account to get started.

---

## 5. Database Setup

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS amar_krishi CHARACTER SET utf8mb4;"
mysql -u root -p amar_krishi < database/schema.sql
```

This creates all tables (`users`, `crops`, `diseases`, `disease_reports`,
`crop_recommendations`, `market_prices`, `weather`, `transactions`, `notifications`)
and inserts realistic sample data (Bangladeshi districts, crops, diseases, market prices).

Alternatively, `app.py` will call `db.create_all()` on first run to create tables
from the SQLAlchemy models directly (useful for quick local testing), but
`schema.sql` is the canonical, fully-commented schema for grading/demo purposes.

---

## 6. Project Features Recap

- Fully responsive (desktop / tablet / mobile) with a collapsible sidebar
- Soft shadows, 15px rounded cards, green/yellow agricultural theme
- Language dictionary pattern — adding a new language only requires extending `translations.py`
- Secure password hashing (Werkzeug), session-based auth, server-side input handling
- Placeholder AI model hook clearly marked in `routes/main_routes.py` (`disease_detection`) for
  swapping in a real TensorFlow / Teachable Machine `.h5` or `.tflite` model later

---

## 7. Future Scope

- Replace the placeholder disease-detection logic with a trained CNN model (TensorFlow/Keras or Teachable Machine export)
- Integrate a live weather API (OpenWeatherMap key slot already in `config.py`)
- Real SMS gateway integration (currently a demo toggle) for flood/storm alerts
- MongoDB-backed AI prediction logging for analytics
- Real-time chat backend for the AI Assistant and Expert Consultation modules
- Payment/subsidy application workflow with government API integration
- Admin panel for managing crops, diseases, and market price feeds

---

## 8. Security Notes

- Passwords are hashed with Werkzeug's `generate_password_hash` / `check_password_hash`
- SQLAlchemy ORM is used throughout, preventing raw SQL injection
- File uploads are restricted by extension (`png`, `jpg`, `jpeg`) and size (5 MB max)
- `SECRET_KEY` and DB credentials should always be set via environment variables in production, never hard-coded

---

## 9. Credits

Built as a Final Semester University Project — **Amar Krishi: Digital Farming
Assistance Platform**, designed for Bangladeshi farmers with simplicity and
accessibility as the top priority.
