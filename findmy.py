import logging
import pwnagotchi.plugins as plugins

class FindMyPlugin(plugins.Plugin):
    __author__ = 'CyberArtemio'
    __version__ = '1.0'
    __license__ = 'GPL3'
    __description__ = 'FindMy is a Pwnagotchi plugin that lets you locate your Pwnagotchi via Apple FindMy network using openhaystack '

    def on_loaded(self):
        logging.info("[FindMy] Plugin loaded")

    def on_unload(self, ui):
        pass

    def on_ui_setup(self, ui):
        pass
    def on_ui_update(self, ui):
        pass