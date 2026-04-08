from django.core.cache import cache
from decimal import Decimal
from ..utils.prices import get_live_price

CACHE_TTL = 5

def get_stock_price(symbol):
    symbol = symbol.strip().upper()
    cache_key = f"stock_live_{symbol}"

    cached = cache.get(cache_key)
    if cached:
        return cached

    price = get_live_price(symbol)

    if price:
        data = {
            "price": price,
            "symbol": symbol
        }
        cache.set(cache_key, data, timeout=5)
        return data

    return None