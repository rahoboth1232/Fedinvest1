# utils/prices.py
import finnhub
from django.conf import settings
from decimal import Decimal

finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)

def get_live_price(symbol):
    try:
        data = finnhub_client.quote(symbol)
        price = data.get("c")  # c = current price
        if price:
            return Decimal(str(price))
        return None
    except:
        return None


def get_live_prices(symbols):
    """
    Returns dict: { "AAPL": Decimal('178.23'), ... }
    Fewer API calls than calling individually.
    """
    prices = {}
    for sym in symbols:
        prices[sym] = get_live_price(sym)
    return prices