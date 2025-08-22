from enum import Enum
import logging

from ...feature import Feature
from ..iotmodule import IotModule

_LOGGER = logging.getLogger(__name__)


class SdStatus(Enum):
    """SD Card status"""

    Ok = "ok",
    NoSdCard = "no sdcard",
    FormatNotSupported = "file system not support",
    NoPartition = "no partition",
    ReadOnly = "read only",
    InsufficientSpace = "insufficient space",
    MultiplePartitions = "multi-partitions",
    Unmounted = "unmount",
    IOError = "io error",
    CapacityNotSupported = "capacity not support",
    Formatting = "formatting"


class SDCard(IotModule):
    
    def _initialize_features(self) -> None:

        self._add_feature(
            Feature(
                self._device,
                id="sd_status",
                name="SDCard Status",
                container=self,
                attribute_getter="status",
                type=Feature.Type.Sensor
            )
        )

        if (
            self.status == SdStatus.Ok.value[0] or
            self.status == SdStatus.FormatNotSupported.value[0] or
            self.status == SdStatus.NoPartition.value[0] or
            self.status == SdStatus.MultiplePartitions.value[0]
        ):
            self._add_feature(
                Feature(
                    self._device,
                    id="sd_format",
                    name="SDCard Format (Wipe)",
                    container=self,
                    attribute_setter="format",
                    type=Feature.Type.Action,
                )
            )

        if self.status == SdStatus.Ok.value[0]:
            self._add_feature(
                Feature(
                    self._device,
                    id="sd_capacity",
                    name="SDCard Capacity",
                    container=self,
                    attribute_getter="get_size_free",
                    type=Feature.Type.Sensor
                )
            )
            self._add_feature(
                Feature(
                    self._device,
                    id="sd_used",
                    name="SDCard Used Space",
                    container=self,
                    attribute_getter="get_size_used",
                    type=Feature.Type.Sensor
                )
            )
            self._add_feature(
                Feature(
                    self._device,
                    id="sd_free",
                    name="SDCard Free Space",
                    container=self,
                    attribute_getter="get_size_free",
                    type=Feature.Type.Sensor
                )
            )

    @property
    def enabled(self) -> bool:
        return True
    
    def query(self) -> dict:
        return self.query_for_command("get_sd_card_state")
    
    @property
    def status(self) -> str | None:
        return self.data.get("get_sd_card_state").get("state")
    
    @property
    def get_size_capacity(self) -> str | None:
        """Technically there is another property `sd_capacity`, but it doesn't include reserved space.
        To make it clearer to uses how much space is available for *their* use, this value is used instead.
        """
        return self.data.get("get_sd_card_state").get("total")

    @property
    def get_size_used(self) -> str | None:
        return self.data.get("get_sd_card_state").get("used")

    @property
    def get_size_free(self) -> str | None:
        return self.data.get("get_sd_card_state").get("free")
    
    async def format(self) -> dict:
        """Re-format the SD Card"""
        return await self.call("set_format_sd_card")