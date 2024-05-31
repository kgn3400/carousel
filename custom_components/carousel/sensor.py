"""Sensor for Carousel helper."""

from __future__ import annotations

from typing import Any

from custom_components.carousel.base_classes import BaseCarousel, BaseEntityInfo
from homeassistant.components.sensor import (  # SensorDeviceClass,; SensorEntityDescription,
    SensorEntity,
)
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.template import Template
from homeassistant.util import dt as dt_util

from .const import CONF_ENTITY_IDS, CONF_SHOW_IF_TEMPLATE, TRANSLATION_KEY


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
class CarouselSensor(SensorEntity, BaseCarousel):
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

    # ------------------------------------------------------------------
    async def async_refresh(self) -> None:
        """Refresh."""

        await self.async_refresh_common()
        return

        # ------------------------------------------------------------------
        async def async_refresh_entity():
            await self.async_refresh_common_first_part()

            self.current_entity = self.entities_list[
                self.current_entity_pos
            ] = await self.async_get_entity_info(self.current_entity)

            self.device_class = self.current_entity.device_class

        await async_refresh_entity()

        tmp_res: str = ""

        if len(self.entities_list) > 0 and self.entry.options.get(
            CONF_SHOW_IF_TEMPLATE, ""
        ):
            while tmp_res != "True" and any(
                item.is_visible for item in self.entities_list
            ):
                self.async_write_ha_state()

                value_template: Template | None = Template(
                    str(self.entry.options.get(CONF_SHOW_IF_TEMPLATE)), self.hass
                )

                tmp_res = str(value_template.async_render_with_possible_json_value(""))

                if tmp_res == "True":
                    self.entities_list[self.current_entity_pos].is_visible = True

                else:
                    self.entities_list[self.current_entity_pos].is_visible = False
                    await async_refresh_entity()

            if not any(item.is_visible for item in self.entities_list):
                self.current_entity = None
                return

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
    def extra_state_attributes(self) -> dict:
        """Extra state attributes.

        Returns:
            dict: Extra state attributes

        """

        attr: dict = {}

        if self.current_entity is not None and self.current_entity.state is not None:
            attr = self.current_entity.state.attributes.copy()

        if any(item.is_visible for item in self.entities_list):
            attr["any entities visible"] = True
        else:
            attr["any entities visible"] = False

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
    # async def get_entity_infoX(self, entity_info: SensorEntityInfo) -> SensorEntityInfo:
    #     """Get entity info."""
    #     state: State | None = self.hass.states.get(entity_info.entity_id)

    #     if state is not None:
    #         entity_info.friendly_name = state.attributes.get(ATTR_FRIENDLY_NAME, None)
    #         entity_info.icon = state.attributes.get(ATTR_ICON, None)
    #         entity_info.device_class = get_device_class(
    #             self.hass, entity_info.entity_id
    #         )
    #         entity_info.unit_of_measurement = state.attributes.get(
    #             ATTR_UNIT_OF_MEASUREMENT, None
    #         )

    #         if entity_info.icon is not None or entity_info.device_class is not None:
    #             return entity_info

    #         entity_registry = er.async_get(self.hass)
    #         source_entity = entity_registry.async_get(entity_info.entity_id)

    #         if source_entity is not None:
    #             if source_entity.icon is not None:
    #                 entity_info.icon = source_entity.icon
    #                 return entity_info

    #             icons = await ic.async_get_icons(
    #                 self.hass,
    #                 "entity",
    #                 integrations=[source_entity.platform],
    #                 # "entity_component",
    #                 # integrations=["sensor"],
    #             )

    #             if (
    #                 icons is not None
    #                 and source_entity.platform in icons
    #                 and source_entity.domain in icons[source_entity.platform]
    #                 and source_entity.translation_key
    #                 in icons[source_entity.platform][source_entity.domain]
    #                 and "default"
    #                 in icons[source_entity.platform][source_entity.domain][
    #                     source_entity.translation_key
    #                 ]
    #             ):
    #                 entity_info.icon = icons[source_entity.platform][
    #                     source_entity.domain
    #                 ][source_entity.translation_key]["default"]

    #     return entity_info
