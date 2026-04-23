"""ADB-only device factory."""


class DeviceFactory:
    """Provide Android device helpers through the ADB backend."""

    def __init__(self) -> None:
        self._module = None

    @property
    def module(self):
        if self._module is None:
            from phone_agent import adb

            self._module = adb
        return self._module

    def get_screenshot(self, device_id: str | None = None, timeout: int = 10):
        return self.module.get_screenshot(device_id, timeout)

    def get_current_app(self, device_id: str | None = None) -> str:
        return self.module.get_current_app(device_id)

    def tap(
        self, x: int, y: int, device_id: str | None = None, delay: float | None = None
    ):
        return self.module.tap(x, y, device_id, delay)

    def double_tap(
        self, x: int, y: int, device_id: str | None = None, delay: float | None = None
    ):
        return self.module.double_tap(x, y, device_id, delay)

    def long_press(
        self,
        x: int,
        y: int,
        duration_ms: int = 3000,
        device_id: str | None = None,
        delay: float | None = None,
    ):
        return self.module.long_press(x, y, duration_ms, device_id, delay)

    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration_ms: int | None = None,
        device_id: str | None = None,
        delay: float | None = None,
    ):
        return self.module.swipe(
            start_x, start_y, end_x, end_y, duration_ms, device_id, delay
        )

    def back(self, device_id: str | None = None, delay: float | None = None):
        return self.module.back(device_id, delay)

    def home(self, device_id: str | None = None, delay: float | None = None):
        return self.module.home(device_id, delay)

    def launch_app(
        self, app_name: str, device_id: str | None = None, delay: float | None = None
    ) -> bool:
        return self.module.launch_app(app_name, device_id, delay)

    def type_text(self, text: str, device_id: str | None = None):
        return self.module.type_text(text, device_id)

    def clear_text(self, device_id: str | None = None):
        return self.module.clear_text(device_id)

    def detect_and_set_adb_keyboard(self, device_id: str | None = None) -> str:
        return self.module.detect_and_set_adb_keyboard(device_id)

    def restore_keyboard(self, ime: str, device_id: str | None = None):
        return self.module.restore_keyboard(ime, device_id)

    def list_devices(self):
        return self.module.list_devices()

    def get_connection_class(self):
        from phone_agent.adb import ADBConnection

        return ADBConnection


_DEVICE_FACTORY = DeviceFactory()


def get_device_factory() -> DeviceFactory:
    """Return the singleton Android device factory."""

    return _DEVICE_FACTORY
