"""Module for cameras."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, tzinfo

from ..device_type import DeviceType
from ..deviceconfig import DeviceConfig
from ..protocols import BaseProtocol
from ..device import WifiNetwork
from .iotdevice import IotDevice, KasaException
from ..module import Module
from .linkiemodules import VideoControl, SDCard, NightVision, StreamToggle

_LOGGER = logging.getLogger(__name__)


class IotCamera(IotDevice):
    """Representation of a TP-Link Camera."""

    # Enumerations
    key_types = ["NONE", "WEP", "WPA_PSK", "WPA2_PSK", "WEP64", "WEP128", "WPA_AUTO", "WPA3"]
    cipher_types = ["NONE", "TKIP", "AES", "AUTO", "CCMP"]

    valid_daynight_modes = ["day", "night", "auto"]

    def __init__(
        self,
        host: str,
        *,
        config: DeviceConfig | None = None,
        protocol: BaseProtocol | None = None,
    ) -> None:
        super().__init__(host=host, config=config, protocol=protocol)
        self._device_type = DeviceType.Camera

    async def _initialize_modules(self) -> None:
        """Initialize modules."""
        await super()._initialize_modules()
        self.add_module(Module.LinkieVideoControl, VideoControl(self, "smartlife.cam.ipcamera.videoControl"))
        self.add_module(Module.LinkieSDCard, SDCard(self, "smartlife.cam.ipcamera.sdCard"))
        self.add_module(Module.LinkieStreamToggle, StreamToggle(self, "smartlife.cam.ipcamera.switch"))
        self.add_module(Module.LinkieNightVision, NightVision(self, "smartlife.cam.ipcamera.dayNight"))

    @property
    def time(self) -> datetime:
        """Get the camera's time."""
        return datetime.fromtimestamp(self.sys_info["system_time"])

    @property
    def timezone(self) -> tzinfo:
        """Get the camera's timezone."""
        return None  # type: ignore

    @property  # type: ignore
    def is_on(self) -> bool:
        """Return whether device is on."""
        return True

    async def set_alias(self, alias: str) -> dict:
        await self._query_helper("smartlife.cam.ipcamera.system", "set_alias", {"value":alias})

    async def reboot(self, delay: int = 1) -> None:
        await self._query_helper("smartlife.cam.ipcamera.system", "set_reboot", {"delay":delay})

    async def wifi_scan(self) -> list[WifiNetwork]:
        response = await self._query_helper("smartlife.cam.ipcamera.wireless", "get_ap_list", {"scan":True,"scan_type":"fast"})

        if "ap_info" not in response:
            raise KasaException(f"Invalid response for wifi scan: {response}")

        network_objs = []
        for net in response["ap_info"]:
            
            key_type_int = -1 # For debugging
            try:
                key_type_int = self.key_types.index(net.get("wpa_mode"))
            except ValueError:
                pass

            network = WifiNetwork(
                ssid=net.get("ssid"),
                key_type=key_type_int,
                bssid=net.get("bssid"),
                channel=net.get("channel"),
                rssi=net.get("rssi"),
            )
            network_objs.append(network)
        return network_objs

    async def wifi_join(self, ssid: str, password: str, keytype: str = "6") -> dict:  # noqa: D202
        # Should be {"smartlife.cam.ipcamera.wireless":{"set_uplink":{"err_code":0}}}
        # But often it just returns {}
        await self._query_helper("smartlife.cam.ipcamera.wireless", "set_uplink", {"encryption":"AUTO", "passphrase":password,"ssid":ssid,"wpa_mode":self.key_types[int(keytype)]})
