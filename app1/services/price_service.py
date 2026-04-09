from django.core.cache import cache
from decimal import Decimal
from ..utils.prices import get_live_price

CACHE_TTL = 30  # ✅ 30 seconds (important)


def get_stock_price(symbol):
    symbol = symbol.strip().upper()
    cache_key = f"stock_live_{symbol}"

    # ✅ 1. Return cached instantly
    cached = cache.get(cache_key)
    if cached:
        return cached

    # ✅ 2. Try API
    try:
        price = get_live_price(symbol)

        if price:
            data = {
                "price": Decimal(str(price)),
                "symbol": symbol
            }

            cache.set(cache_key, data, timeout=CACHE_TTL)
            return data

    except Exception as e:
        print("API ERROR:", e)

    # ✅ 3. Fallback (VERY IMPORTANT)
    if cached:
        return cached

    return None