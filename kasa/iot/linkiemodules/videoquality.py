import logging

from ...feature import Feature
from ..iotmodule import IotModule

_LOGGER = logging.getLogger(__name__)

class VideoQuality(IotModule):

    def _initialize_features(self) -> None:
        """Initialize features after the initial update."""
        self._add_feature(
            Feature(
                device=self._device,
                container=self,
                id="videoresolution",
                name="Video Resolution",
                attribute_getter="video_resolution",
                attribute_setter="set_video_resolution",
                choices_getter="video_resolutions",
                category=Feature.Category.Config,
                type=Feature.Type.Choice,
            )
        )
        self._add_feature(
            Feature(
                device=self._device,
                container=self,
                id="videobitrate",
                name="Video Birate",
                attribute_getter="video_bitrate",
                attribute_setter="set_video_bitrate",
                choices_getter="video_bitrates",
                category=Feature.Category.Config,
                type=Feature.Type.Choice,
            )
        )

    @property
    def enabled(self) -> bool:
        return True

    def query(self) -> dict:
        return self.query_for_command("get_channel_quality")
    
    @property
    def resolution(self) -> str:
        return self._device.sys_info.get('resolution')

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
    
    @property
    def bitrate(self) -> str:
        return self.data.get('get_channel_quality').get("value")[0].get("quality")

    @property
    def video_bitrates(self) -> list[str]:
        return ["low", "medium", "high"]

    @property
    def video_bitrate(self) -> str:
        return self.bitrate
    
    async def set_video_bitrate(self, bitrate: str) -> dict:
        if bitrate not in self.video_bitrates:
            raise ValueError(
                f"bitrate must be one of {', '.join(self.video_bitrates)}: {bitrate}"
            )
        return await self.call("set_channel_quality", {"value":[{"channel": 1, "quality": bitrate}]})
