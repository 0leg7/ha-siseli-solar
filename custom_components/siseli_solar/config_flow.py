"""Config flow для Siseli Solar."""
import json
import logging
import os
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult

from .api import SiseliAPI, SiseliAuthError, SiseliConnectionError
from .const import DOMAIN, CONF_TOKEN, TOKEN_FILE

_LOGGER = logging.getLogger(__name__)


class SiseliSolarConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        # Пробуем прочитать токен из файла
        token_default = ""
        try:
            path = self.hass.config.path(TOKEN_FILE)
            if os.path.exists(path):
                with open(path) as f:
                    token_default = json.load(f).get("access_token", "")
        except Exception:
            pass

        if user_input is not None:
            token = user_input[CONF_TOKEN].strip()
            api = SiseliAPI(token=token)
            try:
                stations = await api.get_stations()
                if not stations:
                    errors["base"] = "no_stations"
                else:
                    owner = stations[0].get("ownerUserName", "Solar")
                    await self.async_set_unique_id(f"siseli_{owner.lower()}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Siseli Solar ({owner})",
                        data={CONF_TOKEN: token},
                    )
            except SiseliAuthError:
                errors["base"] = "invalid_auth"
            except SiseliConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Ошибка Siseli")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_TOKEN, default=token_default): str}),
            errors=errors,
        )
