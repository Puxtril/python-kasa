import logging

from ...feature import Feature
from ..iotmodule import IotModule

_LOGGER = logging.getLogger(__name__)

class NightVision(IotModule):
    """Control the camera's Night Vision mode"""

    def _initialize_features(self) -> None:
        self._add_feature(
            Feature(
                device=self._device,
                container=self,
                id="nightmode",
                name="Camera Night Mode",
                attribute_getter="night_mode",
                attribute_setter="set_night_mode",
                choices_getter="night_modes",
                category=Feature.Category.Config,
                type=Feature.Type.Choice,
            )
        )

    @property
    def enabled(self) -> bool:
        return True

    def query(self) -> dict:
        return self.query_for_command("get_mode")

    @property
    def mode(self) -> str:
        return self.data.get("get_mode").get("value")

    @property
    def night_modes(self) -> list[str]:
        return ["day", "night", "auto"]

    @property
    def night_mode(self) -> str:
        return self.mode
    
    async def set_night_mode(self, mode: str) -> dict:
        if mode not in self.night_modes:
            raise ValueError(
                f"Night mode must be one of {', '.join(self.night_modes)}: {mode}"
            )
        return await self.call("set_mode", {"value": mode})