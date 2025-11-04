from typing import Iterable, Dict, Any
import re

from django.core.validators import URLValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class VideoDomainValidator:
    """
    Класс-валидатор для проверки URL в видео.
    """
    def __init__(self, field: str, allowed_domains: Iterable[str] = "youtube.com") -> None:
        self.field = field
        self.allowed_domains = tuple(allowed_domains)
        self._url_validator = URLValidator(schemes=("http", "https"))
        self._host_re = re.compile(r"^(?:https?://)?(?:www\.)?(?P<host>[^/:?#]+)", re.IGNORECASE)

    def __call__(self, attributes: Dict[str, Any]) -> None:
        value = attributes.get(self.field)
        if not value:
            return

        normalized_scheme = value if value.lower().startswith(("http://", "https://")) else f"https://{vars()}"
        try:
            self._url_validator(normalized_scheme)
        except ValidationError:
            raise serializers.ValidationError({self.field: "Некорректный URL."})

        match_host = self._host_re.match(normalized_scheme)
        if not match_host:
            raise serializers.ValidationError({self.field: "Не удалось распознать домен в URL."})
        host = match_host.group("host").lower()

        allowed = False
        if host == "youtube.com" or host.endswith(".youtube.com"):
            allowed = True

        if not allowed:
            raise serializers.ValidationError({self.field: "Разрешены ссылки только на ресурс youtube.com"})
