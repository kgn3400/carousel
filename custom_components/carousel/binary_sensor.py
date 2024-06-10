"""Sensor for Carousel helper."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_carousel_entity import BaseCarouselEntity
from .base_entity_info import BaseEntityInfo
from .const import CONF_ENTITY_IDS, TRANSLATION_KEY


# ------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensor setup."""

    registry = er.async_get(hass)
    entities = er.async_validate_entity_ids(registry, entry.options[CONF_ENTITY_IDS])

    if len(entities) > 0:
        async_add_entities([CarouselBinarySensor(hass, entry, entities)])


# ------------------------------------------------------
# ------------------------------------------------------
class BinarySensorEntityInfo(BaseEntityInfo):
    """Sensor Entity info class."""

    def __init__(
        self,
        entity_id: str,
        friendly_name: str | None = None,
        icon: str | None = None,
        unit_of_measurement: str | None = None,
        device_class: BinarySensorDeviceClass | None = None,
    ) -> None:
        """Sensor entity info."""
        super().__init__(
            entity_id,
            friendly_name,
            icon,
            unit_of_measurement,
        )

        self.device_class: BinarySensorDeviceClass | None = device_class
        self.entity_obj: BinarySensorEntity


# ------------------------------------------------------
# ------------------------------------------------------
class CarouselBinarySensor(BinarySensorEntity, BaseCarouselEntity):
    """Binary sensor class for carousel."""

    # ------------------------------------------------------
    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, entities: list[str]
    ) -> None:
        """Carousel sensor."""
        super().__init__(
            hass,
            entry,
        )

        self.entities_list: list[BinarySensorEntityInfo] = [
            BinarySensorEntityInfo(entity) for entity in entities
        ]

        self.translation_key = TRANSLATION_KEY

    # ------------------------------------------------------
    @property
    def is_on(self) -> bool:
        """Get the state."""

        if self.current_entity is not None:
            return self.current_entity.state.state == "on"

        return None

    # ------------------------------------------------------
    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit the value is expressed in."""

        if self.current_entity is not None:
            return self.current_entity.unit_of_measurement

        return None

    # ------------------------------------------------------
    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    # ------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return if entity is available."""

        return self.coordinator.last_update_success

    # ------------------------------------------------------
