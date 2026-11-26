"""
MetaMask On-Ramp Provider Quote Scraper
Author: Senior/Staff Growth Data Scientist Candidate
Case Study: Monetization & Pricing Strategy
"""

import time
import json
import logging
from typing import List, Dict, Any, Optional
import requests
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Base API Configuration
BASE_ORDERS_URL = "https://on-ramp.api.cx.metamask.io"
BASE_CACHE_URL = "https://on-ramp-cache.api.cx.metamask.io"

REQUEST_HEADERS = {
    "Origin": "https://portfolio.metamask.io",
    "Referer": "https://portfolio.metamask.io/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}

# Supported Countries & Fiat Mapping
COUNTRIES = {
    "US": {
        "regionId": "/regions/us-tx",
        "fiatCurrencyId": "/currencies/fiat/usd",
        "fiatSymbol": "USD",
        "countryName": "United States",
    },
    "UK": {
        "regionId": "/regions/gb",
        "fiatCurrencyId": "/currencies/fiat/gbp",
        "fiatSymbol": "GBP",
        "countryName": "United Kingdom",
    },
    "DE": {
        "regionId": "/regions/de",
        "fiatCurrencyId": "/currencies/fiat/eur",
        "fiatSymbol": "EUR",
        "countryName": "Germany",
    },
}

# Target Cryptocurrencies
CRYPTOCURRENCIES = {
    "ETH_MAINNET": {
        "name": "Ethereum Mainnet",
        "symbol": "ETH",
        "chain": "Ethereum",
        "chainId": "1",
        "cryptoCurrencyId": "/currencies/crypto/1/0x0000000000000000000000000000000000000000",
        "coingecko_id": "ethereum",
    },
    "USDT_ETHEREUM": {
        "name": "USDT (Ethereum)",
        "symbol": "USDT",
        "chain": "Ethereum",
        "chainId": "1",
        "cryptoCurrencyId": "/currencies/crypto/1/0xdac17f958d2ee523a2206206994597c13d831ec7",
        "coingecko_id": "tether",
    },
    "USDT_BNB": {
        "name": "USDT (BNB Chain)",
        "symbol": "USDT",
        "chain": "BNB Chain",
        "chainId": "56",
        "cryptoCurrencyId": "/currencies/crypto/56/0x55d398326f99059ff775485246999027b3197955",
        "coingecko_id": "tether",
    },
}

# Price Bins ($30 to $30,000)
PRICE_BINS = [
    {"bin_label": "[30, 100)", "min": 30, "max": 100, "midpoint": 65},
    {"bin_label": "[100, 250)", "min": 100, "max": 250, "midpoint": 175},
    {"bin_label": "[250, 500)", "min": 250, "max": 500, "midpoint": 375},
    {"bin_label": "[500, 1,000)", "min": 500, "max": 1000, "midpoint": 750},
    {"bin_label": "[1,000, 2,500)", "min": 1000, "max": 2500, "midpoint": 1750},
    {"bin_label": "[2,500, 5,000)", "min": 2500, "max": 5000, "midpoint": 3750},
    {"bin_label": "[5,000, 10,000)", "min": 5000, "max": 10000, "midpoint": 7500},
    {"bin_label": "[10,000, 30,000]", "min": 10000, "max": 30000, "midpoint": 20000},
]

# Active Aggregated Providers
PROVIDERS = [
    "moonpay",
    "transak",
    "sardine",
    "banxa",
    "mercuryo",
    "ramp-network",
    "stripe",
    "robinhood",
    "topper",
    "swapped",
    "coinbase",
]

DEFAULT_WALLET_ADDRESS = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
DEFAULT_REDIRECT_URL = "https://portfolio.metamask.io/buy/build-quote"


def fetch_spot_prices() -> Dict[str, Dict[str, float]]:
    """
    Fetch live reference spot prices from CoinGecko or fallback.
    Returns: { 'ethereum': {'usd': ..., 'gbp': ..., 'eur': ...}, 'tether': {...} }
    """
    logger.info("Fetching reference spot prices from CoinGecko...")
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "ethereum,tether", "vs_currencies": "usd,gbp,eur"}
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            prices = resp.json()
            logger.info("CoinGecko spot prices fetched: %s", prices)
            return prices
    except Exception as e:
        logger.warning("CoinGecko fetch failed: %s. Using Binance fallback.", e)

    # Fallback to Binance
    try:
        eth_usd = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT", timeout=5).json()["price"])
        rates = {
            "ethereum": {"usd": eth_usd, "gbp": eth_usd * 0.79, "eur": eth_usd * 0.95},
            "tether": {"usd": 1.0, "gbp": 0.79, "eur": 0.95},
        }
        logger.info("Binance fallback spot prices: %s", rates)
        return rates
    except Exception as e2:
        logger.error("All spot price fetches failed: %s. Using static defaults.", e2)
        return {
            "ethereum": {"usd": 1730.0, "gbp": 1360.0, "eur": 1640.0},
            "tether": {"usd": 1.0, "gbp": 0.79, "eur": 0.95},
        }


def get_available_payment_methods(country_code: str, fiat_id: str) -> List[Dict[str, str]]:
    """
    Fetch supported payment methods for a given country and fiat from MetaMask cache.
    """
    region_id = COUNTRIES[country_code]["regionId"].replace("/regions/", "")
    url = f"{BASE_CACHE_URL}/regions/{region_id}/light"
    params = {
        "sdk": "2.1.13",
        "context": "browser",
        "action": "buy",
        "fiat": fiat_id,
        "multiplePayments": "true",
    }
    try:
        resp = requests.get(url, headers=REQUEST_HEADERS, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            payments = []
            for p in data.get("payments", []):
                payments.append({"id": p["id"], "name": p.get("name", p["id"])})
            logger.info("Found %d payment methods for %s", len(payments), country_code)
            return payments
    except Exception as e:
        logger.warning("Failed to fetch payments for %s: %s", country_code, e)

    # Fallback payment methods
    return [
        {"id": "/payments/debit-credit-card", "name": "Debit or Credit"},
        {"id": "/payments/paypal", "name": "PayPal"},
    ]


def fetch_provider_quote(
    provider: str,
    region_id: str,
    payment_method_id: str,
    crypto_currency_id: str,
    fiat_currency_id: str,
    amount: float,
    wallet_address: str = DEFAULT_WALLET_ADDRESS,
) -> Optional[Dict[str, Any]]:
    """
    Request a single quote from a specific provider via MetaMask Aggregator API.
    """
    url = f"{BASE_ORDERS_URL}/providers/{provider}/quote"
    params = {
        "regionId": region_id,
        "paymentMethodId": payment_method_id,
        "cryptoCurrencyId": crypto_currency_id,
        "fiatCurrencyId": fiat_currency_id,
        "amount": str(amount),
        "walletAddress": wallet_address,
        "redirectUrl": DEFAULT_REDIRECT_URL,
    }

    try:
        resp = requests.get(url, headers=REQUEST_HEADERS, params=params, timeout=12)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code in (400, 422, 500):
            # Unsupported parameter combination or amount out of bounds
            return None
    except requests.RequestException:
        return None
    return None


def calculate_fees_and_spread(
    amount_in: float,
    amount_out: float,
    provider_fee: float,
    network_fee: float,
    extra_fee: float,
    quoted_exchange_rate: float,
    spot_price: float,
) -> Dict[str, float]:
    """
    Calculate fee breakdown, residual implicit spread, and effective margins.
    
    Fee components:
    - providerFee: Explicit processor fee
    - networkFee: Blockchain gas/settlement fee
    - extraFee: Partner/Aggregator fee (MetaMask markup if applicable)
    - spread: Implicit fee charged via exchange rate markup
      Formula: spread = amountIn - (amountOut * spot_price) - (providerFee + networkFee + extraFee)
    """
    explicit_fees = (provider_fee or 0.0) + (network_fee or 0.0) + (extra_fee or 0.0)
    
    # Fair value of cryptocurrency delivered at benchmark spot price
    fair_crypto_value = amount_out * spot_price
    
    # Total effective fee paid by the user (everything they didn't receive in fair crypto)
    total_effective_fee = amount_in - fair_crypto_value
    
    # Implicit spread is the remainder beyond explicit fees
    implicit_spread = max(0.0, total_effective_fee - explicit_fees)
    
    # Total fee = explicit fees + implicit spread
    total_fee = explicit_fees + implicit_spread
    effective_fee_pct = (total_fee / amount_in * 100.0) if amount_in > 0 else 0.0
    spread_pct = ((quoted_exchange_rate - spot_price) / spot_price * 100.0) if spot_price > 0 else 0.0

    return {
        "fair_crypto_value": round(fair_crypto_value, 4),
        "total_effective_fee": round(total_effective_fee, 4),
        "implicit_spread": round(implicit_spread, 4),
        "total_fee": round(total_fee, 4),
        "effective_fee_pct": round(effective_fee_pct, 4),
        "spread_pct": round(spread_pct, 4),
    }


def crawl_metamask_quotes(
    target_countries: Optional[List[str]] = None,
    target_cryptos: Optional[List[str]] = None,
    price_bins: Optional[List[Dict[str, Any]]] = None,
    providers_list: Optional[List[str]] = None,
    max_payment_methods: int = 4,
    rate_limit_delay: float = 0.25,
) -> pd.DataFrame:
    """
    Comprehensive crawler iterating across:
    Country x Fiat x Crypto x Price Bin x Payment Method x Provider
    """
    countries = target_countries or list(COUNTRIES.keys())
    cryptos = target_cryptos or list(CRYPTOCURRENCIES.keys())
    bins = price_bins or PRICE_BINS
    providers = providers_list or PROVIDERS

    spot_prices = fetch_spot_prices()
    rows = []
    total_queries = 0
    successful_quotes = 0

    logger.info("Starting crawl across %d countries, %d assets, %d bins, %d providers...",
                len(countries), len(cryptos), len(bins), len(providers))

    for country_code in countries:
        country_cfg = COUNTRIES[country_code]
        fiat_symbol = country_cfg["fiatSymbol"]
        fiat_id = country_cfg["fiatCurrencyId"]
        region_id = country_cfg["regionId"]

        # Fetch payment methods for this country
        payments = get_available_payment_methods(country_code, fiat_id)[:max_payment_methods]

        for crypto_key in cryptos:
            crypto_cfg = CRYPTOCURRENCIES[crypto_key]
            crypto_id = crypto_cfg["cryptoCurrencyId"]
            crypto_symbol = crypto_cfg["symbol"]
            chain_name = crypto_cfg["chain"]
            cg_id = crypto_cfg["coingecko_id"]

            # Current spot price for this crypto in the country's fiat
            spot_price = spot_prices.get(cg_id, {}).get(fiat_symbol.lower(), 1.0)

            for price_bin in bins:
                price_point = price_bin["midpoint"]
                bin_label = price_bin["bin_label"]

                for payment in payments:
                    payment_id = payment["id"]
                    payment_name = payment["name"]

                    for provider in providers:
                        total_queries += 1
                        raw_quote = fetch_provider_quote(
                            provider=provider,
                            region_id=region_id,
                            payment_method_id=payment_id,
                            crypto_currency_id=crypto_id,
                            fiat_currency_id=fiat_id,
                            amount=price_point,
                        )

                        if raw_quote and "quote" in raw_quote:
                            q = raw_quote["quote"]
                            amount_in = float(q.get("amountIn", price_point))
                            amount_out = float(q.get("amountOut", 0.0))
                            provider_fee = float(q.get("providerFee", 0.0) or 0.0)
                            network_fee = float(q.get("networkFee", 0.0) or 0.0)
                            extra_fee = float(q.get("extraFee", 0.0) or 0.0)
                            quoted_rate = float(q.get("exchangeRate", 0.0) or 0.0)

                            provider_name = raw_quote.get("providerInfo", {}).get("name", provider)

                            # Calculate spread & net margin metrics
                            metrics = calculate_fees_and_spread(
                                amount_in=amount_in,
                                amount_out=amount_out,
                                provider_fee=provider_fee,
                                network_fee=network_fee,
                                extra_fee=extra_fee,
                                quoted_exchange_rate=quoted_rate,
                                spot_price=spot_price,
                            )

                            rows.append({
                                "scraped_timestamp": pd.Timestamp.utcnow(),
                                "country_code": country_code,
                                "country_name": country_cfg["countryName"],
                                "fiat_currency": fiat_symbol,
                                "price_point": amount_in,
                                "price_bin": bin_label,
                                "bin_min": price_bin["min"],
                                "bin_max": price_bin["max"],
                                "cryptocurrency_symbol": crypto_symbol,
                                "cryptocurrency_name": crypto_cfg["name"],
                                "blockchain_network": chain_name,
                                "crypto_currency_id": crypto_id,
                                "payment_method_id": payment_id,
                                "payment_method_name": payment_name,
                                "provider_code": provider,
                                "provider_name": provider_name,
                                "quote_fiat_amount": amount_in,
                                "quote_crypto_amount": amount_out,
                                "quoted_exchange_rate": quoted_rate,
                                "reference_spot_price": spot_price,
                                "provider_fee": provider_fee,
                                "network_fee": network_fee,
                                "extra_fee": extra_fee,
                                "implicit_spread": metrics["implicit_spread"],
                                "total_fee": metrics["total_fee"],
                                "effective_fee_pct": metrics["effective_fee_pct"],
                                "spread_pct": metrics["spread_pct"],
                                "fair_crypto_value": metrics["fair_crypto_value"],
                            })
                            successful_quotes += 1

                        # Be polite to the endpoint
                        time.sleep(rate_limit_delay)

    logger.info("Scraping completed! Total Queries: %d | Successful Quotes: %d", total_queries, successful_quotes)
    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    df_result = crawl_metamask_quotes()
    output_path = "/Users/saieshwarreddy/.gemini/antigravity/scratch/moonpay-assignment/data/metamask_quotes.csv"
    df_result.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}. Shape: {df_result.shape}")
