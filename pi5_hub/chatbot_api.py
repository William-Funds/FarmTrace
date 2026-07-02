"""
FarmTrace — Chatbot API Server
Lightweight Flask API for farmer chatbot recommendations.
Runs independently on a configurable port (default: 5001).

Usage:
    from pi5_hub.chatbot_api import ChatbotAPI
    api = ChatbotAPI(config, sensors, location_lookup)
    api.start()  # Runs in background thread
"""
import logging
import json
import threading
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)


class ChatbotAPI:
    def __init__(self, config: dict, sensors=None, location_lookup=None):
        """
        Initialize the chatbot API.

        Args:
            config: Hub configuration dict
            sensors: SensorManager instance for getting current readings
            location_lookup: location_lookup module for geocoding
        """
        self.cfg = config
        self.sensors = sensors
        self.location_lookup = location_lookup
        self.port = config.get("chatbot", {}).get("api_port", 5001)
        self.host = config.get("chatbot", {}).get("api_host", "0.0.0.0")
        self.enabled = config.get("chatbot", {}).get("enabled", True)

        # Import recommendation engine
        from .recommendation_engine import RecommendationEngine

        self.engine = RecommendationEngine(config)
        self.app = None
        self.thread = None

        if self.enabled:
            self._setup_routes()

    def _setup_routes(self):
        """Set up Flask routes."""
        try:
            from flask import Flask, request, jsonify

            self.app = Flask("FarmTraceBot")

            @self.app.route("/health", methods=["GET"])
            def health():
                """Health check endpoint."""
                return jsonify({"status": "ok", "service": "chatbot-api"}), 200

            @self.app.route("/recommendations", methods=["POST"])
            def get_recommendations():
                """
                Get crop recommendations.

                Request JSON:
                {
                    "location": "Harare District",
                    "query": "What should I plant?",
                    "include_sensor_data": true  (optional, default: true)
                }

                Response JSON:
                {
                    "success": true,
                    "recommendations": [...],
                    "reasoning": "...",
                    "sensor_data": {...},
                    "timestamp": "..."
                }
                """
                try:
                    data = request.get_json() or {}
                    location = data.get("location", "Unknown")
                    query = data.get("query", "What crops should I plant?")
                    include_sensor = data.get("include_sensor_data", True)

                    # Get current sensor data
                    sensor_data = None
                    if include_sensor and self.sensors:
                        latest = self.sensors.latest
                        sensor_data = {
                            "temp_c": latest.get("temp_c"),
                            "humidity": latest.get("humidity"),
                            "soil_pct": latest.get("soil_pct"),
                            "lat": latest.get("lat"),
                            "lon": latest.get("lon"),
                            "ts": latest.get("ts"),
                        }

                    # Get recommendations
                    result = self.engine.get_recommendations(location, query, sensor_data)
                    return jsonify(result), 200

                except Exception as e:
                    log.error(f"Error in /recommendations: {e}")
                    return jsonify({"success": False, "error": str(e)}), 500

            @self.app.route("/query", methods=["POST"])
            def handle_query():
                """
                Handle a free-form farmer query with optional coordinates.

                Request JSON:
                {
                    "query": "My tomatoes have spots, what should I do?",
                    "lat": -17.8292,
                    "lon": 31.0522
                }

                Response JSON: Same as /recommendations
                """
                try:
                    data = request.get_json() or {}
                    query = data.get("query", "")
                    lat = data.get("lat")
                    lon = data.get("lon")

                    if not query:
                        return (
                            jsonify({"success": False, "error": "Query required"}),
                            400,
                        )

                    # Try to lookup location from coordinates
                    location = "Zimbabwe"
                    if lat and lon and self.location_lookup:
                        try:
                            # Reverse geocode if possible
                            from .location_lookup import lookup

                            lookup_result = lookup(f"{lat},{lon}")
                            if lookup_result:
                                location = lookup_result.get(
                                    "display_name", lookup_result.get("short_name", location)
                                )
                        except:
                            pass

                    # Get recommendations
                    sensor_data = None
                    if self.sensors:
                        latest = self.sensors.latest
                        sensor_data = {
                            "temp_c": latest.get("temp_c"),
                            "humidity": latest.get("humidity"),
                            "soil_pct": latest.get("soil_pct"),
                        }

                    result = self.engine.get_recommendations(location, query, sensor_data)
                    return jsonify(result), 200

                except Exception as e:
                    log.error(f"Error in /query: {e}")
                    return jsonify({"success": False, "error": str(e)}), 500

            @self.app.route("/status", methods=["GET"])
            def status():
                """Get chatbot service status."""
                return jsonify(
                    {
                        "status": "running",
                        "engine_enabled": self.engine.enabled,
                        "llm_provider": self.engine.provider,
                        "llm_model": self.engine.model,
                        "sensors_connected": self.sensors is not None,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ), 200

            log.info("Chatbot API routes set up")

        except ImportError:
            log.error("Flask not installed. Install with: pip install flask")
            self.enabled = False

    def start(self):
        """Start the API server in a background thread."""
        if not self.enabled:
            log.warning("Chatbot API not enabled")
            return

        if not self.app:
            log.warning("Chatbot API not properly initialized")
            return

        def _run():
            try:
                log.info(f"Starting Chatbot API on {self.host}:{self.port}")
                self.app.run(
                    host=self.host,
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True,
                )
            except Exception as e:
                log.error(f"Chatbot API error: {e}")

        self.thread = threading.Thread(target=_run, daemon=True, name="ChatbotAPI")
        self.thread.start()

    def stop(self):
        """Stop the API server."""
        if self.thread and self.thread.is_alive():
            log.info("Stopping Chatbot API")
            # Flask doesn't have a clean shutdown in threaded mode
            # The daemon thread will stop when the main process exits
