"""
FarmTrace — Recommendation Engine
Uses LLM to provide crop recommendations based on:
- Location and season
- Current sensor data (temperature, humidity)
- Free-text farmer queries
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

log = logging.getLogger(__name__)


class RecommendationEngine:
    def __init__(self, config: dict):
        """Initialize the recommendation engine with LLM configuration."""
        self.cfg = config.get("llm", {})
        self.provider = self.cfg.get("provider", "openai").lower()
        self.api_key = self.cfg.get("api_key")
        self.model = self.cfg.get("model", "gpt-4-turbo")
        self.max_tokens = self.cfg.get("max_tokens", 500)
        self.temperature = self.cfg.get("temperature", 0.7)

        if not self.api_key:
            log.warning("LLM API key not configured in hub_config.json")
            self.enabled = False
        else:
            self.enabled = True
            self._init_client()

    def _init_client(self):
        """Initialize the LLM client based on provider."""
        if self.provider == "openai":
            try:
                import openai
                openai.api_key = self.api_key
                self.client = openai.ChatCompletion
                log.info("OpenAI client initialized")
            except ImportError:
                log.error("openai package not installed. Install with: pip install openai")
                self.enabled = False
        elif self.provider == "google":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model)
                log.info("Google Gemini client initialized")
            except ImportError:
                log.error("google-generativeai package not installed")
                self.enabled = False
        else:
            log.error(f"Unknown LLM provider: {self.provider}")
            self.enabled = False

    def get_recommendations(
        self,
        location: str,
        query: str,
        sensor_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get crop recommendations from the LLM.

        Args:
            location: Location name (e.g., "Harare District, Zimbabwe")
            query: Free-text farmer query (e.g., "What crops should I plant?")
            sensor_data: Dict with 'temp_c', 'humidity', 'soil_pct', 'lat', 'lon'

        Returns:
            Dict with 'recommendations', 'reasoning', 'timestamp', 'success'
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "LLM not configured",
                "recommendations": [],
                "timestamp": datetime.utcnow().isoformat(),
            }

        try:
            # Get current season based on month
            season = self._get_season()

            # Build the prompt
            prompt = self._build_prompt(location, season, query, sensor_data)

            # Call LLM
            if self.provider == "openai":
                response = self._call_openai(prompt)
            elif self.provider == "google":
                response = self._call_google(prompt)
            else:
                return {
                    "success": False,
                    "error": "Unknown provider",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            return {
                "success": True,
                "recommendations": response.get("recommendations", []),
                "reasoning": response.get("reasoning", ""),
                "timestamp": datetime.utcnow().isoformat(),
                "location": location,
                "season": season,
                "sensor_data": sensor_data,
            }

        except Exception as e:
            log.error(f"Error getting recommendations: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _get_season(self) -> str:
        """Determine the current season in Zimbabwe (Southern Hemisphere)."""
        month = datetime.utcnow().month
        if month in [12, 1, 2]:
            return "Summer"
        elif month in [3, 4, 5]:
            return "Autumn"
        elif month in [6, 7, 8]:
            return "Winter"
        else:
            return "Spring"

    def _build_prompt(
        self,
        location: str,
        season: str,
        query: str,
        sensor_data: Optional[Dict[str, Any]],
    ) -> str:
        """Build the LLM prompt with context."""
        prompt = f"""You are an agricultural expert advising smallholder farmers in Zimbabwe.

Location: {location}
Current Season: {season}
Farmer Query: {query}

"""

        if sensor_data:
            prompt += "Current Environmental Conditions:\n"
            if sensor_data.get("temp_c"):
                prompt += f"- Temperature: {sensor_data['temp_c']:.1f}°C\n"
            if sensor_data.get("humidity"):
                prompt += f"- Humidity: {sensor_data['humidity']:.1f}%\n"
            if sensor_data.get("soil_pct"):
                prompt += f"- Soil Moisture: {sensor_data['soil_pct']:.1f}%\n"
            prompt += "\n"

        prompt += """Based on the location, season, current conditions, and the farmer's query:

1. Recommend 3-5 crop varieties suitable for these conditions
2. For each crop, provide:
   - Expected yield range
   - Best planting window
   - Water requirements
   - Common pests/diseases to watch for
3. Suggest any immediate actions the farmer should take

Keep recommendations practical and based on Zimbabwe's climate and smallholder farming context.
Format your response as a JSON object with 'recommendations' (array), 'reasoning' (string), and 'next_steps' (array)."""

        return prompt

    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API."""
        import json

        response = self.client.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an agricultural expert for Zimbabwean smallholder farmers.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        content = response.choices[0].message.content.strip()

        # Try to extract JSON from response
        try:
            # Look for JSON block in response
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content

            result = json.loads(json_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw content
            result = {"recommendations": [content], "reasoning": "Raw LLM output"}

        return result

    def _call_google(self, prompt: str) -> Dict[str, Any]:
        """Call Google Gemini API."""
        import json

        response = self.client.generate_content(prompt)
        content = response.text.strip()

        # Try to extract JSON from response
        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content

            result = json.loads(json_str)
        except json.JSONDecodeError:
            result = {"recommendations": [content], "reasoning": "Raw LLM output"}

        return result
