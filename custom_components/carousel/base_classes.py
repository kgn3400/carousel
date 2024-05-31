"""Base classes."""

from __future__ import annotations

from datetime import datetime, timedelta

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_FRIENDLY_NAME,
    ATTR_ICON,
    ATTR_UNIT_OF_MEASUREMENT,
)
from homeassistant.core import (
    CALLBACK_TYPE,
    Event,
    HomeAssistant,
    ServiceCall,
    State,
    callback,
)
from homeassistant.helpers import (
    config_validation as cv,
    entity_platform,
    entity_registry as er,
    icon as ic,
    issue_registry as ir,
    start,
)
from homeassistant.helpers.entity import Entity, get_device_class
from homeassistant.helpers.entity_platform import EntityPlatform
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
)
from homeassistant.helpers.template import Template
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_LISTEN_TO_TIMER_TRIGGER,
    CONF_RESTART_TIMER,
    CONF_ROTATE_EVERY_MINUTES,
    CONF_SHOW_IF_TEMPLATE,
    DOMAIN,
    DOMAIN_NAME,
    LOGGER,
    SERVICE_ADD_ENTITY_ID,
    SERVICE_REMOVE_ENTITY_ID,
    SERVICE_SHOW_ENTITY_ID,
    SERVICE_SHOW_FOR,
    SERVICE_SHOW_X_TIMES,
    TRANSLATION_KEY_MISSING_ENTITY,
    RefreshType,
)
from .timer_trigger import TimerTrigger


# ------------------------------------------------------
# ------------------------------------------------------
class BaseEntityInfo:
    """Base entity info class."""

    def __init__(
        self,
        entity_id: str,
        friendly_name: str | None = None,
        icon: str | None = None,
        unit_of_measurement: str | None = None,
        show_x_times: int | None = None,
        remove_at_timedelta: timedelta | None = None,
    ) -> None:
        """Entity info base."""
        self.entity_id: str = entity_id
        self.friendly_name: str | None = friendly_name
        self.icon: str | None = icon
        self.unit_of_measurement: str | None = unit_of_measurement
        self.state: State = None
        self.show_x_times: int = show_x_times
        self.remove_at: datetime = None
        self.is_visible: bool = True

        if remove_at_timedelta is not None:
            self.remove_at = datetime.now() + remove_at_timedelta

        self.entity_obj: Entity
        self.device_class: str


# ------------------------------------------------------
# ------------------------------------------------------
class BaseCarousel(Entity):
    """Carousel base."""

    restart_timer: bool = True

    # ------------------------------------------------------
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Carousel sensor."""
        self.hass: HomeAssistant = hass
        self.entry: ConfigEntry = entry

        self.entities_list: list[BaseEntityInfo]
        self.cancel_state_listener: CALLBACK_TYPE = None

        self.current_entity: BaseEntityInfo = None
        self.current_entity_pos = -1
        self.stay_at_current_pos: bool = False
        self.refresh_type: RefreshType = RefreshType.NORMAL

        self.timer_trigger: TimerTrigger

        self.coordinator: DataUpdateCoordinator = DataUpdateCoordinator(
            self.hass,
            LOGGER,
            name=DOMAIN,
            update_interval=None,
            update_method=self.async_refresh,
        )

        self.platform: EntityPlatform = entity_platform.async_get_current_platform()

        self.platform.async_register_entity_service(
            self.platform.domain + "_add",
            {
                vol.Required(SERVICE_ADD_ENTITY_ID): cv.string,
                vol.Optional(SERVICE_SHOW_X_TIMES): cv.positive_int,
                vol.Optional(SERVICE_SHOW_FOR): cv.time_period,
            },
            self.async_add_entity_dispatcher,
        )
        self.platform.async_register_entity_service(
            self.platform.domain + "_show_entity",
            {
                vol.Required(SERVICE_SHOW_ENTITY_ID): cv.string,
            },
            self.async_show_entity_dispatcher,
        )
        self.platform.async_register_entity_service(
            self.platform.domain + "_show_next",
            {},
            self.async_show_next_dispatcher,
        )
        self.platform.async_register_entity_service(
            self.platform.domain + "_show_prev",
            {},
            self.async_show_prev_dispatcher,
        )
        self.platform.async_register_entity_service(
            self.platform.domain + "_remove",
            {
                vol.Required(SERVICE_REMOVE_ENTITY_ID): cv.string,
            },
            self.async_remove_entity_dispatcher,
        )

        if self.entry.options.get(CONF_LISTEN_TO_TIMER_TRIGGER, ""):
            self.refresh_type = RefreshType.LISTEN_TO_TIMER_TRIGGER

            self.timer_trigger = TimerTrigger(
                self,
                self.entry.options.get(CONF_LISTEN_TO_TIMER_TRIGGER, ""),
                self.async_handle_timer_finished,
                self.entry.options.get(CONF_RESTART_TIMER, ""),
            )
            self.coordinator.update_interval = None

    # ------------------------------------------------------------------
    async def async_handle_timer_finished(self, error: bool) -> None:
        """Handle timer finished."""

        if error:
            self.refresh_type = RefreshType.NORMAL
            self.coordinator.update_interval = timedelta(
                minutes=self.entry.options.get(CONF_ROTATE_EVERY_MINUTES, 1)
            )

        if self.refresh_type == RefreshType.LISTEN_TO_TIMER_TRIGGER:
            await self.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_add_entity_dispatcher(
        self, entity: BaseCarousel, service_data: ServiceCall
    ) -> None:
        """Add entity."""

        await entity.async_add_entity(service_data)

    # ------------------------------------------------------------------
    async def async_add_entity(self, service_data: ServiceCall) -> None:
        """Add entity."""
        self.entities_list.append(
            BaseEntityInfo(service_data.data.get(SERVICE_ADD_ENTITY_ID), "")
        )
        await self.async_verify_entities_exist()

    # ------------------------------------------------------------------
    async def async_show_entity_dispatcher(
        self, entity: BaseCarousel, service_data: ServiceCall
    ) -> None:
        """Show entity."""

        await entity.async_show_entity(service_data)

    # ------------------------------------------------------------------
    async def async_show_entity(self, service_data: ServiceCall) -> None:
        """Show entity."""

        if (
            pos := self.find_entity_pos(
                service_data.data.get(SERVICE_SHOW_ENTITY_ID, "")
            )
        ) > -1:
            self.current_entity_pos = pos
            self.stay_at_current_pos = True
            await self.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_show_next_dispatcher(
        self, entity: BaseCarousel, service_data: ServiceCall
    ) -> None:
        """Show next."""

        await entity.async_show_next(service_data)

    # ------------------------------------------------------------------
    async def async_show_next(self, service_data: ServiceCall) -> None:
        """Show next."""

        await self.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_show_prev_dispatcher(
        self, entity: BaseCarousel, service_data: ServiceCall
    ) -> None:
        """Show prev."""

        await entity.async_show_prev(service_data)

    # ------------------------------------------------------------------
    async def async_show_prev(self, service_data: ServiceCall) -> None:
        """Show prev."""

        if len(self.entities_list) == 0:
            self.current_entity = None
            return

        if self.current_entity_pos <= 1:
            self.current_entity_pos = len(self.entities_list) - 1
        else:
            self.current_entity_pos -= 2

        await self.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_remove_entity_dispatcher(
        self, entity: BaseCarousel, service_data: ServiceCall
    ) -> None:
        """Remove entity."""

        await entity.async_show_prev(service_data)

    # ------------------------------------------------------------------
    async def async_remove_entity(self, service_data: ServiceCall) -> None:
        """Remove entity."""

        if (
            pos := self.find_entity_pos(
                service_data.data.get(SERVICE_REMOVE_ENTITY_ID, "")
            )
        ) > -1:
            del self.entities_list[pos]
            self.stay_at_current_pos = True
            await self.coordinator.async_refresh()

    # ------------------------------------------------------------------
    def find_entity_pos(self, entity_id: str) -> int:
        """Find entity pos."""
        for index, entity in enumerate(self.entities_list):
            if entity.entity_id == entity_id:
                return index

        return -1

    # ------------------------------------------------------------------
    async def async_remove_expired_entities(self) -> None:
        """Remove expired entites."""

        if (
            self.current_entity is not None
            and self.current_entity.show_x_times is not None
        ):
            if self.current_entity.show_x_times <= 0:
                del self.entities_list[self.current_entity_pos]
            else:
                self.current_entity.show_x_times -= 1
                self.entities_list[self.current_entity_pos] = self.current_entity

        if (
            self.current_entity is not None
            and self.current_entity.remove_at is not None
            and self.current_entity.remove_at < datetime.now()
        ):
            del self.entities_list[self.current_entity_pos]

    # ------------------------------------------------------------------
    async def async_refresh_common(self) -> None:
        """Refresh common."""

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
                # self.async_write_ha_state()
                tmp_state: State = self.hass.states.get(self.current_entity.entity_id)
                template_values: dict = {
                    "state": tmp_state.state,
                    "state_attributes": tmp_state.attributes.copy(),
                }

                value_template: Template | None = Template(
                    str(self.entry.options.get(CONF_SHOW_IF_TEMPLATE)), self.hass
                )

                tmp_res = str(
                    value_template.async_render_with_possible_json_value(
                        "", variables=template_values
                    )
                )

                if tmp_res == "True":
                    self.entities_list[self.current_entity_pos].is_visible = True

                else:
                    self.entities_list[self.current_entity_pos].is_visible = False
                    await async_refresh_entity()

            if not any(item.is_visible for item in self.entities_list):
                self.current_entity = None
                return

        await self.async_refresh_common_last_part()

    # ------------------------------------------------------------------
    async def async_refresh_common_first_part(self) -> None:
        """Refresh common first part."""

        if len(self.entities_list) == 0:
            self.current_entity = None
            return

        await self.async_remove_expired_entities()

        if self.stay_at_current_pos:
            self.stay_at_current_pos = False
        else:
            self.current_entity_pos += 1

        if (self.current_entity_pos + 1) > len(self.entities_list):
            self.current_entity_pos = 0

        self.current_entity = self.entities_list[self.current_entity_pos]
        self.current_entity.state = self.hass.states.get(self.current_entity.entity_id)

        if self.current_entity.state is not None:
            self.current_entity.entity_obj = self.platform.domain_entities.get(
                self.current_entity.entity_id, None
            )
        else:
            await self.async_create_issue_entity(
                self.current_entity.entity_id, TRANSLATION_KEY_MISSING_ENTITY
            )
            self.entities_list.pop(self.current_entity_pos)
            await self.async_refresh()
            return

        if self.cancel_state_listener is not None:
            self.cancel_state_listener()
            self.cancel_state_listener = None

    # ------------------------------------------------------------------
    async def async_refresh_common_last_part(self) -> None:
        """Refresh common last part."""

        self.cancel_state_listener = async_track_state_change_event(
            self.hass,
            self.current_entity.entity_id,
            self.sensor_state_listener,
        )

    # ------------------------------------------------------
    @callback
    async def sensor_state_listener(
        self,
        event: Event[EventStateChangedData],
    ) -> None:
        """Handle state changes on the observed device."""

        if event.data[ATTR_ENTITY_ID] == self.current_entity.entity_id:
            self.stay_at_current_pos = True
            await self.coordinator.async_refresh()

    # ------------------------------------------------------------------
    async def async_create_issue_entity(
        self, entity_id: str, translation_key: str
    ) -> None:
        """Create issue on entity."""

        ir.async_create_issue(
            self.hass,
            DOMAIN,
            DOMAIN_NAME + datetime.now().isoformat(),
            issue_domain=DOMAIN,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=translation_key,
            translation_placeholders={
                "entity": entity_id,
                "carousel_helper": self.entity_id,
            },
        )

    # ------------------------------------------------------
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""

        if self.cancel_state_listener is not None:
            self.cancel_state_listener()

    # ------------------------------------------------------
    async def async_update(self) -> None:
        """Update the entity. Only used by the generic entity update service."""
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""

        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

        self.async_on_remove(start.async_at_started(self.hass, self.async_hass_started))

    # ------------------------------------------------------
    async def async_verify_entities_exist(self) -> bool:
        """Verify entities exist."""
        res: bool = True

        for index, entity_info in reversed(list(enumerate(self.entities_list))):
            state: State | None = self.hass.states.get(entity_info.entity_id)

            if state is None:
                await self.async_create_issue_entity(
                    entity_info.entity_id,
                    TRANSLATION_KEY_MISSING_ENTITY,
                )
                del self.entities_list[index]
                res = False

        return res

    # ------------------------------------------------------
    async def async_hass_started(self, _event: Event) -> None:
        """Hass started."""

        await self.async_verify_entities_exist()

        if self.refresh_type == RefreshType.NORMAL:
            self.coordinator.update_interval = timedelta(
                minutes=self.entry.options.get(CONF_ROTATE_EVERY_MINUTES, 1)
            )
        elif self.refresh_type == RefreshType.LISTEN_TO_TIMER_TRIGGER:
            if not await self.timer_trigger.async_validate_timer():
                self.coordinator.update_interval = timedelta(
                    minutes=self.entry.options.get(CONF_ROTATE_EVERY_MINUTES, 1)
                )
                self.refresh_type = RefreshType.NORMAL

        self.async_schedule_update_ha_state()
        await self.coordinator.async_refresh()

    # ------------------------------------------------------
    async def async_get_icon(self, entity_id: str) -> str:
        """Get icon."""

        state: State | None = self.hass.states.get(entity_id)
        tmp_icon = state.attributes.get(ATTR_ICON, None)

        if tmp_icon is not None:
            return tmp_icon

        entity_registry = er.async_get(self.hass)
        source_entity = entity_registry.async_get(entity_id)

        if source_entity is not None:
            if source_entity.icon is not None:
                return source_entity.icon

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
                return icons[source_entity.platform][source_entity.domain][
                    source_entity.translation_key
                ]["default"]

        return None

    # ------------------------------------------------------
    async def async_get_entity_info(
        self, entity_info: BaseEntityInfo
    ) -> BaseEntityInfo:
        """Get entity info."""
        state: State | None = self.hass.states.get(entity_info.entity_id)

        if state is not None:
            entity_info.friendly_name = state.attributes.get(ATTR_FRIENDLY_NAME, None)
            entity_info.device_class = get_device_class(
                self.hass, entity_info.entity_id
            )
            entity_info.unit_of_measurement = state.attributes.get(
                ATTR_UNIT_OF_MEASUREMENT, None
            )

            if entity_info.device_class is not None:
                return entity_info

            entity_info.icon = await self.async_get_icon(entity_info.entity_id)

        return entity_info
