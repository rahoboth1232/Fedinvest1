from django.core.cache import cache
from decimal import Decimal
from ..utils.prices import get_live_price

CACHE_TTL = 30  # ✅ 30 seconds (important)

def get_stock_price(symbol):
    symbol = symbol.strip().upper()
    cache_key = f"stock_live_{symbol}"

    cached = cache.get(cache_key)

    # ✅ FIX: normalize cached data
    if cached:
        if isinstance(cached, dict):
            price = cached.get("price")

            # 🔥 FIX nested dict
            if isinstance(price, dict):
                price = price.get("price")

            return {
                "symbol": symbol,
                "price": price
            }

    try:
        price = get_live_price(symbol)

        if price:
            clean_price = float(price)

            data = {
                "symbol": symbol,
                "price": clean_price
            }

            cache.set(cache_key, data, timeout=60)
            return data

    except Exception as e:
        print("SERVICE ERROR:", e)

    return cached if cached else None