"""The integration setup."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

from .const import DOMAIN, DEFAULT_TCP_PORT
from .coordinator import SolisDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    # store a coordinator that listens for packets and holds the parsed data
    port = entry.options.get("port", DEFAULT_TCP_PORT)
    coordinator = SolisDataUpdateCoordinator(hass, entry, port=port)
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "entry": entry,
    }

    # start the listener in background
    await coordinator.async_start()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # stop listener/coordinator
        data = hass.data[DOMAIN].pop(entry.entry_id, {})
        coordinator = data.get("coordinator")
        if coordinator:
            await coordinator.async_stop()

    return unload_ok