"""Sensor for Carousel helper."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (  # SensorDeviceClass,; SensorEntityDescription,
    SensorEntity,
)
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

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
        async_add_entities([CarouselSensor(hass, entry, entities)])


# ------------------------------------------------------
# ------------------------------------------------------
class SensorEntityInfo(BaseEntityInfo):
    """Sensor Entity info class."""

    def __init__(
        self,
        entity_id: str,
        friendly_name: str | None = None,
        icon: str | None = None,
        unit_of_measurement: str | None = None,
        device_class: SensorDeviceClass | None = None,
    ) -> None:
        """Sensor entity info."""
        super().__init__(
            entity_id,
            friendly_name,
            icon,
            unit_of_measurement,
        )

        self.device_class: SensorDeviceClass | None = device_class
        self.entity_obj: SensorEntity


# ------------------------------------------------------
# ------------------------------------------------------
class CarouselSensor(SensorEntity, BaseCarouselEntity):
    """Sensor class for carousel."""

    # ------------------------------------------------------
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        entities: list[str],
    ) -> None:
        """Carousel sensor."""
        super().__init__(
            hass,
            entry,
        )

        self.entities_list: list[SensorEntityInfo] = [
            SensorEntityInfo(entity) for entity in entities
        ]

        self.translation_key = TRANSLATION_KEY

    # ------------------------------------------------------
    @property
    def native_value(self) -> Any | None:
        """Native value.

        Returns:
            str | None: Native value

        """

        if self.current_entity is not None:
            if self.current_entity.device_class == SensorDeviceClass.TIMESTAMP:
                return dt_util.parse_datetime(self.current_entity.state.state)

            if (
                self.current_entity.device_class is SensorDeviceClass.DATE
                and (value := dt_util.parse_datetime(self.current_entity.state.state))
                is not None
            ):
                return value.date()

            return self.current_entity.state.state

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
