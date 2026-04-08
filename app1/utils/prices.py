import finnhub
from django.conf import settings
from decimal import Decimal
from django.core.cache import cache

finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)

CACHE_TTL = 30  # seconds


def get_live_price(symbol):
    symbol = symbol.strip().upper()
    cache_key = f"stock_live_{symbol}"

    # ✅ 1. Check cache
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        data = finnhub_client.quote(symbol)
        price = data.get("c")

        if price:
            price_decimal = Decimal(str(price))

            # ✅ store in cache
            cache.set(cache_key, price_decimal, CACHE_TTL)

            return price_decimal

        return None

    except Exception:
        return None


def get_live_prices(symbols):
    result = {}
    symbols = [s.strip().upper() for s in symbols]

    for sym in symbols:
        result[sym] = get_live_price(sym)

    return result