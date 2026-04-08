"""Клиент API Siseli Solar (Sun House)."""
import json
import logging
import os
from typing import Any

import aiohttp

from .const import API_BASE_URL, TOKEN_FILE

_LOGGER = logging.getLogger(__name__)


class SiseliApiError(Exception):
    """Общая ошибка API."""

class SiseliAuthError(SiseliApiError):
    """Ошибка авторизации."""

class SiseliConnectionError(SiseliApiError):
    """Ошибка соединения."""


class SiseliAPI:
    """Клиент API Siseli Solar."""

    def __init__(self, token: str = "", session: aiohttp.ClientSession | None = None,
                 timezone: str = "Europe/Moscow", config_dir: str = "") -> None:
        self.token = token
        self.timezone = timezone
        self._session = session
        self._config_dir = config_dir

    def _get_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "IOT-Time-Zone": self.timezone,
            "IOT-Token": self.token,
        }

    def load_token_from_file(self) -> bool:
        """Загрузить токен из файла (записывается Puppeteer скриптом).

        Вызывается ПЕРЕД каждым запросом к API — всегда использует
        самый свежий токен из файла.
        """
        try:
            path = os.path.join(self._config_dir, TOKEN_FILE) if self._config_dir else TOKEN_FILE
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                new_token = data.get("access_token", "")
                if new_token and new_token != self.token:
                    self.token = new_token
                    _LOGGER.info("Siseli: токен обновлён из файла")
                    return True
        except Exception as e:
            _LOGGER.debug("Не удалось прочитать %s: %s", TOKEN_FILE, e)
        return False

    async def _request(self, endpoint: str, data: dict[str, Any] | None = None, method: str = "POST") -> dict[str, Any]:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

        url = f"{API_BASE_URL}{endpoint}"
        headers = self._get_headers()

        try:
            if method == "GET":
                req = self._session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30))
            else:
                req = self._session.post(url, json=data or {}, headers=headers, timeout=aiohttp.ClientTimeout(total=30))
            async with req as resp:
                if resp.status >= 400:
                    raise SiseliApiError(f"HTTP {resp.status}")
                result = await resp.json()
        except aiohttp.ClientError as err:
            raise SiseliConnectionError(f"Ошибка соединения: {err}") from err

        code = result.get("code", -1)
        if code != 0:
            msg = result.get("message", "Unknown error")
            if code in (30, 31, 32, 33, 34, 35):
                raise SiseliAuthError(f"Токен недействителен ({code}): {msg}")
            raise SiseliApiError(f"API ошибка ({code}): {msg}")

        return result.get("data", {})

    async def get_stations(self) -> list[dict[str, Any]]:
        data = {"page": 1, "count": 50, "state": "", "stationType": "",
                "connectedGridType": "", "name": ""}
        result = await self._request("/apis/station/list", data=data)
        return result.get("list", [])

    async def get_devices(self) -> list[dict[str, Any]]:
        data = {"page": 1, "count": 50, "serialNumber": "", "name": "",
                "state": "", "applyModeCategory": 1}
        result = await self._request("/apis/device/list", data=data)
        return result.get("list", [])

    async def get_device_state(self, device_id: str) -> dict[str, Any]:
        """Получить данные устройства в реальном времени (все параметры)."""
        result = await self._request(
            f"/apis/deviceState/simple/state/latest/v1?deviceId={device_id}",
            data=None, method="GET"
        )
        return result.get("fields", {})

    async def get_all_data(self) -> dict[str, Any]:
        stations = await self.get_stations()
        devices = await self.get_devices()

        # Получаем realtime данные для каждого устройства
        device_states = {}
        for device in devices:
            device_id = device.get("id", "")
            if device_id:
                try:
                    state = await self.get_device_state(device_id)
                    device_states[device_id] = state
                except Exception as e:
                    _LOGGER.debug("Не удалось получить state для %s: %s", device_id, e)

        return {"stations": stations, "devices": devices, "device_states": device_states}

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
