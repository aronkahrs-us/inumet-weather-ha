# [Inumet][inumet]

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

**This integration will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show acrive alerts.
`sensor` | Show Weather info.
`wheater` | Wheater sensor with forecast.

## Installation

### HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=aronkahrs-us&repository=inumet-weather-ha&category=integration)

### Manual

1. Using the tool of choice open the directory (folder) for your [HA configuration](https://www.home-assistant.io/docs/configuration/) (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `inumet`.
4. Download _all_ the files from the `custom_components/inumwt/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant


## Configuration is done in the UI

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=inumet)

[![Config flow](configimg)]
<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[inumet]: https://github.com/aronkahrs-us/inumet-weather-ha
[commits-shield]: https://img.shields.io/github/commit-activity/y/aronkahrs-us/inumet-weather-ha.svg?style=for-the-badge
[commits]: https://github.com/aronkahrs-us/inumet-weather-ha/commits/main
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/ludeeus/integration_blueprint.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Aron%20Kahrs-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/aronkahrs-us/inumet-weather-ha.svg?style=for-the-badge
[releases]: https://github.com/aronkahrs-us/inumet-weather-ha/releases
[configimg]: (https://github.com/aronkahrs-us/inumet-weather-ha/blob/main/step.jpg?raw=true)
