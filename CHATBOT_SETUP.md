# FarmTrace Chatbot — Setup & Usage Guide

The FarmTrace chatbot provides AI-powered crop recommendations to farmers based on:
- **Location** (region-specific conditions)
- **Season** (Zimbabwe's climate seasons)
- **Sensor data** (temperature, humidity, soil moisture)
- **Free-text queries** (farmer questions/concerns)

---

## 🚀 Quick Start

Install the full Python dependency set for the repository in one step:

```bash
pip install -r requirements.txt
```

### 1. Install Dependencies

Install the repository's Python dependencies in one step:

```bash
pip install -r requirements.txt
```

The file includes the Flask API dependencies plus the optional OpenAI and Google Gemini packages. If you prefer to install only the chatbot stack manually, the equivalent packages are:

```bash
pip install openai flask requests
```

For Google Gemini instead of OpenAI:
```bash
pip install google-generativeai flask requests
```

### 2. Configure API Key

Edit `config/hub_config.json` and add your LLM API key:

#### For OpenAI:
```json
"llm": {
  "provider": "openai",
  "api_key": "sk-...",
  "model": "gpt-4-turbo",
  "max_tokens": 500,
  "temperature": 0.7
}
```

Get your OpenAI API key from: https://platform.openai.com/api-keys

#### For Google Gemini:
```json
"llm": {
  "provider": "google",
  "api_key": "AIzaSy...",
  "model": "gemini-1.5-pro",
  "max_tokens": 500,
  "temperature": 0.7
}
```

Get your Gemini API key from: https://aistudio.google.com/app/apikeys

### 3. Start the Hub

```bash
python -m pi5_hub.main
```

The chatbot API will start automatically on `http://localhost:5001`

### 4. Verify It's Working

Check the health endpoint:
```bash
curl http://localhost:5001/health
```

Response:
```json
{"status": "ok", "service": "chatbot-api"}
```

---

## 📡 API Endpoints

### `GET /health`
Simple health check.

**Response:**
```json
{"status": "ok", "service": "chatbot-api"}
```

### `GET /status`
Get detailed service status.

**Response:**
```json
{
  "status": "running",
  "engine_enabled": true,
  "llm_provider": "openai",
  "llm_model": "gpt-4-turbo",
  "sensors_connected": true,
  "timestamp": "2024-07-01T10:30:45.123456"
}
```

### `POST /recommendations`
Get crop recommendations for a location.

**Request:**
```json
{
  "location": "Harare District, Zimbabwe",
  "query": "What should I plant?",
  "include_sensor_data": true
}
```

**Response:**
```json
{
  "success": true,
  "recommendations": ["Maize", "Tobacco", "Cotton"],
  "reasoning": "Based on temperature (25°C) and current season...",
  "sensor_data": {
    "temp_c": 25.5,
    "humidity": 65.3,
    "soil_pct": 72.1,
    "lat": -17.8292,
    "lon": 31.0522,
    "ts": "2024-07-01T10:30:00Z"
  },
  "location": "Harare District, Zimbabwe",
  "season": "Summer",
  "timestamp": "2024-07-01T10:30:45.123456"
}
```

### `POST /query`
Free-form query endpoint (e.g., problem diagnosis, specific questions).

**Request:**
```json
{
  "query": "My tomatoes have brown spots on leaves",
  "lat": -17.8292,
  "lon": 31.0522
}
```

**Response:**
Same format as `/recommendations`

---

## 💻 Using the Python Client

Import and use the client in your code:

```python
from chatbot_client import FarmTraceChatbotClient

client = FarmTraceChatbotClient("http://localhost:5001")

# Get recommendations
response = client.get_recommendations(
    location="Harare District, Zimbabwe",
    query="What crops should I plant this season?"
)

if response.get("success"):
    print("Recommendations:", response.get("recommendations"))
    print("Reasoning:", response.get("reasoning"))
else:
    print("Error:", response.get("error"))
```

Or run the example script:
```bash
python chatbot_client.py
```

---

## 🔧 Configuration Options

In `config/hub_config.json`:

```json
{
  "llm": {
    "provider": "openai",              // "openai" or "google"
    "api_key": "YOUR_API_KEY",         // REQUIRED
    "model": "gpt-4-turbo",            // Model name
    "max_tokens": 500,                 // Response length limit
    "temperature": 0.7                 // 0.0=deterministic, 1.0=creative
  },
  "chatbot": {
    "enabled": true,                   // Enable/disable chatbot
    "api_host": "0.0.0.0",             // Listen on all interfaces
    "api_port": 5001                   // API port
  }
}
```

---

## 📊 How It Works

1. **Location + Season Detection**: System determines current Zimbabwe season based on month
2. **Sensor Integration**: Pulls live temp/humidity/soil moisture from DHT22 and sensors
3. **Prompt Building**: Constructs detailed agricultural context for the LLM
4. **LLM Call**: Sends to OpenAI or Google Gemini with farmer's query
5. **Response Parsing**: Extracts structured recommendations from LLM output
6. **Return**: JSON response with crop recommendations and reasoning

---

## 🌱 Example Scenarios

### Scenario 1: Spring Planting Guide
```bash
curl -X POST http://localhost:5001/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Chinhoyi, Zimbabwe",
    "query": "I have a 1-hectare plot. What should I plant for maximum profit?"
  }'
```

### Scenario 2: Pest Diagnosis
```bash
curl -X POST http://localhost:5001/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "My cotton plants have white bugs and webbing. What is this and how do I treat it?",
    "lat": -17.7,
    "lon": 31.2
  }'
```

### Scenario 3: Climate-Adaptive Farming
```bash
curl -X POST http://localhost:5001/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Masvingo Province, Zimbabwe",
    "query": "We had a very dry season last year. What drought-resistant crops should we try?"
  }'
```

---

## 🐛 Troubleshooting

### API not accessible
- Ensure `pi5_hub.main` is running
- Check that port 5001 is not blocked
- Try: `curl http://localhost:5001/health`

### LLM not configured
```
LLM not configured in hub_config.json
```
- Add `api_key` to the `llm` section in `hub_config.json`

### Rate limit errors
- OpenAI: Wait a few minutes, then retry
- Gemini: Consider upgrading your API plan

### Sensor data not included
- Ensure sensors are running and `SensorManager` is started
- Check `include_sensor_data` is `true` in the request

---

## 🔐 Security Notes

- **API Key**: Keep your LLM API key private. Use environment variables in production:
  ```bash
  export OPENAI_API_KEY="sk-..."
  ```
  Then read from `os.environ["OPENAI_API_KEY"]`

- **Firewall**: The API listens on all interfaces by default. In production, restrict with:
  ```json
  "chatbot": {
    "api_host": "127.0.0.1"  // Only localhost
  }
  ```

- **Rate Limiting**: Consider adding rate limiting middleware for public deployments

---

## 📚 LLM Model Comparison

| Provider | Model | Cost | Latency | Quality |
|----------|-------|------|---------|---------|
| OpenAI | gpt-4-turbo | $10-$30/month (free tier available) | ~2-5s | Excellent |
| OpenAI | gpt-3.5-turbo | $5-$15/month (free tier available) | ~1-2s | Good |
| Google | gemini-1.5-pro | Free tier available | ~3-4s | Excellent |
| Google | gemini-1.5-flash | Free tier available | ~1-2s | Very Good |

---

## 🚀 Next Steps

1. **Integrate into UI**: Add a chat widget in `ui/app.py` that calls the chatbot API
2. **SMS Support**: Add SMS query support via the GSM module
3. **Farmer Portal**: Create a web portal for farmers to access recommendations
4. **Training Data**: Fine-tune with local Zimbabwe agricultural data
5. **Offline Mode**: Cache recommendations for offline access

---

## 📞 Support

For issues:
1. Check the logs in `logs/farmtrace_YYYYMMDD.log`
2. Verify API key is correct in `hub_config.json`
3. Test the API directly: `curl http://localhost:5001/status`
