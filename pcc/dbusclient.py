import re
import subprocess
from pcc.logger import Logger

# Explore available dbus commands via (for example):
#   gdbus introspect --system --dest org.gnome.ShairportSync --object-path /org/gnome/ShairportSync
class DbusClient():

    __SPS_DBUS_CMD   =  "dbus-send --system --print-reply --type=method_call --dest=org.gnome.ShairportSync '/org/gnome/ShairportSync'"
    __BLUEZ_DBUS_CMD =  "dbus-send --system --print-reply --type=method_call --dest=org.bluez '/org/bluez/hci0'"

    def __init__(self):
        self.__logger = Logger().set_namespace(self.__class__.__name__)

    # vol should be in the range [-30, 0]
    def set_airplay_vol(self, vol, return_cmd = False, throw = False):
        # dbus-send --system --print-reply --type=method_call --dest=org.gnome.ShairportSync '/org/gnome/ShairportSync' org.gnome.ShairportSync.RemoteControl.SetAirplayVolume double:-29.99
        cmd = f"{self.__SPS_DBUS_CMD} org.gnome.ShairportSync.RemoteControl.SetAirplayVolume double:{vol}"
        if return_cmd:
            return cmd
        try:
            subprocess.check_output(cmd, shell = True, executable = '/bin/bash', stderr=subprocess.STDOUT).decode("utf-8")
        except Exception as e:
            self.__logger.warning(f'Unable to set airplay client volume: {e}')
            if throw:
                raise e

    def set_bluetooth_discoverable(self, discoverable, return_cmd = False, throw = False):
        if discoverable:
            discoverable_str = 'true'
        else:
            discoverable_str = 'false'

        # dbus-send --system --print-reply --type=method_call --dest=org.bluez /org/bluez/hci0 org.freedesktop.DBus.Properties.Set string:org.bluez.Adapter1 string:Discoverable variant:boolean:false
        cmd = f'{self.__BLUEZ_DBUS_CMD} org.freedesktop.DBus.Properties.Set string:org.bluez.Adapter1 string:Discoverable variant:boolean:{discoverable_str}'
        if return_cmd:
            return cmd
        try:
            subprocess.check_output(cmd, shell = True, executable = '/bin/bash', stderr=subprocess.STDOUT).decode("utf-8")
        except Exception as e:
            self.__logger.warning(f'Unable to set bluetooth discoverable: {e}')
            if throw:
                raise e

    def get_shairport_sync_client_name(self, return_cmd = False, throw = False):
        # dbus-send --print-reply --system --dest=org.gnome.ShairportSync /org/gnome/ShairportSync org.freedesktop.DBus.Properties.Get string:org.gnome.ShairportSync.RemoteControl string:ClientName
        cmd = f"{self.__SPS_DBUS_CMD} org.freedesktop.DBus.Properties.Get string:org.gnome.ShairportSync.RemoteControl string:ClientName"
        if return_cmd:
            return cmd
        try:
            res = subprocess.check_output(cmd, shell = True, executable = '/bin/bash', stderr=subprocess.STDOUT).decode("utf-8")
        except Exception as e:
            self.__logger.warning(f'Unable to get shairport-sync client name: {e}')
            if throw:
                raise e
            else:
                return None

        m = re.search(r"^\s+variant\s+string\s+(.*)", res)
        if m is None:
            self.__logger.warning('Unable to parse shairport-sync client name')
            if throw:
                raise Exception('Unable to parse shairport-sync client name')
            else:
                return None
        else:
            return m.group(1).strip('"')

    def get_shairport_sync_player_state(self, return_cmd = False, throw = False):
        # dbus-send --print-reply --system --dest=org.gnome.ShairportSync /org/gnome/ShairportSync org.freedesktop.DBus.Properties.Get string:org.gnome.ShairportSync.RemoteControl string:PlayerState
        cmd = f"{self.__SPS_DBUS_CMD} org.freedesktop.DBus.Properties.Get string:org.gnome.ShairportSync.RemoteControl string:PlayerState"
        if return_cmd:
            return cmd
        try:
            res = subprocess.check_output(cmd, shell = True, executable = '/bin/bash', stderr=subprocess.STDOUT).decode("utf-8")
        except Exception as e:
            self.__logger.warning(f'Unable to get shairport-sync client name: {e}')
            if throw:
                raise e
            else:
                return None

        m = re.search(r"^\s+variant\s+string\s+(.*)", res)
        if m is None:
            self.__logger.warning('Unable to parse shairport-sync player state')
            if throw:
                raise Exception('Unable to parse shairport-sync player state')
            else:
                return None
        else:
            return m.group(1).strip('"')
