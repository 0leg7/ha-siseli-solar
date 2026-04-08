"""Сенсоры Siseli Solar."""
import logging
from typing import Any
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, STATION_SENSORS, DEVICE_SENSORS, REALTIME_SENSORS, STATUS_SENSORS

_LOGGER = logging.getLogger(__name__)
DC = {"power": SensorDeviceClass.POWER, "energy": SensorDeviceClass.ENERGY,
      "voltage": SensorDeviceClass.VOLTAGE, "current": SensorDeviceClass.CURRENT,
      "temperature": SensorDeviceClass.TEMPERATURE, "frequency": SensorDeviceClass.FREQUENCY,
      "battery": SensorDeviceClass.BATTERY, "apparent_power": SensorDeviceClass.APPARENT_POWER}
SC = {"measurement": SensorStateClass.MEASUREMENT, "total_increasing": SensorStateClass.TOTAL_INCREASING}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = []
    data = coordinator.data or {}

    # Сенсоры станции
    for station in data.get("stations", []):
        sid, sname = station.get("id", ""), station.get("name", "Station")
        for key, sdef in STATION_SENSORS.items():
            entities.append(SiseliSensor(coordinator, "stations", sid, sname, key, sdef, "station"))

    # Сенсоры устройства + realtime + status
    for device in data.get("devices", []):
        did, dname = device.get("id", ""), device.get("name", "Inverter")
        serial = device.get("serialNumber", "")

        # Базовые сенсоры устройства
        for key, sdef in DEVICE_SENSORS.items():
            entities.append(SiseliSensor(coordinator, "devices", did, dname, key, sdef, "inverter", serial))

        # Realtime сенсоры (voltage, current, power, temperature)
        for key, sdef in REALTIME_SENSORS.items():
            entities.append(SiseliRealtimeSensor(coordinator, did, dname, key, sdef, serial))

        # Текстовые статусы (режим работы и т.д.)
        for key, sdef in STATUS_SENSORS.items():
            entities.append(SiseliStatusSensor(coordinator, did, dname, key, sdef, serial))

        # Онлайн/офлайн
        entities.append(SiseliOnlineSensor(coordinator, did, dname, serial))

    add(entities)


def _device_info(did, dname, serial):
    return DeviceInfo(
        identifiers={(DOMAIN, did)},
        name=f"Siseli Inverter {dname}",
        manufacturer="Siseli / PowMr",
        model="PV Inverter",
        serial_number=serial or None,
    )


class SiseliSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, dtype, item_id, item_name, sensor_id, sensor_def, dev_type, serial=""):
        super().__init__(coordinator)
        self._dtype, self._item_id, self._sdef = dtype, item_id, sensor_def
        self._attr_unique_id = f"{DOMAIN}_{item_id}_{sensor_id}"
        self._attr_name = sensor_def["name"]
        self._attr_native_unit_of_measurement = sensor_def.get("unit")
        self._attr_icon = sensor_def.get("icon")
        dc = sensor_def.get("device_class")
        if dc and dc in DC: self._attr_device_class = DC[dc]
        sc = sensor_def.get("state_class")
        if sc and sc in SC: self._attr_state_class = SC[sc]
        if dev_type == "station":
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, item_id)}, name=f"Siseli Station {item_name}",
                manufacturer="Siseli / PowMr", model="Solar Station")
        else:
            self._attr_device_info = _device_info(item_id, item_name, serial)

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        for item in self.coordinator.data.get(self._dtype, []):
            if item.get("id") == self._item_id:
                val = item.get(self._sdef["key"])
                if val is None:
                    val = item.get("summaryProperty", {}).get(self._sdef["key"])
                if val is not None:
                    try: return round(float(val), 3)
                    except: return None
        return None


class SiseliRealtimeSensor(CoordinatorEntity, SensorEntity):
    """Сенсор реального времени (из deviceState API)."""
    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id, device_name, sensor_id, sensor_def, serial=""):
        super().__init__(coordinator)
        self._device_id = device_id
        self._sdef = sensor_def
        self._attr_unique_id = f"{DOMAIN}_{device_id}_rt_{sensor_id}"
        self._attr_name = sensor_def["name"]
        self._attr_native_unit_of_measurement = sensor_def.get("unit")
        self._attr_icon = sensor_def.get("icon")
        dc = sensor_def.get("device_class")
        if dc and dc in DC: self._attr_device_class = DC[dc]
        sc = sensor_def.get("state_class")
        if sc and sc in SC: self._attr_state_class = SC[sc]
        self._attr_device_info = _device_info(device_id, device_name, serial)

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        states = self.coordinator.data.get("device_states", {})
        fields = states.get(self._device_id, {})
        field = fields.get(self._sdef["key"], {})
        val = field.get("value") if isinstance(field, dict) else None
        if val is not None:
            try: return round(float(val), 2)
            except: return None
        return None


class SiseliStatusSensor(CoordinatorEntity, SensorEntity):
    """Текстовый сенсор статуса (режим работы и т.д.)."""
    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id, device_name, sensor_id, sensor_def, serial=""):
        super().__init__(coordinator)
        self._device_id = device_id
        self._sdef = sensor_def
        self._attr_unique_id = f"{DOMAIN}_{device_id}_st_{sensor_id}"
        self._attr_name = sensor_def["name"]
        self._attr_icon = sensor_def.get("icon")
        self._attr_device_info = _device_info(device_id, device_name, serial)

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        states = self.coordinator.data.get("device_states", {})
        fields = states.get(self._device_id, {})
        field = fields.get(self._sdef["key"], {})
        return field.get("valueDisplay") if isinstance(field, dict) else None


class SiseliOnlineSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id, device_name, serial=""):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{DOMAIN}_{device_id}_online"
        self._attr_name = "Статус инвертора"
        self._attr_icon = "mdi:lan-connect"
        self._attr_device_info = _device_info(device_id, device_name, serial)

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        for d in self.coordinator.data.get("devices", []):
            if d.get("id") == self._device_id:
                return "Online" if d.get("isOnline") else "Offline"
        return None

    @property
    def icon(self):
        return "mdi:lan-connect" if self.native_value == "Online" else "mdi:lan-disconnect"
