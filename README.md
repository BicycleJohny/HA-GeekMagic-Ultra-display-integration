# GeekMagic Ultra Display for Home Assistant

HACS custom integration and ESPHome configuration for showing Home Assistant
entities on the ESP8266-based GeekMagic Ultra. The integration renders a small
JSON payload and sends it through Home Assistant's ESPHome API to a text entity
on the display. It does not use the stock GeekMagic firmware or a direct HTTP
server on the clock.

The project is inspired by
[geekmagic-hacs](https://github.com/adrienbrault/geekmagic-hacs), especially its
selection of entities, layouts, and color themes. This implementation is
purpose-built for the Ultra's ESP8266 and renders locally on its 240 x 240
display rather than sending full-screen images.

## Requirements

- Home Assistant with the ESPHome integration configured.
- GeekMagic Ultra / SmallTV hardware using ESP8266. The ESP32 Pro needs a
  different pinout and firmware and is not supported by this YAML.
- ESPHome firmware installed from [`esphome/geekmagic-ultra.yaml`](esphome/geekmagic-ultra.yaml).

## Install the ESPHome firmware

1. Copy `esphome/geekmagic-ultra.yaml` into your ESPHome configuration.
2. Add `api_encryption_key`, `wifi_ssid`, `wifi_password`, and
   `fallback_password` to ESPHome `secrets.yaml`. Use the same API key in the
   device configuration; Home Assistant discovers the ESPHome device over the
   network after it joins Wi-Fi.
3. Compile and initially flash the device over 3.3 V USB-UART. GPIO14/GPIO13
   are SPI clock/data, GPIO0 is display DC, GPIO2 is display reset, and GPIO5
   controls the backlight. Never connect 5 V logic to the ESP8266.
4. Add or confirm the device in **Settings → Devices & services → ESPHome**.
   The device must expose the text entity **Display payload**.

The YAML uses the no-framebuffer ST7789V external component because a full
240 x 240 framebuffer is a poor fit for ESP8266 memory. This driver is fetched
from the `rletendu/esphome` Git repository at build time. The display is only
redrawn when a payload arrives, avoiding the five-second refresh flicker.

## Install through HACS

1. In HACS, add this GitHub repository as a **custom repository** of category
   **Integration**, then install **GeekMagic Ultra Display**.
2. Restart Home Assistant.
3. Select **Settings → Devices & services → Add integration → GeekMagic**.
4. Select the ESPHome **Display payload** text entity, up to four source
   entities, a title, layout, and color theme.

The integration sends a fresh payload at setup and whenever any selected
source entity changes. To edit the sources, layout, title, or theme later, open
the integration's options.

### Layouts and themes

- **List**: title and up to four label/value rows.
- **Hero**: emphasizes the first entity, with remaining entities below.
- **Compact**: tighter label/value spacing.
- **Midnight**, **Ocean**, **Amber**, and **Light** color themes.

Numeric states include their `unit_of_measurement` when available. Binary
`on`/`off` states are shown as Zapnuto/Vypnuto. Missing or unavailable entities
are rendered as Nedostupné. The payload is limited to 255 characters to match
Home Assistant's ESPHome text-entity limit. It supports up to four selected
entities; long labels and values are shortened as needed to fit.

## Data path

`Home Assistant entity state → GeekMagic integration → text.set_value service
→ ESPHome native API → ESPHome Display payload text entity → ST7789V`

The integration does not connect directly to the device IP. The ESPHome
integration must be online and expose the selected text entity; the `text`
domain service call then transports the value to the device.

## Development checks

Run the renderer unit tests with:

```sh
python -m unittest discover -s tests
```

## Acknowledgements

- [ESPHome Community discussion on GeekMagic SmallTV/Ultra/Pro](https://community.home-assistant.io/t/installing-esphome-on-geekmagic-smart-weather-clock-smalltv-pro/618029)
- [geekmagic-hacs](https://github.com/adrienbrault/geekmagic-hacs) for display customization inspiration.
