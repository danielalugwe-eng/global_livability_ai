"""Build public image URLs for Streamlit cards without API keys.

For "real" location photos, we first query Wikipedia/Wikimedia metadata and
use the page thumbnail when available. If no match is found, we fall back to
public photo services.
"""
from __future__ import annotations

import json
import hashlib
from functools import lru_cache
import urllib.parse
import urllib.request

LOREMFLICKR_BASE = "https://loremflickr.com/{width}/{height}/{query}"
PICSUM_BASE = "https://picsum.photos/seed/{seed}/{width}/{height}"
WIKI_SEARCH = (
    "https://en.wikipedia.org/w/api.php?action=opensearch"
    "&limit=5&namespace=0&format=json&search={query}"
)
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"


def image_url(query: str) -> str:
    """Return a stable public image URL for the given search query.

    We prefer a keyword-driven photo from loremflickr. If that host fails in
    some regions, app code can switch to `fallback_image_url` without changing
    call sites.
    """
    tokens = [t.strip().lower() for t in query.split(",") if t.strip()]
    tag_str = ",".join(tokens[:6]) if tokens else "travel"
    encoded = urllib.parse.quote(tag_str, safe=",")
    return LOREMFLICKR_BASE.format(width=1200, height=700, query=encoded)


def fallback_image_url(query: str) -> str:
    """Return deterministic fallback image URL.

    Picsum does not support semantic tags, but seeded URLs keep visuals stable
    for the same query between reruns.
    """
    seed = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
    return PICSUM_BASE.format(seed=seed, width=1200, height=700)


def _http_get_json(url: str) -> dict | list | None:
    """Return decoded JSON for URL or None when unavailable."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "sea-livability-ai/1.0 (streamlit-dashboard)"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8", errors="ignore"))
    except Exception:
        return None


@lru_cache(maxsize=512)
def _wikipedia_thumbnail_for_query(query: str) -> str | None:
    """Resolve a Wikipedia page thumbnail for a natural-language query."""
    search_url = WIKI_SEARCH.format(query=urllib.parse.quote_plus(query))
    search_payload = _http_get_json(search_url)
    if not isinstance(search_payload, list) or len(search_payload) < 2:
        return None

    titles = search_payload[1]
    if not titles:
        return None

    for raw_title in titles:
        title = str(raw_title).strip()
        if not title:
            continue

        summary_url = WIKI_SUMMARY.format(title=urllib.parse.quote(title, safe=""))
        summary_payload = _http_get_json(summary_url)
        if not isinstance(summary_payload, dict):
            continue

        thumb = summary_payload.get("thumbnail")
        if isinstance(thumb, dict):
            src = thumb.get("source")
            if isinstance(src, str) and src.startswith("http"):
                return src
    return None


def real_image_url(query: str, fallback_query: str | None = None) -> str:
    """Return a best-effort real-world image URL, with deterministic fallback."""
    thumb = _wikipedia_thumbnail_for_query(query)
    if thumb:
        return thumb
    query_for_fallback = fallback_query if fallback_query else query
    return image_url(query_for_fallback)


def country_hero_url(country_name: str) -> str:
    return real_image_url(
        f"{country_name} tourism",
        fallback_query=f"{country_name},landmark,travel",
    )


def tourist_spot_url(spot_name: str, country_name: str) -> str:
    # Try specific spot match first, then country-qualified query.
    direct = _wikipedia_thumbnail_for_query(spot_name)
    if direct:
        return direct
    return real_image_url(
        f"{spot_name} {country_name}",
        fallback_query=f"{spot_name},{country_name},tourism",
    )


def transport_url(country_name: str, mode: str) -> str:
    return real_image_url(
        f"Transport in {country_name}",
        fallback_query=f"{country_name},{mode},transport",
    )


def cost_of_living_url(country_name: str) -> str:
    return real_image_url(
        f"{country_name} city",
        fallback_query=f"{country_name},city,street,market",
    )
