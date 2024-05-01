"""Sensor for Carousel helper."""

from __future__ import annotations

from custom_components.carousel.base_classes import BaseCarousel, BaseEntityInfo
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_FRIENDLY_NAME, ATTR_ICON, ATTR_UNIT_OF_MEASUREMENT
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er, icon as ic
from homeassistant.helpers.entity import get_device_class
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
class CarouselBinarySensor(BinarySensorEntity, BaseCarousel):
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

    # ------------------------------------------------------------------
    async def async_refresh(self) -> None:
        """Refresh."""

        await self.async_refresh_common_first_part()

        self.current_entity = self.entities_list[
            self.current_entity_pos
        ] = await self.async_get_entity_info(self.current_entity)

        self.device_class = self.current_entity.device_class

        await self.async_refresh_common_last_part()

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        """Name.

        Returns:
            str: Name

        """

        if self.current_entity is not None:
            return self.current_entity.friendly_name

        return self.entry.title

    # ------------------------------------------------------
    @property
    def icon(self) -> str:
        """Icon.

        Returns:
            str: Icon

        """
        if self.current_entity is not None:
            return self.current_entity.icon

        return None

    # ------------------------------------------------------
    @property
    def is_on(self) -> bool:
        """Get the state."""

        if self.current_entity is not None:
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
    def extra_state_attributes(self) -> dict:
        """Extra state attributes.

        Returns:
            dict: Extra state attributes

        """

        attr: dict = {}

        if self.current_entity is not None and self.current_entity.state is not None:
            attr = self.current_entity.state.attributes.copy()

        return attr

    # ------------------------------------------------------
    @property
    def unique_id(self) -> str:
        """Unique id.

        Returns:
            str: Unique  id

        """
        return self.entry.entry_id

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

    async def get_entity_infoX(
        self, entity_info: BinarySensorEntityInfo
    ) -> BinarySensorEntityInfo:
        """Get entity info."""
        state: State | None = self.hass.states.get(entity_info.entity_id)

        if state is not None:
            entity_info.friendly_name = state.attributes.get(ATTR_FRIENDLY_NAME, None)
            entity_info.icon = state.attributes.get(ATTR_ICON, None)
            entity_info.device_class = get_device_class(
                self.hass, entity_info.entity_id
            )
            entity_info.unit_of_measurement = state.attributes.get(
                ATTR_UNIT_OF_MEASUREMENT, None
            )

            if entity_info.icon is not None or entity_info.device_class is not None:
                return entity_info

            entity_registry = er.async_get(self.hass)
            source_entity = entity_registry.async_get(entity_info.entity_id)

            if source_entity is not None:
                if source_entity.icon is not None:
                    entity_info.icon = source_entity.icon
                    return entity_info

                icons = await ic.async_get_icons(
                    self.hass,
                    "entity",
                    integrations=[source_entity.platform],
                    # "entity_component",
                    # integrations=["sensor"],
                )

                if (
                    icons is not None
                    and source_entity.platform in icons
                    and source_entity.domain in icons[source_entity.platform]
                    and source_entity.translation_key
                    in icons[source_entity.platform][source_entity.domain]
                    and "default"
                    in icons[source_entity.platform][source_entity.domain][
                        source_entity.translation_key
                    ]
                ):
                    entity_info.icon = icons[source_entity.platform][
                        source_entity.domain
                    ][source_entity.translation_key]["default"]

        return entity_info
