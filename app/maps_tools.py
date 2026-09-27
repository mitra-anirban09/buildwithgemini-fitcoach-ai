"""Geocoding and Places (New) tools for FitCoach AI using Google Maps REST APIs."""

import json
import os
import urllib.parse
import urllib.request


def _get_api_key() -> str:
    """Retrieve the Google Maps API Key from environment variables or .env."""
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("GOOGLE_MAPS_API_KEY="):
                        key = line.split("=", 1)[1].strip()
                        break
    if not key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set.")
    return key


def geocode_address(address: str) -> str:
    """Convert a location address into latitude and longitude coordinates using the Geocoding API.

    Args:
        address: The address or city name to geocode (e.g., '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Seattle, WA').

    Returns:
        Formatted summary with formatted address, latitude, longitude, and place_id.
    """
    try:
        api_key = _get_api_key()
        encoded_address = urllib.parse.quote(address)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("status") != "OK" or not data.get("results"):
            return f"Geocoding failed for address '{address}'. Status: {data.get('status')}"

        result = data["results"][0]
        formatted_address = result.get("formatted_address", address)
        location = result.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")
        place_id = result.get("place_id", "")

        return (
            f"Geocoded Address:\n"
            f"- Address: {formatted_address}\n"
            f"- Coordinates: Latitude {lat}, Longitude {lng}\n"
            f"- Place ID: {place_id}"
        )

    except Exception as e:
        return f"Error during geocoding: {e}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "gym",
    radius_meters: int = 5000,
) -> str:
    """Find nearby places (e.g., gyms, fitness centers, parks) around coordinates using Places API (New).

    Args:
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        place_type: Type of place to search for (e.g., 'gym', 'fitness_center', 'park', 'sports_complex').
        radius_meters: Search radius in meters (default 5000m).

    Returns:
        List of matching nearby places with name, formatted address, and coordinates.
    """
    try:
        api_key = _get_api_key()
        url = "https://places.googleapis.com/v1/places:searchNearby"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
        }

        payload = {
            "includedTypes": [place_type.lower().strip()],
            "maxResultCount": 10,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": float(radius_meters),
                }
            },
        }

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        places = data.get("places", [])
        if not places:
            return f"No nearby places of type '{place_type}' found within {radius_meters}m of ({latitude}, {longitude})."

        results = []
        for p in places:
            display_name = p.get("displayName", {}).get("text", "Unknown Name")
            formatted_addr = p.get("formattedAddress", "No address provided")
            loc = p.get("location", {})
            p_lat = loc.get("latitude")
            p_lng = loc.get("longitude")

            results.append(
                f"• {display_name}\n"
                f"  Address: {formatted_addr}\n"
                f"  Location: Lat {p_lat}, Lng {p_lng}"
            )

        return f"Nearby '{place_type}' locations ({len(results)} found):\n\n" + "\n\n".join(results)

    except Exception as e:
        return f"Error searching nearby places: {e}"
