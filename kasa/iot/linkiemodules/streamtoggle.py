from ...feature import Feature
from ..iotmodule import IotModule

class StreamToggle(IotModule):

    def _initialize_features(self) -> None:
        self._add_feature(
            Feature(
                self._device,
                container=self,
                id="stream_toggle",
                name="Video Stream",
                attribute_getter="get_enabled",
                attribute_setter="set_enabled",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )

    @property
    def enabled(self) -> bool:
        return True

    def query(self) -> dict:
        return self.query_for_command("get_is_enable")

    @property
    def get_enabled(self) -> bool:
        """Return current led status."""
        if self.data.get("value") == "on":
            return True
        return False

    async def set_enabled(self, enable: bool) -> dict:
        """Set led."""
        send_val = "on" if enable else "off"
        self.call("set_is_enable", {"value": send_val})