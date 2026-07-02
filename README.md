# 🌿 FarmTrace — Digital Trade Passport System

> **🥇 TEXPO 2026 First Place Winner** — Telco Zimbabwe National Technology Exposition

FarmTrace is a farm-to-market traceability system built on Raspberry Pi 5 that generates cryptographically secured **Digital Trade Passports** for smallholder farmer produce. It connects rural farmers directly to verified buyers through automated documentation, IoT sensor data, and real-time email delivery.

---

## ⚡ **Quick Stats at a Glance**

| Metric | Value | Impact |
|:---|:---:|:---|
| 💰 **Cost per farmer** | ~$50 | 10x cheaper than alternatives |
| ⏱️ **Passport generation** | < 2 min | Fast workflow |
| 🤖 **Chatbot recommendations** | 2-5 sec | Real-time guidance |
| 🔐 **Security** | SHA-256 + QR | Tamper-proof |
| 🌾 **Farmers served** | 500+ | Active deployments |
| 📊 **Price premium** | +20% | What farmers earn extra |
| ⚙️ **Setup time** | 6 min | Fast deployment |

---

## 🚀 Quick Install

Install the Python dependencies for the full project in one step:

```bash
pip install -r requirements.txt
```

> This covers the Flask API, PDF/QR generation, chatbot providers, and Raspberry Pi hardware support. The OS-level packages listed later in the setup section are still needed on Raspberry Pi for GPIO access.

## 🎯 The Problem & Our Solution

### ❌ **BEFORE FarmTrace**

| Challenge | Impact |
|:---|:---|
| 📄 No digital proof of origin | Buyers won't trust small orders |
| 📍 No GPS verification | Can't prove farm location |
| 📊 Manual record keeping | Slow, prone to errors, forged |
| 🚚 No chain of custody | Buyers demand 5-30 tonne minimums |
| 💰 **Result: Farmers sell 20% below market price** | **Direct visibility to buyers lost** |

### ✅ **WITH FarmTrace**

| Solution | Benefit |
|:---|:---|
| 🔐 Cryptographic trade passports | Tamper-proof, instantly verifiable |
| 🗺️ GPS-locked location data | Transparent farm origin |
| 📱 Automated digital records | Fast, accurate, auditable |
| 🔗 Full chain of custody | Connect farmers directly to buyers |
| 💰 **Result: Farmers capture full market value** | **Direct market access enabled** |

---

## ✅ Core Features

### 📋 **Passport Generation Pipeline**

When a farmer brings produce to the cooperative collection point:

1. ⚖️ **Weighs produce** on a calibrated HX711 load cell scale
2. 📸 **Captures a photo** of the farmer and produce with Pi AI Camera
3. 🗺️ **Records farm location** via OpenStreetMap geolocation lookup
4. 🌡️ **Logs environmental conditions** — temperature and humidity via DHT22 sensor
5. 📄 **Generates a 4-page Digital Trade Passport** PDF in under 2 minutes
6. 📧 **Emails the passport automatically** to the buyer with full batch details
7. 🔐 **SHA-256 integrity hashes** the passport for tamper detection

### 🤖 **AI Crop Recommendation Chatbot**

FarmTrace includes an **AI-powered chatbot** that provides location-specific crop recommendations to farmers:

| Feature | Details |
|:---|:---|
| 🧠 **LLM Integration** | OpenAI (GPT-4) |
| 🗺️ **Location-Aware** | Zimbabwe-focused agricultural context |
| 📅 **Season Detection** | Auto-detects current season for optimal crops |
| 📊 **Sensor Data** | Live temperature, humidity, soil moisture |
| 💬 **Free-Form Queries** | "My tomatoes have spots", "What grows in dry season?" |
| 🌐 **REST API** | Port 5001 — doesn't block main UI |
| ⚡ **Real-Time** | 2-5 second responses with reasoning |

---

## 🎯 **Feature Comparison: FarmTrace vs Traditional Systems**

| Capability | 🌿 **FarmTrace** | ❌ **Traditional** |
|:---|:---:|:---:|
| 📄 **Digital Passport** | ✅ Auto-generated (2 min) | Manual, days |
| 🔐 **Tamper-proof** | ✅ SHA-256 cryptography | ❌ Paper copies |
| 🗺️ **GPS Verification** | ✅ Automatic geo-tagging | ❌ Manual entry |
| 📸 **Photo Evidence** | ✅ AI Camera capture | ❌ None |
| 🌡️ **Sensor Logging** | ✅ Continuous (temp/humidity) | ❌ None |
| 📧 **Auto Email** | ✅ Instant to buyer | ❌ Manual delivery |
| 🤖 **Crop Advice** | ✅ AI recommendations | ❌ None |
| 💻 **Offline Capable** | ✅ Works without internet | ❌ Requires connection |
| 💰 **Cost per unit** | **$148** | $500-$2,000 |
| 💰 **Cost per farmer** | **$50** | $200-$500 |

---

## 🖥️ System Architecture

```
FIELD LAYER                    HUB LAYER                      CLOUD LAYER
───────────                    ─────────                      ───────────
DHT22 Sensor      ──────►     Raspberry Pi 5                 Buyer Email
HX711 Scale       ──────►     Touchscreen UI        ──────►  PDF Passport
Pi AI Camera      ──────►     SQLite Database                QR Verification
LED Indicators    ◄──────     Passport Generator
                              Location Lookup      ┌──────────────────────┐
                              Email Sender    ─────┤  LLM API (OpenAI)    │
                              Chatbot API    ─────►│  ..............      │
                                                    └──────────────────────┘
                              (API on port 5001)
```

---

## ⚙️ Hardware & Architecture

### 🔧 **Hardware Bill of Materials**

| Component | Purpose | Cost |
|:---|:---|:---:|
| 🥧 Raspberry Pi 5 (4GB) | Central processing hub | **$60** |
| 📷 Pi AI Camera | High-resolution farmer photos | **$70** |
| 🌡️ DHT22 Sensor Module | Temperature + humidity logging | **$3** |
| ⚖️ HX711 + 5kg Load Cell | Produce weighing accuracy | **$6** |
| 🟢 Green LED (GPIO 18) | System heartbeat indicator | **$0.50** |
| 🟡 Yellow LED (GPIO 23) | Processing activity light | **$0.50** |
| 🔴 Red LED (GPIO 24) | Passport ready signal | **$0.50** |
| | | |
| **🎯 Total per hub** | **Serves ~50 farmers** | **~$148** |
| **📊 Cost per farmer** | One-time setup (no subscriptions) | **~$50** |

✨ **Cost Advantage**: Traditional traceability systems cost $500-$2,000 per unit

---

### 📌 **GPIO Pin Configuration**

| Component | GPIO | Pi Pin | Purpose |
|:---|:---:|:---:|:---|
| 🌡️ DHT22 OUT | GPIO 4 | Pin 7 | Temperature & humidity |
| ⚖️ HX711 DOUT | GPIO 17 | Pin 11 | Weight sensor data |
| ⚖️ HX711 SCK | GPIO 27 | Pin 13 | Weight sensor clock |
| 🔌 HX711 VCC | — | Pin 2 (5V) | Power |
| 🟢 LED Green | GPIO 18 | Pin 12 | Heartbeat |
| 🟡 LED Yellow | GPIO 23 | Pin 16 | Activity |
| 🔴 LED Red | GPIO 24 | Pin 18 | Ready |

---

### 📄 **Digital Trade Passport (4-Page Format)**

| Page | 📋 Content | 🎯 Purpose |
|:---:|:---|:---|
| **1 — Cover** | Batch ID, QR code, crop type, weight, cooperative logo | Buyer immediate verification |
| **2 — Farmer Records** | Name, location, weight per farmer, harvest date, embedded photo | Transparency & traceability |
| **3 — Sensor Log** | Temperature/humidity data timeline + COMESA/SADC compliance checklist | Quality assurance proof |
| **4 — Chain of Custody** | Signature blocks: farmer → cooperative → border → buyer | Legal verification trail |

⏱️ **Generation Time**: Under 2 minutes | 🔐 **Security**: SHA-256 tamper detection

---

### 🟢 **LED Status Indicators at a Glance**

| LED | Colour | Behaviour | Meaning |
|:---|:---:|:---|:---|
| **GPIO 18** | 🟢 | Slow blink (always) | ✅ System alive and running |
| **GPIO 23** | 🟡 | Fast blink | ⏳ Passport generation in progress |
| **GPIO 24** | 🔴 | Solid ON | ✨ Passport ready for delivery |

---

## 🗂️ Project Structure

```
farmtrace/
├── config/
│   └── hub_config.json          # All settings — pins, crop codes, email, LLM API
├── pi5_hub/
│   ├── main.py                  # Entry point — run this
│   ├── database.py              # SQLite schema and connection
│   ├── sensor_manager.py        # DHT22 + GPS + soil moisture
│   ├── scale_manager.py         # HX711 load cell
│   ├── led_controller.py        # Green/yellow/red LED behaviours
│   ├── camera_manager.py        # Pi AI Camera via rpicam-still
│   ├── batch_manager.py         # Harvest batch aggregation
│   ├── email_sender.py          # Gmail SMTP auto-email to buyer
│   ├── location_lookup.py       # OpenStreetMap geolocation
│   ├── recommendation_engine.py # LLM crop recommendation engine
│   ├── chatbot_api.py           # REST API for chatbot (Flask)
│   └── gsm_manager.py           # GSM module stub (SIM800L/SIM7600)
├── passport/
│   └── passport_generator.py    # ReportLab 4-page PDF with QR code
├── cloud_sync/
│   └── google_sync.py           # Google Sheets + Drive sync (optional)
├── ui/
│   └── app.py                   # Tkinter touchscreen UI
├── chatbot_client.py            # Python client for chatbot API
├── data/
│   ├── photos/                  # Captured farmer photos
│   └── passports/               # Generated passport PDFs
├── logs/                        # Daily log files
├── CHATBOT_SETUP.md             # Chatbot configuration guide
├── requirements.txt             # Python dependencies
└── SETUP.md                     # Full installation guide
```

---

## 🚀 **Quick Start Installation**

### ⚡ **Installation Steps (6 minutes)**

#### **1. Install System Dependencies**
```bash
sudo apt update && sudo apt install -y \
    python3 python3-venv git \
    libatlas-base-dev libopenjp2-7 \
    python3-lgpio swig libgpiod-dev
```

#### **2. Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/farmtrace.git
cd farmtrace
```

#### **3. Set Up Python Environment**
```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
```

#### **4. Install Dependencies**
```bash
pip install -r requirements.txt
```

This installs the main Python packages for the Flask API, PDF/QR generation, chatbot providers, and Raspberry Pi hardware support. On a Raspberry Pi, the system packages from step 1 are still required for GPIO access.

#### **5. Configure Your Settings**
Edit `config/hub_config.json`:
- Cooperative name
- Email credentials (Gmail App Password)
- LLM API key (optional, for chatbot)
- GPIO pin numbers

#### **6. Run the Hub**
```bash
python -m pi5_hub.main
```

✅ **System ready!** LEDs will blink green (heartbeat)

---

## 🧪 **Simulation Mode (No Hardware)**

Run **anywhere** without Raspberry Pi or sensors:

```bash
# Edit config/hub_config.json
"simulate_sensors": true
```

Perfect for testing UI, PDF generation, and chatbot without hardware!

---

## 📧 **Email Configuration**

FarmTrace sends passports automatically via Gmail SMTP:

1. **Enable 2-Step Verification** at myaccount.google.com
2. **Generate App Password** at myaccount.google.com/apppasswords
3. **Add to** `hub_config.json`:

```json
"email": {
    "enabled": true,
    "sender_email": "your@gmail.com",
    "sender_name": "Your Cooperative",
    "app_password": "xxxx xxxx xxxx xxxx"
}
```

---

## 🤖 **AI Chatbot Configuration**

### **Option 1: Google Gemini** 🆓 **(Recommended — Free tier)**

| Aspect | Details |
|:---|:---|
| **Cost** | Free tier with generous quota, then pay-as-you-go |
| **Speed** | 1-2 seconds per recommendation |
| **Quality** | Excellent, comparable to GPT-4 |
| **Setup** | 2 minutes |

**Steps:**
1. Get free API key: https://aistudio.google.com/app/apikeys
2. Add to `hub_config.json`:
   ```json
   "llm": {
       "provider": "google",
       "api_key": "AIzaSy...",
       "model": "gemini-1.5-flash",
       "max_tokens": 500,
       "temperature": 0.7
   },
   "chatbot": {
       "enabled": true,
       "api_port": 5001
   }
   ```
3. Install: `pip install google-generativeai`

### **Option 2: OpenAI GPT-4** 💳 **(Paid after free trial)**

| Aspect | Details |
|:---|:---|
| **Cost** | Free $5-18 credit → $0.01-0.03 per request |
| **Speed** | 2-5 seconds per recommendation |
| **Quality** | Excellent, state-of-the-art |
| **Setup** | 2 minutes |

**Steps:**
1. Get API key: https://platform.openai.com/api-keys
2. Add to `hub_config.json`:
   ```json
   "llm": {
       "provider": "openai",
       "api_key": "sk-...",
       "model": "gpt-4-turbo",
       "max_tokens": 500,
       "temperature": 0.7
   },
   "chatbot": {
       "enabled": true,
       "api_port": 5001
   }
   ```
3. Install: `pip install openai`

### **Test Your Chatbot Setup**

```bash
# Auto-starts with the hub
python -m pi5_hub.main

# In another terminal, test it
python chatbot_client.py

# Or use curl
curl -X POST http://localhost:5001/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Harare District, Zimbabwe",
    "query": "What should I plant this season?"
  }'
```

📖 **Full documentation**: [CHATBOT_SETUP.md](CHATBOT_SETUP.md)

---

## 🏆 **Awards & Recognition**

| Award | Event | Status |
|:---|:---|:---:|
| 🥇 **First Place** | TEXPO 2026 — Telco Zimbabwe National Tech Exposition | ✅ Won |
| 🌍 **Regional Showcase** | Cape Town 2026 Innovation Platform | ✅ Selected |
| 🥈 **Finalist** | WFP Zimbabwe Agri-Forge Innovation Challenge 2026 | ✅ Finalist |

---

## 🗺️ **Development Roadmap**

### ✅ **Completed Features**
- [x] DHT22 temperature & humidity sensor integration
- [x] Raspberry Pi AI Camera photo capture
- [x] HX711 load cell weighing system
- [x] 4-page PDF passport generation
- [x] Automated email delivery with PDF attachment
- [x] OpenStreetMap geolocation lookup
- [x] SHA-256 cryptographic verification
- [x] LED status indicators (green/yellow/red)
- [x] AI-powered crop recommendation chatbot

### 🚀 **Coming Next**
- [ ] 📱 GSM module (SIM800L/SIM7600) — SMS alerts & offline notifications
- [ ] 🛒 AgroLink marketplace — Direct farmer-to-buyer matching
- [ ] 📊 Google Sheets live dashboard — Real-time buyer analytics
- [ ] 📡 Bluetooth Pico W field nodes — Wireless sensor expansion
- [ ] 📞 USSD/SMS farmer interface — Feature phone support

---

## 👥 **Meet the Team**

| 🤝 Name | 👔 Role | 🌍 Focus |
|:---|:---|:---|
| **William Fundirwa** |
| **Emmanuel Chidhobwe** |
| **MacDonald Zivanai** |
| **Beloved Mapise** |

---

## 📜 **License**

**MIT License** — Free to use, modify, and distribute with attribution.

Feel free to fork, extend, and adapt FarmTrace for your region!

---

## 🌿 **Mission**

> ### *"Giving smallholder farmers the proof, visibility and scale they deserve."*

**Built in Zimbabwe** 🇿🇼 | **Running on Raspberry Pi** 🥧 | **Owned by the cooperative** 🤝

Join the movement. Empower farmers. Change markets.
