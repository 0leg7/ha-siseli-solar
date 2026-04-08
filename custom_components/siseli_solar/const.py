"""Константы для интеграции Siseli Solar (Sun House)."""

DOMAIN = "siseli_solar"
API_BASE_URL = "https://solar.siseli.com"
CONF_TOKEN = "token"
TOKEN_FILE = "siseli_token.json"
DEFAULT_SCAN_INTERVAL = 300

# === Сенсоры станции (из /apis/station/list) ===
STATION_SENSORS = {
    "producing_power": {
        "key": "producingPower", "name": "Мощность генерации",
        "unit": "kW", "device_class": "power", "state_class": "measurement", "icon": "mdi:solar-power",
    },
    "daily_production": {
        "key": "dailyProducedQuantity", "name": "Выработка за сегодня",
        "unit": "kWh", "device_class": "energy", "state_class": "total_increasing", "icon": "mdi:solar-power-variant",
    },
    "monthly_production": {
        "key": "monthlyProducedQuantity", "name": "Выработка за месяц",
        "unit": "kWh", "device_class": "energy", "state_class": "total_increasing", "icon": "mdi:calendar-month",
    },
    "yearly_production": {
        "key": "yearlyProducedQuantity", "name": "Выработка за год",
        "unit": "kWh", "device_class": "energy", "state_class": "total_increasing", "icon": "mdi:calendar",
    },
    "total_production": {
        "key": "totalProducedQuantity", "name": "Выработка всего",
        "unit": "kWh", "device_class": "energy", "state_class": "total_increasing", "icon": "mdi:counter",
    },
    "co2_reduction": {
        "key": "co2EmissionReduction", "name": "Снижение CO2",
        "unit": "kg", "device_class": None, "state_class": "total_increasing", "icon": "mdi:molecule-co2",
    },
}

# === Сенсоры реального времени (из /apis/deviceState/simple/state/latest/v1) ===
REALTIME_SENSORS = {
    # --- Сеть (Grid) ---
    "grid_voltage": {
        "key": "gridVoltage", "name": "Напряжение сети",
        "unit": "V", "device_class": "voltage", "state_class": "measurement", "icon": "mdi:transmission-tower",
    },
    "grid_frequency": {
        "key": "gridFrequency", "name": "Частота сети",
        "unit": "Hz", "device_class": "frequency", "state_class": "measurement", "icon": "mdi:sine-wave",
    },
    # --- Выход (AC Output) ---
    "ac_output_voltage": {
        "key": "acOutputVoltage", "name": "Напряжение выхода",
        "unit": "V", "device_class": "voltage", "state_class": "measurement", "icon": "mdi:flash",
    },
    "ac_output_frequency": {
        "key": "acOutputFrequency", "name": "Частота выхода",
        "unit": "Hz", "device_class": "frequency", "state_class": "measurement", "icon": "mdi:sine-wave",
    },
    "ac_output_power": {
        "key": "acOutputActivePower", "name": "Мощность нагрузки",
        "unit": "kW", "device_class": "power", "state_class": "measurement", "icon": "mdi:home-lightning-bolt",
    },
    "ac_output_apparent_power": {
        "key": "ratedApparentPower", "name": "Полная мощность нагрузки",
        "unit": "VA", "device_class": "apparent_power", "state_class": "measurement", "icon": "mdi:flash-triangle",
    },
    "output_load_percent": {
        "key": "outputLoadPercent", "name": "Загрузка инвертора",
        "unit": "%", "device_class": None, "state_class": "measurement", "icon": "mdi:gauge",
    },
    # --- Батарея ---
    "battery_voltage": {
        "key": "batteryVoltage", "name": "Напряжение батареи",
        "unit": "V", "device_class": "voltage", "state_class": "measurement", "icon": "mdi:car-battery",
    },
    "battery_capacity": {
        "key": "batteryCapacity", "name": "Заряд батареи",
        "unit": "%", "device_class": "battery", "state_class": "measurement", "icon": "mdi:battery",
    },
    "battery_charging_current": {
        "key": "batteryChargingCurrent", "name": "Ток заряда батареи",
        "unit": "A", "device_class": "current", "state_class": "measurement", "icon": "mdi:current-dc",
    },
    "battery_discharge_current": {
        "key": "batteryDischargeCurrent", "name": "Ток разряда батареи",
        "unit": "A", "device_class": "current", "state_class": "measurement", "icon": "mdi:current-dc",
    },
    # --- Солнечные панели (PV) ---
    "pv_input_voltage": {
        "key": "pvInputVoltage1", "name": "Напряжение PV",
        "unit": "V", "device_class": "voltage", "state_class": "measurement", "icon": "mdi:solar-panel",
    },
    "pv_input_current": {
        "key": "pv1InputCurrentForBattery", "name": "Ток PV",
        "unit": "A", "device_class": "current", "state_class": "measurement", "icon": "mdi:solar-panel",
    },
    "generation_power": {
        "key": "generationPower", "name": "Мощность PV",
        "unit": "kW", "device_class": "power", "state_class": "measurement", "icon": "mdi:solar-power",
    },
    # --- Температура ---
    "inverter_temperature": {
        "key": "inverterHeatSinkTemperature", "name": "Температура инвертора",
        "unit": "°C", "device_class": "temperature", "state_class": "measurement", "icon": "mdi:thermometer",
    },
    # --- Шина ---
    "bus_voltage": {
        "key": "busVoltage", "name": "Напряжение шины DC",
        "unit": "V", "device_class": "voltage", "state_class": "measurement", "icon": "mdi:flash-circle",
    },
}

# === Текстовые сенсоры (статусы) ===
STATUS_SENSORS = {
    "working_mode": {
        "key": "workingMode", "name": "Режим работы", "icon": "mdi:cog",
    },
    "charging_status": {
        "key": "chargingStatus", "name": "Статус заряда", "icon": "mdi:battery-charging",
    },
    "output_source_priority": {
        "key": "outputSourcePriority", "name": "Приоритет источника", "icon": "mdi:priority-high",
    },
    "charger_source_priority": {
        "key": "chargerSourcePriority", "name": "Приоритет зарядки", "icon": "mdi:battery-arrow-up",
    },
}

# === Сенсоры устройства (из /apis/device/list) — оставляем базовые ===
DEVICE_SENSORS = {
    "device_total_energy": {
        "key": "totalGeneratedEnergy", "name": "Всего выработано (инвертор)",
        "unit": "kWh", "device_class": "energy", "state_class": "total_increasing", "icon": "mdi:lightning-bolt",
    },
}
