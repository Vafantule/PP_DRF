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
