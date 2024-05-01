"""Fix entity selctor."""

from __future__ import annotations

from typing import Any, cast

import voluptuous as vol

#  from homeassistant import config_entries
from homeassistant.core import split_entity_id, valid_entity_id
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    ENTITY_FILTER_SELECTOR_CONFIG_SCHEMA,
    SELECTORS,
    EntityFilterSelectorConfig,
    Selector,
)


# ------------------------------------------------------------------
# ------------------------------------------------------------------
# ------------------------------------------------------------------
class EntitySelectorConfig(EntityFilterSelectorConfig, total=False):
    """Class to represent an entity selector config."""

    exclude_entities: list[str]
    include_entities: list[str]
    multiple: bool
    filter: EntityFilterSelectorConfig | list[EntityFilterSelectorConfig]


@SELECTORS.register("entity")
class EntitySelector(Selector[EntitySelectorConfig]):
    """Selector of a single or list of entities."""

    selector_type = "entity"

    CONFIG_SCHEMA = ENTITY_FILTER_SELECTOR_CONFIG_SCHEMA.extend(
        {
            vol.Optional("exclude_entities"): [str],
            vol.Optional("include_entities"): [str],
            vol.Optional("multiple", default=False): cv.boolean,
            vol.Optional("filter"): vol.All(
                cv.ensure_list,
                [ENTITY_FILTER_SELECTOR_CONFIG_SCHEMA],
            ),
        }
    )

    def __init__(self, config: EntitySelectorConfig | None = None) -> None:
        """Instantiate a selector."""
        super().__init__(config)

    def __call__(self, data: Any) -> str | list[str]:
        """Validate the passed selection."""

        include_entities = self.config.get("include_entities")
        exclude_entities = self.config.get("exclude_entities")

        def validate(e_or_u: str) -> str:
            e_or_u = e_or_u.strip()

            if e_or_u:
                e_or_u = cv.entity_id_or_uuid(e_or_u)
                if not valid_entity_id(e_or_u):
                    return e_or_u
                if allowed_domains := cv.ensure_list(self.config.get("domain")):
                    domain = split_entity_id(e_or_u)[0]
                    if domain not in allowed_domains:
                        raise vol.Invalid(
                            f"Entity {e_or_u} belongs to domain {domain}, "
                            f"expected {allowed_domains}"
                        )
                if include_entities:
                    vol.In(include_entities)(e_or_u)
                if exclude_entities:
                    vol.NotIn(exclude_entities)(e_or_u)
            return e_or_u

        if not self.config["multiple"]:
            return validate(data)
        if not isinstance(data, list):
            raise vol.Invalid("Value should be a list")
        return cast(list, vol.Schema([validate])(data))  # Output is a list


# ------------------------------------------------------------------
# ------------------------------------------------------------------
# ------------------------------------------------------------------
# ------------------------------------------------------------------
