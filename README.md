# Siseli Solar (Sun House) for Home Assistant

Home Assistant integration + token updater addon for [Siseli Solar](https://solar.siseli.com/) (PowMr) inverters.

## Components

### 1. Custom Integration (`custom_components/siseli_solar`)

Provides real-time sensors for your Siseli/PowMr solar inverter:

- **Station**: generation power, daily/monthly/yearly/total production, CO2 reduction
- **Inverter realtime**: grid voltage/frequency, AC output, battery voltage/charge/current, PV voltage/current/power, temperature, bus voltage
- **Status**: working mode, charging status, output/charger source priority, online/offline

#### Installation

Copy `custom_components/siseli_solar` to your HA `config/custom_components/` directory and restart Home Assistant.

Then go to **Settings > Devices & Services > Add Integration > Siseli Solar**.

### 2. Token Updater Addon (`siseli_token_updater`)

Local HA addon that automatically refreshes the API token every 110 minutes using headless Chromium.

#### Installation

1. Copy `siseli_token_updater` to your HA `addons/` directory
2. Go to **Settings > Add-ons > Add-on Store** (three dots) > **Check for updates**
3. Find **Siseli Token Updater** in local add-ons and install
4. Configure your account and password in the addon settings
5. Start the addon

The addon writes the token to `/config/siseli_token.json`. The integration reads it automatically before each API call.

## How it works

```
[Siseli Solar Cloud] <-- API calls with IOT-Token --> [siseli_solar integration]
                                                              ^
                                                              | reads token
                                                              |
[solar.siseli.com] <-- Puppeteer login --> [siseli_token_updater addon]
                                                   |
                                                   v
                                           /config/siseli_token.json
```

## License

MIT
