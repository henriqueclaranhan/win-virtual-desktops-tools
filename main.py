import multiprocessing
from src.core.app_context import AppContext
from src.ui.listeners.mouse_listener import MouseListenerController
from src.ui.tray.tray_app import TrayApp


def main() -> None:
    multiprocessing.freeze_support()

    ctx = AppContext()
    ctx.start_background_workers()

    mouse_listener = MouseListenerController(ctx)
    mouse_listener.start()

    tray = TrayApp(app_context=ctx, mouse_listener=mouse_listener)
    tray.start()


if __name__ == "__main__":
    main()
