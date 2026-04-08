from django.core.cache import cache
from decimal import Decimal
from ..utils.prices import get_live_price

CACHE_TTL = 5


def get_stock_price(symbol):
    symbol = symbol.strip().upper()
    cache_key = f"stock_live_{symbol}"

    # ✅ 1. Try cache
    cached = cache.get(cache_key)
    if cached:
        return {
            "price": cached,
            "symbol": symbol
        }

    # ✅ 2. Fetch from API
    price = get_live_price(symbol)

    if price:
        cache.set(cache_key, price, CACHE_TTL)

        return {
            "price": price,
            "symbol": symbol
        }

    return None