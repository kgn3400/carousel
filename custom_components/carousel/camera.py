"""Carousel camera."""

from __future__ import annotations

from aiohttp import web

from homeassistant.components.camera import Camera  # CameraEntityFeature
from homeassistant.components.camera.const import StreamType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_carousel_entity import BaseCarouselEntity
from .base_entity_info import BaseEntityInfo
from .const import CONF_ENTITY_IDS, TRANSLATION_KEY


# ------------------------------------------------------
# ------------------------------------------------------
class CameraEntityInfo(BaseEntityInfo):
    """Camera Entity info class."""

    def __init__(
        self,
        entity_id: str,
        friendly_name: str | None = None,
        icon: str | None = None,
        unit_of_measurement: str | None = None,
        device_class: str | None = None,
    ) -> None:
        """Sensor entity info."""
        super().__init__(
            entity_id,
            friendly_name,
            icon,
            unit_of_measurement,
        )

        self.device_class: str | None = device_class
        self.entity_obj: Camera


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
        async_add_entities([CarouselCamera(hass, entry, entities)])


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class CarouselCamera(Camera, BaseCarouselEntity):
    """Camera carousel."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        entities: list[str],
    ) -> None:
        """Initialize the camera."""
        Camera.__init__(self)
        BaseCarouselEntity.__init__(self, hass, entry)

        self.entities_list: list[CameraEntityInfo] = [
            CameraEntityInfo(entity) for entity in entities
        ]

        self.current_entity: CameraEntityInfo = None

        self.translation_key = TRANSLATION_KEY

    # ------------------------------------------------------------------
    async def async_refresh(self) -> None:
        """Refresh."""

        await self.async_refresh_common()

        self.current_entity = self.entities_list[
            self.current_entity_pos
        ] = await self.async_get_entity_info(self.current_entity)

        if self.current_entity.entity_obj is not None:
            self._attr_supported_features = (
                self.current_entity.entity_obj._attr_supported_features
            )
            self._attr_should_poll = self.current_entity.entity_obj._attr_should_poll

        if self.async_write_ha_state is not None:
            self.async_write_ha_state()

    # ------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return True if entity is available."""

        if (
            self.current_entity is not None
            and self.current_entity.entity_obj is not None
        ):
            return self.current_entity.entity_obj.available

        return False

    # ------------------------------------------------------
    @property
    def frame_interval(self) -> float:
        """Return the interval between frames of the mjpeg stream."""

        if (
            self.current_entity is not None
            and self.current_entity.entity_obj is not None
        ):
            return self.current_entity.entity_obj.frame_interval

        return 0

    # ------------------------------------------------------
    @property
    def frontend_stream_type(self) -> StreamType | None:
        """Return the type of stream supported by this camera.

        A camera may have a single stream type which is used to inform the
        frontend which camera attributes and player to use. The default type
        is to use HLS, and components can override to change the type.
        """
        if (
            self.current_entity is not None
            and self.current_entity.entity_obj is not None
            and self.current_entity.entity_obj.frontend_stream_type is not None
        ):
            return self.current_entity.entity_obj.frontend_stream_type()

        return None

    # ------------------------------------------------------
    @property
    def model(self) -> str | None:
        """Return the camera model."""

        if (
            self.current_entity is not None
            and self.current_entity.entity_obj is not None
        ):
            return self.current_entity.entity_obj.model

        return None

    # ------------------------------------------------------
    @property
    def use_stream_for_stills(self) -> bool:
        """Whether or not to use stream to generate stills."""
        if (
            self.current_entity is not None
            and self.current_entity.entity_obj is not None
        ):
            return self.current_entity.entity_obj.use_stream_for_stills

        return False

    # ------------------------------------------------------
    # @property
    # def supported_features(self) -> CameraEntityFeature:
    #     """Flag supported features."""
    #     if (
    #         self.current_entity is not None
    #         and self.current_entity.entity_obj is not None
    #         and self.current_entity.entity_obj.supported_features is not None
    #     ):
    #         return self.current_entity.entity_obj.supported_features

    #     return None

    # ------------------------------------------------------
    def camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""

        if (
            self.current_entity is not None
            and self.current_entity.entity_obj is not None
            and self.current_entity.entity_obj.camera_image is not None
        ):
            return self.current_entity.entity_obj.camera_image(width, height)

        return None

    # ------------------------------------------------------
    async def stream_source(self) -> str | None:
        """Return the stream source."""

        if (
            self.current_entity is not None
            and self.current_entity.entity_obj is not None
            and self.current_entity.entity_obj.stream_source is not None
        ):
            return await self.current_entity.entity_obj.stream_source()

        return None

    # ------------------------------------------------------
    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Camera image."""

        if (
            self.current_entity is not None
            and self.current_entity.entity_obj is not None
            and self.current_entity.entity_obj.async_camera_image is not None
        ):
            return await self.current_entity.entity_obj.async_camera_image(
                width, height
            )

        return None

    # ------------------------------------------------------
    async def handle_async_mjpeg_stream(
        self, request: web.Request
    ) -> web.StreamResponse | None:
        """Mjpeg stream."""

        if (
            self.current_entity is not None
            and self.current_entity.entity_obj is not None
        ):
            return await self.current_entity.entity_obj.handle_async_mjpeg_stream(
                request
            )

        return None
