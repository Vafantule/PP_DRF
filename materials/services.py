import json
import os
from typing import Optional, Dict, Any

import requests
from requests import Response, Timeout, RequestException

STRIPE_API_BASE: str = "https://api.stripe.com/v1"
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
MISSING_STRIPE_KEY_ERROR: str = "STRIPE_API_KEY не задано"

REQUEST_TIMEOUT = (5, 30)
HEADERS: Dict[str, str] = {"Authorization": f"Bearer {STRIPE_API_KEY}"}


def ensure_stripe_key() -> None:
    """
    Функция выброса ValueError, если ключ не задан.
    """
    if not STRIPE_API_KEY:
        raise ValueError(MISSING_STRIPE_KEY_ERROR)


def _raise_for_status(response: Response) -> None:
    """
    Функция вывода исключения при некорректном HTTP-статусе.
    """
    try:
        response.raise_for_status()
    except requests.HTTPError as exception:
        try:
            body: Any = response.json()
        except json.JSONDecodeError:
            body = response.text
        raise requests.HTTPError(f"{exception}; response_body={body}") from exception


def _post(url: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Функция выполнения POST-запроса.
    """
    try:
        response = requests.post(url, data=data, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    except Timeout as exception:
        raise Timeout(f"Timeout при запросе к {url}: {exception}") from exception
    except RequestException as exception:
        raise RequestException(f"Ошибка запроса к {url}: {exception}") from exception
    _raise_for_status(response)
    return response.json()


def _get(url: str) -> Dict[str, Any]:
    """
    Функция выполнения GET-запроса.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    except Timeout as exception:
        raise Timeout(f"Timeout при запросе к {url}: {exception}") from exception
    except RequestException as exception:
        raise RequestException(f"Ошибка запроса к {url}: {exception}") from exception
    _raise_for_status(response)
    return response.json()


def create_product(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Функция создания продукта в Stripe.
    """
    ensure_stripe_key()

    url = f"{STRIPE_API_BASE}/products"
    data: Dict[str, Any] = {"name": name}
    if description:
        data["description"] = description

    return _post(url, data)


def create_price(product_id: str, unit_amount: int, currency: str = "rub",
                 billing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Функция создания цены продукта.
    """
    ensure_stripe_key()

    url = f"{STRIPE_API_BASE}/prices"
    data: Dict[str, Any] = {
        "product": product_id,
        "unit_amount": str(unit_amount),
        "currency": currency
    }
    if billing:
        for key, value in billing.items():
            data[f"billing[{key}]"] = value

    return _post(url, data)


def create_checkout_session(price_id: str, success_url: str, cancel_url: str,
                            metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Функция создания сессии для получения ссылки на оплату.
    """
    ensure_stripe_key()

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
            data[f"metadata[{key}]"] = value

    return _post(url, data)


def retrieve_session(session_id: str) -> Dict[str, Any]:
    """
    Функция получения информации о сессии по id.
    """
    ensure_stripe_key()

    url = f"{STRIPE_API_BASE}/checkout/sessions/{session_id}"
    return _get(url)
