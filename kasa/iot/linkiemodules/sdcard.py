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
                    id="sd_storage",
                    name="SDCard Used",
                    container=self,
                    attribute_getter="size_desc",
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
    def size_desc(self) -> str | None:
        return f"{self.used} / {self.capacity}"
        
    
    @property
    def capacity(self) -> str | None:
        """Technically there is another property `sd_capacity`, but it doesn't include reserved space.
        To make it clearer how much space is available for *user* use, this value is returned.
        """
        return self.data.get("get_sd_card_state").get("total")

    @property
    def used(self) -> str | None:
        return self.data.get("get_sd_card_state").get("used")

    """
    File "/home/___/Documents/Programming/python-kasa/.venv/lib/python3.13/site-packages/asyncclick/core.py", line 824, in invoke
        rv = await rv
            ^^^^^^^^
    File "/home/___/Documents/Programming/python-kasa/kasa/cli/feature.py", line 128, in feature
        echo(response)
        ~~~~^^^^^^^^^^
    File "/home/___/Documents/Programming/python-kasa/kasa/cli/common.py", line 55, in echo
        _echo(*args, **kwargs)
        ~~~~~^^^^^^^^^^^^^^^^^
    File "/home/___/Documents/Programming/python-kasa/kasa/cli/common.py", line 43, in wrapper
        message = rich_formatting.sub("", message)
    TypeError: expected string or bytes-like object, got 'dict'
    """
    async def format(self) -> dict:
        """Re-format the SD Card"""
        return await self.call("set_format_sd_card")