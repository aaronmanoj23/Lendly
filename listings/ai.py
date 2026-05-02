"""
AI price suggestion pipeline.

Flow:
  1. Call Google Vision label detection on an uploaded image.
  2. Use the top labels as a search query against the eBay Finding API.
  3. Average recent sold prices and divide by ~30 to get a per-day rental rate.

Gracefully falls back to None if any step fails or creds are missing.
"""
from decimal import Decimal
from statistics import mean
from typing import List, Optional

import requests
from django.conf import settings


def detect_labels(image_bytes: bytes, max_results: int = 5) -> List[str]:
    try:
        from google.cloud import vision
    except ImportError:
        return []
    if not settings.GOOGLE_APPLICATION_CREDENTIALS:
        return []
    try:
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)
        response = client.label_detection(image=image, max_results=max_results)
        return [label.description for label in response.label_annotations]
    except Exception:
        return []


def ebay_average_price(query: str) -> Optional[Decimal]:
    if not settings.EBAY_APP_ID or not query:
        return None
    url = "https://svcs.ebay.com/services/search/FindingService/v1"
    params = {
        "OPERATION-NAME": "findItemsByKeywords",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": settings.EBAY_APP_ID,
        "RESPONSE-DATA-FORMAT": "JSON",
        "keywords": query,
        "paginationInput.entriesPerPage": "10",
    }
    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        items = (
            data.get("findItemsByKeywordsResponse", [{}])[0]
            .get("searchResult", [{}])[0]
            .get("item", [])
        )
        prices = []
        for item in items:
            price_info = item.get("sellingStatus", [{}])[0].get("currentPrice", [{}])[0]
            val = price_info.get("__value__")
            if val:
                prices.append(float(val))
        if not prices:
            return None
        return Decimal(str(round(mean(prices), 2)))
    except Exception:
        return None


def suggest_daily_price(image_bytes: bytes) -> Optional[Decimal]:
    labels = detect_labels(image_bytes)
    if not labels:
        return None
    query = " ".join(labels[:3])
    avg_item_price = ebay_average_price(query)
    if avg_item_price is None:
        return None
    # Rent at roughly 1/30th the item's resale value per day.
    daily = (avg_item_price / Decimal("30")).quantize(Decimal("0.01"))
    return max(daily, Decimal("1.00"))
