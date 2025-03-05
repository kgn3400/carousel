"""Config flow for carousel integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol

from homeassistant.const import CONF_ICON, CONF_NAME, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowError,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)
from homeassistant.helpers.selector import (
    BooleanSelector,
    IconSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TemplateSelector,
)

from .const import (
    CONF_ENTITY_IDS,
    CONF_LISTEN_TO_TIMER_TRIGGER,
    CONF_PLATFORM_TYPE,
    CONF_RESTART_TIMER,
    CONF_ROTATE_EVERY_MINUTES,
    CONF_SHOW_IF_TEMPLATE,
    DOMAIN,
    StepType,
)


async def _validate_input(
    hass: HomeAssistant, user_input: dict[str, Any], errors: dict[str, str]
) -> bool:
    """Validate the user input."""
    if CONF_ENTITY_IDS not in user_input:
        errors[CONF_ENTITY_IDS] = "missing_selection"
        return False

    if len(user_input[CONF_ENTITY_IDS]) == 0:
        errors[CONF_ENTITY_IDS] = "missing_selection"
        return False

    return True


# ------------------------------------------------------------------
async def _create_form(
    options: dict[str, Any] | None = None,
    step: StepType | None = None,
    domain: str = "",
) -> vol.Schema:
    """Create a form for step/option."""

    CONFIG_NAME = {
        vol.Required(
            CONF_NAME,
        ): selector.TextSelector(),
    }

    CONFIG_OPTIONS = {
        vol.Optional(
            CONF_ICON,
        ): IconSelector(),
        vol.Required(
            CONF_ROTATE_EVERY_MINUTES,
            default=1,
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
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(integration="timer", multiple=False),
        ),
        vol.Optional(
            CONF_RESTART_TIMER,
            default=False,
        ): BooleanSelector(),
    }

    CONFIG_OPTIONS_ENTITIES = {
        vol.Required(
            CONF_ENTITY_IDS,
            default=options.get(CONF_ENTITY_IDS, []),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=domain, multiple=True),
        ),
    }
    CONFIG_SHOW_IF_TEMPLATE = {
        vol.Optional(
            CONF_SHOW_IF_TEMPLATE,
        ): TemplateSelector(),
    }

    match step:
        case StepType.OPTIONS:
            match domain:
                case Platform.BINARY_SENSOR | Platform.SENSOR:
                    return vol.Schema(
                        {
                            **CONFIG_OPTIONS,
                            **CONFIG_SHOW_IF_TEMPLATE,
                            **CONFIG_OPTIONS_ENTITIES,
                        }
                    )
                case _:  # Camera
                    return vol.Schema({**CONFIG_OPTIONS, **CONFIG_OPTIONS_ENTITIES})

        case StepType.CONFIG | _:
            match domain:
                case Platform.BINARY_SENSOR | Platform.SENSOR:
                    return vol.Schema(
                        {
                            **CONFIG_NAME,
                            **CONFIG_OPTIONS,
                            **CONFIG_SHOW_IF_TEMPLATE,
                            **CONFIG_OPTIONS_ENTITIES,
                        }
                    )
                case _:  # Camera
                    return vol.Schema(
                        {**CONFIG_NAME, **CONFIG_OPTIONS, **CONFIG_OPTIONS_ENTITIES}
                    )


MENU_OPTIONS_TEST = [
    Platform.BINARY_SENSOR,
    Platform.CAMERA,
    Platform.SENSOR,
]

MENU_OPTIONS = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]


async def _validate_input(
    handler: SchemaCommonFlowHandler, user_input: dict[str, Any]
) -> dict[str, Any]:
    """Validate user input."""
    if CONF_ENTITY_IDS not in user_input:
        raise SchemaFlowError("missing_selection")

    if len(user_input[CONF_ENTITY_IDS]) == 0:
        raise SchemaFlowError("missing_selection")

    return user_input


# ------------------------------------------------------------------
async def choose_options_step(options: dict[str, Any]) -> str:
    """Return next step_id for options flow according to platform type."""
    return cast(str, options[CONF_PLATFORM_TYPE])


# ------------------------------------------------------------------
async def config_sensor_schema(handler: SchemaCommonFlowHandler) -> vol.Schema:
    """Return schema for the sensor config step."""
    handler.options[CONF_PLATFORM_TYPE] = Platform.SENSOR
    return await _create_form(
        handler.options,
        step=StepType.CONFIG,
        domain=Platform.SENSOR,
    )


# ------------------------------------------------------------------
async def config_binary_sensor_schema(handler: SchemaCommonFlowHandler) -> vol.Schema:
    """Return schema for the sensor config step."""
    handler.options[CONF_PLATFORM_TYPE] = Platform.BINARY_SENSOR
    return await _create_form(
        handler.options,
        step=StepType.CONFIG,
        domain=Platform.BINARY_SENSOR,
    )


# ------------------------------------------------------------------
async def config_camera_schema(handler: SchemaCommonFlowHandler) -> vol.Schema:
    """Return schema for the sensor config step."""
    handler.options[CONF_PLATFORM_TYPE] = Platform.CAMERA
    return await _create_form(
        handler.options,
        step=StepType.CONFIG,
        domain=Platform.CAMERA,
    )


# ------------------------------------------------------------------
async def options_sensor_schema(handler: SchemaCommonFlowHandler) -> vol.Schema:
    """Return schema for the sensor config step."""
    handler.options[CONF_PLATFORM_TYPE] = Platform.SENSOR
    return await _create_form(
        handler.options,
        step=StepType.OPTIONS,
        domain=Platform.SENSOR,
    )


# ------------------------------------------------------------------
async def options_binary_sensor_schema(handler: SchemaCommonFlowHandler) -> vol.Schema:
    """Return schema for the sensor config step."""
    handler.options[CONF_PLATFORM_TYPE] = Platform.BINARY_SENSOR
    return await _create_form(
        handler.options,
        step=StepType.OPTIONS,
        domain=Platform.BINARY_SENSOR,
    )


# ------------------------------------------------------------------
async def options_camera_schema(handler: SchemaCommonFlowHandler) -> vol.Schema:
    """Return schema for the sensor config step."""
    handler.options[CONF_PLATFORM_TYPE] = Platform.CAMERA
    return await _create_form(
        handler.options,
        step=StepType.OPTIONS,
        domain=Platform.CAMERA,
    )


CONFIG_FLOW = {
    "user": SchemaFlowMenuStep(MENU_OPTIONS),
    Platform.BINARY_SENSOR: SchemaFlowFormStep(
        config_binary_sensor_schema,
        validate_user_input=_validate_input,
    ),
    Platform.SENSOR: SchemaFlowFormStep(
        config_sensor_schema,
        validate_user_input=_validate_input,
    ),
}

CONFIG_FLOW_TEST = {
    "user": SchemaFlowMenuStep(MENU_OPTIONS_TEST),
    Platform.BINARY_SENSOR: SchemaFlowFormStep(
        config_binary_sensor_schema,
        validate_user_input=_validate_input,
    ),
    Platform.SENSOR: SchemaFlowFormStep(
        config_sensor_schema,
        validate_user_input=_validate_input,
    ),
    Platform.CAMERA: SchemaFlowFormStep(
        config_camera_schema,
        validate_user_input=_validate_input,
    ),
}


OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(next_step=choose_options_step),
    Platform.BINARY_SENSOR: SchemaFlowFormStep(
        options_binary_sensor_schema,
        validate_user_input=_validate_input,
    ),
    Platform.SENSOR: SchemaFlowFormStep(
        options_sensor_schema,
        validate_user_input=_validate_input,
    ),
    Platform.CAMERA: SchemaFlowFormStep(
        options_sensor_schema,
        validate_user_input=_validate_input,
    ),
}


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""

        return cast(str, options[CONF_NAME])

    # ------------------------------------------------------------------
    @callback
    def async_config_flow_finished(self, options: Mapping[str, Any]) -> None:
        """Take necessary actions after the config flow is finished, if needed.

        The options parameter contains config entry options, which is the union of user
        input from the config flow steps.
        """
