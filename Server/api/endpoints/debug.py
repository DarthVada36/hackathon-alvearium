import os
import time
from typing import Any, Dict

import requests
from fastapi import APIRouter, Query


router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/ping")
def ping():
    return {"service": "debug", "ok": True, "ts": int(time.time())}


@router.get("/redis")
def debug_redis():
    url = os.getenv("REDIS_URL")
    try:
        import redis  # type: ignore

        if not url:
            return {"available": False, "reason": "REDIS_URL not set"}
        client = redis.StrictRedis.from_url(url, socket_connect_timeout=0.25, socket_timeout=0.25)
        ok = bool(client.ping())
        return {"available": ok, "url": url}
    except Exception as e:
        return {"available": False, "error": str(e), "url": url}


@router.get("/pinecone")
def debug_pinecone():
    try:
        from Server.core.services.pinecone_service import pinecone_service

        return pinecone_service.get_status()
    except Exception as e:  # pragma: no cover
        return {"available": False, "error": str(e)}


@router.get("/wiki")
def debug_wikipedia(title: str = Query(..., description="Page title, e.g., 'Plaza Mayor'")):
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
        r = requests.get(url, timeout=8)
        return {
            "status_code": r.status_code,
            "title": r.json().get("title") if r.headers.get("content-type","{}").startswith("application/json") else None,
            "extract_len": len(r.json().get("extract","")) if r.status_code == 200 else 0,
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/geocode")
def debug_geocode(place: str = Query(..., description="Place name, e.g., 'Plaza Mayor'")):
    try:
        params = {"q": f"{place}, Madrid, Spain", "format": "json", "limit": 1}
        headers = {"User-Agent": "ratoncito/1.0"}
        r = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers, timeout=8)
        data = r.json() if r.headers.get("content-type","{}").startswith("application/json") else []
        first = data[0] if data else {}
        return {
            "status_code": r.status_code,
            "lat": first.get("lat"),
            "lon": first.get("lon"),
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/events")
def debug_eventbrite(location: str = "Madrid"):
    token = os.getenv("EVENTBRITE_TOKEN")
    if not token:
        return {"available": False, "reason": "EVENTBRITE_TOKEN not set"}
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = {"location.address": location, "sort_by": "date", "page": 1}
        r = requests.get("https://www.eventbriteapi.com/v3/events/search/", headers=headers, params=params, timeout=10)
        data = r.json() if r.headers.get("content-type","{}").startswith("application/json") else {}
        return {"status_code": r.status_code, "events": len(data.get("events", []))}
    except Exception as e:
        return {"error": str(e)}


@router.get("/transport")
def debug_transport(lat: float, lon: float):
    # EMT API likely requires auth; this just reports the status code to validate connectivity
    try:
        url = "https://openapi.emtmadrid.es/v1/transport/busemtmad/stops"
        r = requests.get(url, params={"lat": lat, "lon": lon}, timeout=8)
        return {"status_code": r.status_code}
    except Exception as e:
        return {"error": str(e)}


@router.get("/google-places")
def debug_google_places(place: str = "Plaza Mayor", radius: int = 500):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"available": False, "reason": "GOOGLE_API_KEY not set"}
    try:
        import googlemaps  # type: ignore

        gmaps = googlemaps.Client(key=api_key)
        # Get coords via Nominatim
        headers = {"User-Agent": "ratoncito/1.0"}
        params = {"q": f"{place}, Madrid, Spain", "format": "json", "limit": 1}
        geo = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers, timeout=8).json()
        if not geo:
            return {"error": "failed to geocode"}
        lat, lon = float(geo[0].get("lat", 0)), float(geo[0].get("lon", 0))
        res: Dict[str, Any] = gmaps.places_nearby(location=(lat, lon), radius=radius, type="restaurant")
        return {"results": len(res.get("results", []))}
    except Exception as e:
        return {"available": False, "error": str(e)}
