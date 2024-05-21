"""Config flow for carousel integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_ICON, CONF_NAME, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.selector import (
    BooleanSelector,
    IconSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_ENTITY_IDS,
    CONF_LISTEN_TO_TIMER_TRIGGER,
    CONF_PLATFORM_TYPE,
    CONF_RESTART_TIMER,
    CONF_ROTATE_EVERY_MINUTES,
    DOMAIN,
    LOGGER,
)

#  from homeassistant import config_entries
from .fix_entity_selector import EntitySelector, EntitySelectorConfig


async def _validate_input(
    hass: HomeAssistant, user_input: dict[str, Any], errors: dict[str, str]
) -> bool:
    """Validate the user input allows us to connect."""

    return True


# ------------------------------------------------------------------
async def _validate_input_init(
    options_flow_handler: OptionsFlowHandler,
    user_input: dict[str, Any],
    errors: dict[str, str],
) -> bool:
    """Validate the user input allows us to connect."""

    return True


# ------------------------------------------------------------------
async def _create_form(
    hass: HomeAssistant,
    user_input: dict[str, Any] | None = None,
    step: str = "",
    domain: str = "",
) -> vol.Schema:
    """Create a form for step/option."""

    if user_input is None:
        user_input = {}

    CONFIG_NAME = {
        vol.Required(CONF_NAME): selector.TextSelector(),
    }

    CONFIG_OPTIONS = {
        vol.Optional(
            CONF_ICON,
            default=user_input.get(CONF_ICON, ""),
        ): IconSelector(),
        vol.Required(
            CONF_ROTATE_EVERY_MINUTES,
            default=user_input.get(CONF_ROTATE_EVERY_MINUTES, 1),
        ): NumberSelector(
            NumberSelectorConfig(
                min=0.25,
                max=999,
                step="any",
                mode=NumberSelectorMode.BOX,
                unit_of_measurement="minutes",
            )
        ),
        vol.Optional(
            CONF_LISTEN_TO_TIMER_TRIGGER,
            default=user_input.get(CONF_LISTEN_TO_TIMER_TRIGGER, ""),
        ): EntitySelector(
            EntitySelectorConfig(integration="timer", multiple=False),
        ),
        vol.Optional(
            CONF_RESTART_TIMER,
            default=user_input.get(CONF_RESTART_TIMER, False),
        ): BooleanSelector(),
    }

    CONFIG_OPTIONS_ENTITIES = {
        vol.Required(
            CONF_ENTITY_IDS,
            default=user_input.get(CONF_ENTITY_IDS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=domain, multiple=True),
        ),
    }

    match step:
        case "init":
            return vol.Schema({**CONFIG_OPTIONS, **CONFIG_OPTIONS_ENTITIES})

        case "user" | _:
            return vol.Schema(
                {**CONFIG_NAME, **CONFIG_OPTIONS, **CONFIG_OPTIONS_ENTITIES}
            )


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class ConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1
    tmp_user_input: dict[str, Any] | None

    # ------------------------------------------------------------------
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        return self.async_show_menu(
            step_id="user",
            menu_options=[Platform.BINARY_SENSOR, Platform.CAMERA, Platform.SENSOR],
        )

    # ------------------------------------------------------------------
    async def async_step_user_x(
        self,
        user_input: dict[str, Any] | None = None,
        domain: str = "",
    ) -> FlowResult:
        """Handle the initial x step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                if await _validate_input(self.hass, user_input, errors):
                    user_input[CONF_PLATFORM_TYPE] = domain

                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=user_input,
                        options=user_input,
                    )

            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id=domain,
            data_schema=await _create_form(self.hass, user_input, "user", domain),
            errors=errors,
            last_step=True,
        )

    # ------------------------------------------------------------------
    async def async_step_sensor(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial sensor step."""

        return await self.async_step_user_x(user_input, Platform.SENSOR)

    # ------------------------------------------------------------------
    async def async_step_binary_sensor(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial binary_sensor step."""

        return await self.async_step_user_x(user_input, Platform.BINARY_SENSOR)

    # ------------------------------------------------------------------
    async def async_step_camera(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial camera step."""

        return await self.async_step_user_x(user_input, Platform.CAMERA)

    # ------------------------------------------------------------------
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Get the options flow."""
        return OptionsFlowHandler(config_entry)


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class OptionsFlowHandler(OptionsFlow):
    """Handle options flow."""

    def __init__(
        self,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize options flow."""

        self.config_entry = config_entry

        self._options: dict[str, Any] = self.config_entry.options.copy()

    # ------------------------------------------------------------------
    async def async_step_init_x(
        self,
        user_input: dict[str, Any] | None = None,
        domain: str = "",
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                if await _validate_input_init(self, user_input, errors):
                    tmp_input = self._options | user_input

                    return self.async_create_entry(
                        data=tmp_input,
                    )
            except Exception:
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
        else:
            user_input = self._options.copy()

        return self.async_show_form(
            step_id="init_" + domain,
            data_schema=await _create_form(
                self.hass,
                user_input,
                "init",
                domain,
            ),
            errors=errors,
            last_step=True,
        )

    # ------------------------------------------------------------------
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        # if user_input is None:
        #     user_input = self._options.copy()

        match self._options[CONF_PLATFORM_TYPE]:
            case Platform.BINARY_SENSOR:
                return await self.async_step_init_binary_sensor(user_input)

            case Platform.CAMERA:
                return await self.async_step_init_camera(user_input)

            case Platform.SENSOR:
                return await self.async_step_init_sensor(user_input)

            case _:
                pass

    # ------------------------------------------------------------------
    async def async_step_init_binary_sensor(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial binary_sensor step."""

        return await self.async_step_init_x(user_input, Platform.BINARY_SENSOR)

    #
    # ------------------------------------------------------------------
    async def async_step_init_camera(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial camera step."""

        return await self.async_step_init_x(user_input, Platform.CAMERA)

    # ------------------------------------------------------------------
    async def async_step_init_sensor(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial sensor step."""

        return await self.async_step_init_x(user_input, Platform.SENSOR)

    # ------------------------------------------------------------------
    # async def async_step_init(
    #     self, user_input: dict[str, Any] | None = None
    # ) -> FlowResult:
    #     """Handle the initial step."""
    #     errors: dict[str, str] = {}

    #     if user_input is not None:
    #         try:
    #             if await _validate_input_init(self, user_input, errors):
    #                 tmp_input = self._options | user_input

    #                 return self.async_create_entry(
    #                     data=tmp_input,
    #                 )
    #         except Exception:  # pylint: disable=broad-except
    #             LOGGER.exception("Unexpected exception")
    #             errors["base"] = "unknown"
    #     else:
    #         user_input = self._options.copy()

    #     return self.async_show_form(
    #         step_id="init",
    #         data_schema=await _create_form(
    #             self.hass,
    #             user_input,
    #             "init",
    #             user_input[CONF_PLATFORM_TYPE],
    #         ),
    #         errors=errors,
    #         last_step=True,
    #     )
