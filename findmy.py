import logging
import toml
import struct
import time
import threading
import subprocess
import base64
import pwnagotchi.plugins as plugins

class FindMyWorker():
    def __init__(self):
        self.adv_interval = None
        self.adv_key = None
        self.__broadcasting_enabled = False
        self.__thread = threading.Thread(target = self.__broadcasting_thread, daemon = True)
    
    def startAdv(self):
        logging.info(f'[FindMy] Broadcasting BT advertisement packets every {self.adv_interval}s...')
        self.__broadcasting_enabled = True
        self.__thread.start()
    def stopAdv(self):
        self.__broadcasting_enabled = False
        self.__thread.join()
        logging.info('[FindMy] Stopped broadcasting BT advertisement packets')
    
    def __broadcasting_thread(self):
        while(self.__broadcasting_enabled):
            self.__advertise(self.adv_key, self.adv_interval * 1000)
            time.sleep(self.adv_interval)
    
    # This code is not mine, is taken from: https://github.com/seemoo-lab/openhaystack/tree/main/Firmware/Linux_HCI
    def __advertisement_template(self):
        adv = ''
        adv += '1e'  # length (30)
        adv += 'ff'  # manufacturer specific data
        adv += '4c00'  # company ID (Apple)
        adv += '1219'  # offline finding type and length
        adv += '00'  # state
        for _ in range(22):  # key[6:28]
            adv += '00'
        adv += '00'  # first two bits of key[0]
        adv += '00'  # hint
        return bytearray.fromhex(adv)


    def __bytes_to_strarray(self, bytes_, with_prefix = False):
        if with_prefix:
            return [hex(b) for b in bytes_]
        else:
            return [format(b, 'x') for b in bytes_]


    def __run_hci_cmd(self, cmd, hci = 'hci0', wait = 1):
        cmd_ = ['hcitool', '-i', hci, 'cmd']
        cmd_ += cmd
        subprocess.run(cmd_)
        if wait > 0:
            time.sleep(wait)


    def __advertise(self, key, interval_ms = 2000):
        addr = bytearray(key[:6])
        addr[0] |= 0b11000000

        adv = self.__advertisement_template()
        adv[7:29] = key[6:28]
        adv[29] = key[0] >> 6

        # Set BLE address
        self.__run_hci_cmd(['0x3f', '0x001'] + self.__bytes_to_strarray(addr, with_prefix=True)[::-1])
        subprocess.run(['systemctl', 'restart', 'bluetooth'])
        time.sleep(1)

        # Set BLE advertisement payload
        self.__run_hci_cmd(['0x08', '0x0008'] + [format(len(adv), 'x')] + self.__bytes_to_strarray(adv))

        # Set BLE advertising mode
        interval_enc = struct.pack('<h', interval_ms)
        hci_set_adv_params = ['0x08', '0x0006']
        hci_set_adv_params += self.__bytes_to_strarray(interval_enc)
        hci_set_adv_params += self.__bytes_to_strarray(interval_enc)
        hci_set_adv_params += ['03', '00', '00', '00', '00', '00', '00', '00', '00']
        hci_set_adv_params += ['07', '00']
        self.__run_hci_cmd(hci_set_adv_params)

        # Start BLE advertising
        self.__run_hci_cmd(['0x08', '0x000a'] + ['01'], wait = 0)

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
            self.__findmy_worker.adv_key = base64.b64decode(self.__adv_key.encode())
            self.__findmy_worker.startAdv()
        
    def on_unload(self, ui):
        self.__findmy_worker.stopAdv()
        logging.info('[FindMy] Plugin unloaded')

    def on_ui_setup(self, ui):
        pass

    def on_ui_update(self, ui):
        pass