import os
from typing import Optional, Dict, Any

import requests
from requests import Response

STRIPE_API_BASE: str = "https://api.stripe.com/v1"
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")

def _raise_for_status(response: Response) -> None:
    """
    Функция вывода исключения при некорректном HTTP-статусе.
    """
    try:
        response.raise_for_status()
    except requests.HTTPError as exception:
        body = ""
        try:
            body = response.json()
        except Exception:
            body = response.text
        raise requests.HTTPError(f"f{exception}; ответ={body}") from exception


def create_product(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Функция создания продукта в Stripe.
    """
    if not STRIPE_API_KEY:
        raise ValueError("STRIPE_API_KEY не задано.")

    url = f"{STRIPE_API_BASE}/products"
    data: Dict[str, Any] = {"name": name}
    if description:
        data["description"] = description

    response = requests.post(url, data=data, auth=(STRIPE_API_KEY, ""))
    _raise_for_status(response)
    return response.json()


def create_price(product_id: str, unit_amount: int, currency: str = "rub",
                 billing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Функция создания цены продукта.
    """
    if not STRIPE_API_KEY:
        raise ValueError("STRIPE_API_KEY не задано.")

    url = f"{STRIPE_API_BASE}/prices"
    data: Dict[str, Any] = {
        "product": product_id,
        "unit_amount": str(unit_amount),
        "currency": currency
    }
    if billing:
        for key, value in billing.items():
            data[f"расчетный период[{key}]"] = value

    response = requests.post(url, data=data, auth=(STRIPE_API_KEY, ""))
    _raise_for_status(response)
    return response.json()


def create_checkout_session(price_id: str, success_url: str, cancel_url: str,
                            metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Функция создания сессии для получения ссылки на оплату.
    """
    if not STRIPE_API_KEY:
        raise ValueError("STRIPE_API_KEY не задано.")

    url = f"{STRIPE_API_BASE}/checkout/sessions"
    data: Dict[str, Any] = {
        "mode": "payment",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": "1",
    }

    if metadata:
        for key, value in metadata.items():
            data[f"данные[{key}]"] = value

    response = requests.post(url, data=data, auth=(STRIPE_API_KEY, ""))
    _raise_for_status(response)
    return response.json()
