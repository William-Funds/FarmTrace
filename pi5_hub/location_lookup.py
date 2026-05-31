"""
FarmTrace — Location Lookup
Uses OpenStreetMap Nominatim API (free, no account needed).
Given a place name, returns human-readable location + coordinates.
"""
import urllib.request, urllib.parse, json, logging

log = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def lookup(place_name: str) -> dict:
    """
    Look up a place name and return location details.
    Returns dict with: display_name, short_name, lat, lon
    Returns None if not found or no internet.
    """
    if not place_name or not place_name.strip():
        return None

    params = urllib.parse.urlencode({
        "q":              place_name.strip(),
        "format":         "json",
        "limit":          1,
        "countrycodes":   "zw",   # bias to Zimbabwe first
        "addressdetails": 1,
    })
    url = f"{NOMINATIM_URL}?{params}"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "FarmTrace/1.0 (farmtrace.coop)"
        })
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())

        if not data:
            # Try without country bias
            params2 = urllib.parse.urlencode({
                "q": place_name.strip(), "format": "json",
                "limit": 1, "addressdetails": 1,
            })
            req2 = urllib.request.Request(
                f"{NOMINATIM_URL}?{params2}",
                headers={"User-Agent": "FarmTrace/1.0"}
            )
            with urllib.request.urlopen(req2, timeout=8) as resp2:
                data = json.loads(resp2.read().decode())

        if not data:
            log.warning("No results found for: %s", place_name)
            return None

        result  = data[0]
        address = result.get("address", {})
        lat     = float(result["lat"])
        lon     = float(result["lon"])

        # Build a clean short name for the passport
        parts = []
        for key in ("village", "town", "city", "suburb",
                    "county", "state_district", "state", "country"):
            val = address.get(key)
            if val and val not in parts:
                parts.append(val)
            if len(parts) == 3:
                break

        short_name   = ", ".join(parts) if parts else result.get("display_name","")
        display_name = result.get("display_name", short_name)

        log.info("Location found: %s  (%.5f, %.5f)", short_name, lat, lon)
        return {
            "short_name":   short_name,
            "display_name": display_name,
            "lat":          lat,
            "lon":          lon,
        }

    except Exception as e:
        log.warning("Location lookup failed: %s", e)
        return None
