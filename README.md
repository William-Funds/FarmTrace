# 🌿 FarmTrace — Digital Trade Passport System

> **TEXPO 2026 First Place Winner** — Telco Zimbabwe National Technology Exposition

FarmTrace is a farm-to-market traceability system built on Raspberry Pi 5 that generates cryptographically secured **Digital Trade Passports** for smallholder farmer produce. It connects rural farmers directly to verified buyers through automated documentation, IoT sensor data, and real-time email delivery.

---

## 🎯 The Problem

Smallholder farmers in rural Zimbabwe grow quality produce but sell at **20% below market price** because buyers demand GPS-verified origin, handling records, and minimum orders of 5–30 tonnes. Without digital proof, farmers remain invisible to regional markets.

**FarmTrace solves this.**

---

## ✅ What It Does

When a farmer brings produce to the cooperative collection point:

1. **Weighs produce** on a calibrated HX711 load cell scale
2. **Captures a photo** of the farmer and produce with Pi AI Camera
3. **Records farm location** via OpenStreetMap geolocation lookup
4. **Logs environmental conditions** — temperature and humidity via DHT22 sensor
5. **Generates a 4-page Digital Trade Passport** PDF in under 2 minutes
6. **Emails the passport automatically** to the buyer with full batch details
7. **SHA-256 integrity hashes** the passport for tamper detection

---

## 🖥️ System Architecture

```
FIELD LAYER                    HUB LAYER                      BUYER LAYER
───────────                    ─────────                      ───────────
DHT22 Sensor      ──────►     Raspberry Pi 5                 Buyer Email
HX711 Scale       ──────►     Touchscreen UI        ──────►  PDF Passport
Pi AI Camera      ──────►     SQLite Database                QR Verification
LED Indicators    ◄──────     Passport Generator
                              Location Lookup
                              Email Sender
```

---

## 🔧 Hardware Components

| Component | Purpose | Cost (USD) |
|-----------|---------|-----------|
| Raspberry Pi 5 (4GB) | Main hub processor | ~$60 |
| Pi AI Camera | Farmer photo capture | ~$70 |
| DHT22 Sensor Module | Temperature + humidity | ~$3 |
| HX711 + 5kg Load Cell | Produce weighing | ~$6 |
| Green LED (GPIO 18) | Heartbeat / system alive | ~$0.50 |
| Yellow LED (GPIO 23) | Activity indicator | ~$0.50 |
| Red LED (GPIO 24) | Passport ready indicator | ~$0.50 |
| **Total per hub** | | **~$148** |

**Cost per farmer: ~$50 (one-time, no subscription fees)**

---

## 📌 GPIO Wiring

| Component | GPIO | Pi Pin |
|-----------|------|--------|
| DHT22 OUT | GPIO 4 | Pin 7 |
| HX711 DOUT | GPIO 17 | Pin 11 |
| HX711 SCK | GPIO 27 | Pin 13 |
| HX711 VCC | — | Pin 2 (5V) |
| LED Green | GPIO 18 | Pin 12 |
| LED Yellow | GPIO 23 | Pin 16 |
| LED Red | GPIO 24 | Pin 18 |

---

## 📄 Digital Trade Passport

Each passport is a 4-page PDF containing:

| Page | Content |
|------|---------|
| 1 — Cover | Batch ID, QR code, crop type, weight, cooperative details |
| 2 — Farmer Records | Name, location, weight, harvest date, embedded photo per farmer |
| 3 — Sensor Log | Temperature/humidity data + COMESA/SADC compliance checklist |
| 4 — Chain of Custody | Signature blocks for farmer, cooperative, border inspector, buyer |

---

## 🗂️ Project Structure

```
farmtrace/
├── config/
│   └── hub_config.json          # All settings — pins, crop codes, email
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
│   └── gsm_manager.py           # GSM module stub (SIM800L/SIM7600)
├── passport/
│   └── passport_generator.py    # ReportLab 4-page PDF with QR code
├── cloud_sync/
│   └── google_sync.py           # Google Sheets + Drive sync (optional)
├── ui/
│   └── app.py                   # Tkinter touchscreen UI
├── data/
│   ├── photos/                  # Captured farmer photos
│   └── passports/               # Generated passport PDFs
├── logs/                        # Daily log files
├── requirements.txt             # Python dependencies
└── SETUP.md                     # Full installation guide
```

---

## 🚀 Installation

### 1. System packages (on Raspberry Pi OS)

```bash
sudo apt update && sudo apt install -y \
    python3 python3-venv git \
    libatlas-base-dev libopenjp2-7 \
    python3-lgpio swig libgpiod-dev
```

### 2. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/farmtrace.git
cd farmtrace
```

### 3. Create virtual environment

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
pip install adafruit-circuitpython-dht adafruit-blinka rpi-lgpio
```

### 5. Configure

Edit `config/hub_config.json` with your cooperative name, email credentials, and sensor pins.

### 6. Run

```bash
python -m pi5_hub.main
```

---

## 🧪 Simulate Mode

Run on any computer without hardware by setting `"simulate_sensors": true` in `hub_config.json`. All sensors return realistic random values — perfect for testing the UI and passport generation.

---

## 🌍 LED Status Indicators

| LED | Colour | Behaviour | Meaning |
|-----|--------|-----------|---------|
| GPIO 18 | 🟢 Green | Slow blink always | System alive |
| GPIO 23 | 🟡 Yellow | Fast blink | Task in progress |
| GPIO 24 | 🔴 Red | Solid ON | Passport generated |

---

## 📧 Email Configuration

FarmTrace uses Gmail SMTP with an App Password. No Google API needed.

1. Enable 2-Step Verification at myaccount.google.com
2. Generate an App Password at myaccount.google.com/apppasswords
3. Add to `hub_config.json`:

```json
"email": {
    "enabled": true,
    "sender_email": "your@gmail.com",
    "sender_name": "Your Cooperative",
    "app_password": "xxxx xxxx xxxx xxxx"
}
```

---

## 🏆 Recognition

- **🥇 First Place — TEXPO 2026**, Telco Zimbabwe National Technology Exposition
- Selected for **Cape Town 2026** regional innovation showcase
- Finalist — **WFP Zimbabwe Agri-Forge Innovation Challenge 2026**

---

## 🗺️ Roadmap

- [x] DHT22 temperature and humidity sensor
- [x] Pi AI Camera photo capture
- [x] HX711 load cell weighing
- [x] 4-page PDF passport generation
- [x] Automated buyer email with PDF attachment
- [x] OpenStreetMap location lookup
- [x] SHA-256 tamper detection
- [x] LED status indicators
- [ ] GSM module (SIM800L/SIM7600) for offline SMS alerts
- [ ] AgroLink marketplace web platform
- [ ] Google Sheets live buyer dashboard
- [ ] Bluetooth Pico W field nodes
- [ ] USSD/SMS farmer interface

---

## 👥 Team

| Name | Role |
|------|------|
| William Fundirwa | Co-Founder & Team Leader |
| Emmanuel Chidhobwe | Co-Founder & Tech Lead |
| MacDonald Zivanai | Co-Founder & Business Lead |
| Beloved Mapise | Co-Founder & Communications Lead |

---

## 📜 License

MIT License — free to use, modify and distribute with attribution.

---

## 🌿 About

> *"Giving smallholder farmers the proof, visibility and scale they deserve."*

Built in Zimbabwe. Running on Raspberry Pi. Owned by the cooperative.
