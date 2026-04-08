"""Интеграция Siseli Solar (Sun House) для Home Assistant."""
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SiseliAPI, SiseliAuthError, SiseliConnectionError
from .const import DOMAIN, CONF_TOKEN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)

    # Сначала пробуем токен из файла (свежий от аддона), потом из config_entry
    api = SiseliAPI(
        token=entry.data[CONF_TOKEN],
        session=session,
        config_dir=hass.config.config_dir,
    )

    # Пробуем загрузить свежий токен из файла
    api.load_token_from_file()

    try:
        await api.get_stations()
    except SiseliAuthError:
        # Токен из файла тоже не работает
        raise ConfigEntryAuthFailed("Токен истёк. Проверьте аддон Siseli Token Updater.")
    except SiseliConnectionError as err:
        raise UpdateFailed(f"Не удалось подключиться: {err}") from err

    coordinator = SiseliDataCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"api": api, "coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class SiseliDataCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, api: SiseliAPI) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN,
                         update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL))
        self.api = api
        self._auth_failures = 0

    async def _async_update_data(self) -> dict[str, Any]:
        # ВСЕГДА проверяем свежий токен из файла перед запросом
        self.api.load_token_from_file()

        try:
            data = await self.api.get_all_data()
            self._auth_failures = 0
            return data
        except SiseliAuthError:
            self._auth_failures += 1
            _LOGGER.warning("Siseli: ошибка авторизации (попытка %d)", self._auth_failures)

            if self._auth_failures >= 6:
                raise UpdateFailed(
                    "Токен Siseli недействителен уже 30 минут. Проверьте аддон Siseli Token Updater."
                )
            raise UpdateFailed("Токен истёк, жду обновления от аддона...")

        except SiseliConnectionError as err:
            raise UpdateFailed(f"Ошибка соединения: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Ошибка: {err}") from err
