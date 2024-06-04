"""The Carousel integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_PLATFORM_TYPE, DOMAIN


# ------------------------------------------------------------------
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up State updates from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    tmp_platform: list[Platform] = [
        Platform.__members__[str(entry.options.get(CONF_PLATFORM_TYPE)).upper()]
    ]

    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, tmp_platform)

    return True


# ------------------------------------------------------------------
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    tmp_platform: list[Platform] = [
        Platform.__members__[str(entry.options.get(CONF_PLATFORM_TYPE)).upper()]
    ]
    return await hass.config_entries.async_unload_platforms(entry, tmp_platform)


# ------------------------------------------------------------------
async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


# ------------------------------------------------------------------
async def update_listener(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> None:
    """Reload on config entry update."""

    await hass.config_entries.async_reload(config_entry.entry_id)
