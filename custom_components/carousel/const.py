"""Constants for Carousel integration."""

from enum import Enum
from logging import Logger, getLogger

DOMAIN = "carousel"
DOMAIN_NAME = "Carousel"
LOGGER: Logger = getLogger(__name__)

TRANSLATION_KEY = DOMAIN
TRANSLATION_KEY_MISSING_ENTITY = "missing_entity"
TRANSLATION_KEY_MISSING__TIMER_ENTITY = "missing_timer_entity"
TRANSLATION_KEY_TEMPLATE_ERROR = "template_error"

CONF_ENTITY_IDS = "entity_ids"
CONF_ROTATE_EVERY_MINUTES = "rotate_every_minutes"
CONF_PLATFORM_TYPE = "platform_type"
CONF_RESTART_TIMER = "restart_timer"
CONF_LISTEN_TO_TIMER_TRIGGER = "listen_to_timer_trigger"
CONF_SHOW_IF_TEMPLATE = "show_if_template"

SERVICE_SHOW_ENTITY_ID = "show_entity_id"
SERVICE_REMOVE_ENTITY_ID = "remove_entity_id"
SERVICE_ADD_ENTITY_ID = "add_entity_id"
SERVICE_SHOW_X_TIMES = "show_x_times"
SERVICE_SHOW_FOR = "show_for"

EVENT_STARTING_OVER = "starting_over"


class RefreshType(Enum):
    """Refresh type."""

    NORMAL = 1
    LISTEN_TO_TIMER_TRIGGER = 2
