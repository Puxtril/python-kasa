import logging

from ...feature import Feature
from ...module import Module
from ...exceptions import KasaException
from ..iotmodule import IotModule, merge

_LOGGER = logging.getLogger(__name__)

class VideoControl(IotModule):

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                device=self._device,
                container=self,
                id="videocontrol",
                name="Video Control",
                icon="mdi:motion-sensor",
                attribute_getter="video_resolution",
                attribute_setter="set_video_resolution",
                choices_getter="video_resolutions",
                category=Feature.Category.Config,
                type=Feature.Type.Choice,
            )
        )

    @property
    def enabled(self) -> bool:
        return True

    def query(self) -> dict:
        return self.query_for_command("get_resolution")
    
    @property
    def resolution(self) -> str:
        try:
            return self.data.get("get_resolution").get("value")[0]["resolution"]
        except Exception as ex:
            _LOGGER.error("Unexpected error getting resolution: %s", str(ex))
        return ""

    @property
    def video_resolutions(self) -> list[str]:
        return ["360P", "720P", "1080P"]

    @property
    def video_resolution(self) -> str:
        return self.resolution
    
    async def set_video_resolution(self, resolution: str) -> dict:
        if resolution not in self.video_resolutions:
            raise ValueError(
                f"Resolution must be one of {', '.join(self.video_resolutions)}: {resolution}"
            )
        return await self.call("set_resolution", {"value":[{"channel": 1, "resolution": resolution}]})
