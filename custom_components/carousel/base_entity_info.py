"""Base entity info class."""

# ------------------------------------------------------
# ------------------------------------------------------
from datetime import datetime, timedelta

from homeassistant.core import State
from homeassistant.helpers.entity import Entity


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
