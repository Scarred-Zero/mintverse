import requests
from decimal import Decimal

USD_FEE = 400  # ✅ Admin-defined minting fee in USD
API_URL = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD"


def get_eth_price():
    """✅ Fetch latest ETH price in USD"""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return Decimal(response.json()["USD"])  # ✅ Convert to Decimal for accuracy
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ETH price: {e}")
        return None  # ✅ Handle API failures gracefully


def calculate_minting_fee():
    """✅ Converts USD minting fee to ETH dynamically"""
    eth_price = get_eth_price()
    if eth_price is None:
        return None  # Avoid errors if API call fails

    return round(Decimal(USD_FEE) / eth_price, 4)  # ✅ Keep precision



# print(f"Minting Fee in ETH: {calculate_minting_fee()} ETH")
