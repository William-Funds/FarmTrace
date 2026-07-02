"""
FarmTrace Chatbot Client — Example Usage
Demonstrates how to interact with the recommendation chatbot API.

The API runs on http://localhost:5001 by default.
"""
import requests
import json
from typing import Dict, Any


class FarmTraceChatbotClient:
    def __init__(self, api_url: str = "http://localhost:5001"):
        """Initialize the chatbot client."""
        self.api_url = api_url.rstrip("/")

    def health_check(self) -> bool:
        """Check if the API is running."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get the chatbot service status."""
        try:
            response = requests.get(f"{self.api_url}/status", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def get_recommendations(
        self,
        location: str,
        query: str = "What crops should I plant?",
        include_sensor_data: bool = True,
    ) -> Dict[str, Any]:
        """
        Get crop recommendations for a specific location and query.

        Args:
            location: Location name (e.g., "Harare District, Zimbabwe")
            query: Farmer's question or request
            include_sensor_data: Include current sensor readings in analysis

        Returns:
            API response with recommendations
        """
        try:
            payload = {
                "location": location,
                "query": query,
                "include_sensor_data": include_sensor_data,
            }
            response = requests.post(
                f"{self.api_url}/recommendations", json=payload, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    def query_chatbot(
        self, query: str, lat: float = None, lon: float = None
    ) -> Dict[str, Any]:
        """
        Send a free-form query to the chatbot.

        Args:
            query: Farmer's question (e.g., "My tomatoes have spots")
            lat: Optional latitude
            lon: Optional longitude

        Returns:
            API response with recommendations
        """
        try:
            payload = {"query": query}
            if lat is not None:
                payload["lat"] = lat
            if lon is not None:
                payload["lon"] = lon

            response = requests.post(
                f"{self.api_url}/query", json=payload, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    def print_recommendations(self, response: Dict[str, Any]):
        """Pretty print recommendations."""
        if not response.get("success"):
            print(f"❌ Error: {response.get('error')}")
            return

        print(f"\n🌾 Recommendations for {response.get('location')} ({response.get('season')})")
        print("=" * 70)

        # Print sensor data if available
        if response.get("sensor_data"):
            print("\n📊 Current Conditions:")
            sensor_data = response["sensor_data"]
            if sensor_data.get("temp_c"):
                print(f"  • Temperature: {sensor_data['temp_c']:.1f}°C")
            if sensor_data.get("humidity"):
                print(f"  • Humidity: {sensor_data['humidity']:.1f}%")
            if sensor_data.get("soil_pct"):
                print(f"  • Soil Moisture: {sensor_data['soil_pct']:.1f}%")

        # Print reasoning
        if response.get("reasoning"):
            print(f"\n💡 Analysis:")
            print(f"  {response['reasoning']}")

        # Print recommendations
        if response.get("recommendations"):
            print(f"\n🌱 Recommended Crops:")
            recs = response["recommendations"]
            if isinstance(recs, list):
                for i, rec in enumerate(recs, 1):
                    print(f"  {i}. {rec}")
            else:
                print(f"  {recs}")

        print("\n" + "=" * 70)


# Example usage
if __name__ == "__main__":
    client = FarmTraceChatbotClient()

    # Check if API is running
    if not client.health_check():
        print("❌ Chatbot API is not running. Start it with: python -m pi5_hub.main")
        exit(1)

    print("✅ Chatbot API is running!\n")

    # Get status
    status = client.get_status()
    print("📡 Service Status:")
    print(json.dumps(status, indent=2))

    # Example 1: Get recommendations for a location
    print("\n\n--- Example 1: Location-based Recommendations ---")
    response = client.get_recommendations(
        location="Harare District, Zimbabwe",
        query="I have 2 hectares. What should I plant this season?",
    )
    client.print_recommendations(response)

    # Example 2: Free-form query
    print("\n\n--- Example 2: Problem-specific Query ---")
    response = client.query_chatbot(
        query="My maize plants have yellow leaves and look sick. What could be wrong?",
        lat=-17.8292,
        lon=31.0522,
    )
    client.print_recommendations(response)

    # Example 3: Another location
    print("\n\n--- Example 3: Different Location ---")
    response = client.get_recommendations(
        location="Bulawayo, Zimbabwe",
        query="What vegetables grow well here?",
    )
    client.print_recommendations(response)
