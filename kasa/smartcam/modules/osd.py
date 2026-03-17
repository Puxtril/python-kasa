"""Implementation of on-screen display module."""

from __future__ import annotations

import logging

from ...feature import Feature
from ..smartcammodule import SmartCamModule

_LOGGER = logging.getLogger(__name__)


class OSD(SmartCamModule):
    """Implementation of on-screen display module."""

    REQUIRED_COMPONENT = "osd"

    QUERY_GETTER_NAME = "getOsd"
    QUERY_MODULE_NAME = "OSD"
    QUERY_SECTION_NAMES = "logo"

    def _initialize_features(self) -> None:
        """Initialize features."""
        device = self._device
        self._add_feature(
            Feature(
                device=device,
                container=self,
                name="OSD Logo",
                id="osd_logo",
                attribute_getter="logo",
                attribute_setter="set_logo",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )
        self._add_feature(
            Feature(
                device=device,
                container=self,
                name="OSD Time",
                id="osd_time",
                attribute_getter="time",
                attribute_setter="set_time",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )

    def query(self) -> dict:
        """Query to execute during the update cycle."""
        section_names = {
            "name": [
                "logo",
                "date",
                "week",
                "font",
            ]
        }
        return {self.QUERY_GETTER_NAME: {self.QUERY_MODULE_NAME: section_names}}

    @property
    def logo(self) -> bool:
        """Return the OSD logo state."""
        return self.data["logo"]["enabled"] == "on"

    async def set_logo(self, enable: bool) -> dict:
        """Set the OSD logo state."""
        params = {
            "enabled": "on" if enable else "off",
            "x_coor": "0",
            "y_coor": "9150",
        }
        return await self._device._query_setter_helper(
            "setOsd", self.QUERY_MODULE_NAME, "logo", params
        )

    @property
    def time(self) -> bool:
        """Return the OSD time state."""
        return self.data["date"]["enabled"] == "on"

    async def set_time(self, enable: bool) -> dict:
        """Set the OSD time state."""
        params = {
            "enabled": "on" if enable else "off",
            "x_coor": "0",
            "y_coor": "0",
        }
        return await self._device._query_setter_helper(
            "setOsd", self.QUERY_MODULE_NAME, "date", params
        )
