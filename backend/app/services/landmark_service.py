from app.infrastructure.cache import TTLCache
from app.infrastructure.overpass_client import OverpassClient
from app.models.address import ParsedAddress
from app.services.pincode_service import PincodeResult
from app.utils.normalization import normalize_component
from rapidfuzz import fuzz

cache = TTLCache()


class LandmarkResult:
    def __init__(self):
        self.candidates = []
        self.matched = None
        self.evidence = []
        self.used_pincode = None


class LandmarkService:
    def __init__(self):
        self.client = OverpassClient()

    def find_landmarks(
        self, parsed: ParsedAddress, pincode_result: PincodeResult
    ) -> LandmarkResult:
        result = LandmarkResult()
        if not parsed.landmark:
            return result
        base_key = self._cache_key(parsed, pincode_result)
        cached = cache.get(base_key)
        if cached is not None:
            result.candidates = cached
            return result
        bbox = (
            self._bounding_box(pincode_result.centroid)
            if pincode_result.centroid
            else None
        )
        if not bbox:
            return result
        query = self._build_query(parsed.landmark, bbox)
        try:
            osm = self.client.query(query)
            candidates = self._extract_candidates(osm, parsed)
            cache.set(base_key, candidates)
            result.candidates = candidates
            return result
        except Exception:
            result.candidates = []
            return result

    def _cache_key(self, parsed: ParsedAddress, pincode_result: PincodeResult) -> str:
        parts = [
            normalize_component(parsed.city or ""),
            normalize_component(parsed.landmark or ""),
            str(pincode_result.matched_pincode or ""),
        ]
        return "|".join(parts)

    def _bounding_box(
        self, centroid: dict | None
    ) -> tuple[float, float, float, float] | None:
        if not centroid:
            return None
        lat = centroid["lat"]
        lon = centroid["lon"]
        delta = 0.05
        return (lat - delta, lon - delta, lat + delta, lon + delta)

    def _build_query(
        self, landmark: str, bbox: tuple[float, float, float, float]
    ) -> str:
        south, west, north, east = bbox
        name = normalize_component(landmark)
        return (
            f"[out:json][timeout:25];"
            f'(node({south},{west},{north},{east})[name~"{name}",i];'
            f'way({south},{west},{north},{east})[name~"{name}",i];'
            f'relation({south},{west},{north},{east})[name~"{name}",i];)'
            f"out center;"
        )

    def _extract_candidates(self, osm: dict, parsed: ParsedAddress) -> list[dict]:
        nodes = osm.get("elements", [])
        candidates = []
        for item in nodes:
            name = item.get("tags", {}).get("name")
            lat = item.get("lat")
            lon = item.get("lon")
            if not lat or not lon:
                center = item.get("center")
                if center:
                    lat = center.get("lat")
                    lon = center.get("lon")
            if lat and lon and name:
                score = fuzz.partial_ratio(
                    normalize_component(parsed.landmark), normalize_component(name)
                )
                candidates.append(
                    {
                        "name": name,
                        "lat": float(lat),
                        "lon": float(lon),
                        "score": score,
                        "relation": parsed.landmark_relation,
                    }
                )
        return sorted(candidates, key=lambda x: x["score"], reverse=True)
