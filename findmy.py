import logging
import toml
import pwnagotchi.plugins as plugins

class FindMyWorker():
    def __init__(self):
        self.adv_interval = None
        self.adv_key = None
    def startAdv(self):
        logging.info(f'[FindMy] Broadcasting BT advertisement packets every {self.adv_interval}s...')
    def stopAdv(self):
        logging.info('[FindMy] Stopped broadcast BT advertisement packets')

class FindMyPlugin(plugins.Plugin):
    __author__ = 'CyberArtemio'
    __version__ = '1.0'
    __license__ = 'GPL3'
    __description__ = 'FindMy is a Pwnagotchi plugin that lets you locate your Pwnagotchi via Apple FindMy network using openhaystack'

    # Default file path where keys for FindMy are stored. Used if user hasn't specified a different path
    DEFAULT_KEYS_PATH = '/root/findmy_config.toml'

    def __load_keys(self):
        logging.info(f'[FindMy] Loading keys from {self.__keys_path}')
        try:
            with open(self.__keys_path, 'r') as keys_file:
                keys = toml.load(keys_file)
                self.__tag_type = keys['type']
                self.__adv_interval = keys['interval']
                self.__adv_key = keys['adv_key']
            self.__ready = True
            logging.info(f'[FindMy] Keys loaded succesfully! Tag type: {self.__tag_type} - Adv interval: {self.__adv_interval}s - Adv key: {self.__adv_key}')
        except Exception as e:
            logging.critical(f'[FindMy] Failed loading keys: {e}')

    def on_loaded(self):
        self.__ready = False
        logging.info('[FindMy] Plugin loaded')
        try:
            self.__keys_path = self.options['keys']
        except:
            self.__keys_path = self.DEFAULT_KEYS_PATH
        
        self.__load_keys() # TODO: check if file exists or not (for future web ui config process)
        self.__findmy_worker = FindMyWorker()

        if(self.__ready):
            self.__findmy_worker.adv_interval = self.__adv_interval
            self.__findmy_worker.adv_key = self.__adv_key
            self.__findmy_worker.startAdv()
        
    def on_unload(self, ui):
        self.__findmy_worker.stopAdv()
        logging.info('[FindMy] Plugin unloaded')

    def on_ui_setup(self, ui):
        pass

    def on_ui_update(self, ui):
        pass