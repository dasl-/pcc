import re
import subprocess
from pcc.logger import Logger

# Explore available dbus commands via (for example):
#   gdbus introspect --system --dest org.gnome.ShairportSync --object-path /org/gnome/ShairportSync
#
# See also: https://github.com/mikebrady/shairport-sync/blob/master/documents/sample%20dbus%20commands
class DbusClient():

    __SPS_DBUS_CMD   =  "dbus-send --system --print-reply=literal --type=method_call --dest=org.gnome.ShairportSync '/org/gnome/ShairportSync'"
    __BLUEZ_DBUS_CMD =  "dbus-send --system --print-reply=literal --type=method_call --dest=org.bluez '/org/bluez/hci0'"

    def __init__(self):
        self.__logger = Logger().set_namespace(self.__class__.__name__)

    # vol: should be in the range [-30, 0]
    #
    # Notes on the 'org.gnome.ShairportSync.RemoteControl.SetAirplayVolume' API:
    # * Controls iOS client properly
    # * Doesn't control macOS client in systemwide airplay mode
    # * When iOS client is connected to multiple servers (multiroom), when the client receives a
    #   volume change message from a given server, the client attempts to maintain relative
    #   volume levels across servers. So the client will then adjust the volume of all other
    #   servers it is connected to. And this implementation is buggy / wacky, so sometimes
    #   unexpected adjustments occur.
    #
    # Notes on AdvancedRemoteControl API ('org.gnome.ShairportSync.AdvancedRemoteControl.SetVolume'):
    # * The advanced remote control API might be able to adjust the volume of just one server when a
    #   client is connected to multiple servers (multiroom)
    # * But the advanced remote control API is not well supported. My iphone doesn't seem to support it, nor does
    #   my macOS laptop when connected in systemwide airplay mode, nor does my macOS laptop when connected via
    #   Music app.
    # * % dbus-send --print-reply --system --dest=org.gnome.ShairportSync /org/gnome/ShairportSync org.freedesktop.DBus.Properties.Get string:org.gnome.ShairportSync.AdvancedRemoteControl string:Available
    #      method return time=1688884569.765822 sender=:1.4963 -> destination=:1.6096 serial=1231 reply_serial=2
    #      variant       boolean false
    # * See https://github.com/mikebrady/shairport-sync/blob/12ad72c47fe7bb04e7250892c324ac5f5faa4071/documents/sample%20dbus%20commands#L95-L97
    # * See https://github.com/mikebrady/shairport-sync/issues/1509#issuecomment-1200961116
    # * See https://github.com/mikebrady/shairport-sync/discussions/1352#discussioncomment-1790518
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
            res = subprocess.check_output(cmd, shell = True, executable = '/bin/bash').decode("utf-8")
        except Exception as e:
            self.__logger.warning(f'Unable to get shairport-sync client name: {e}')
            if throw:
                raise e
            else:
                return None

        m = re.search(r"^\s+variant\s+(.*)", res)
        if m is None:
            self.__logger.warning('Unable to parse shairport-sync client name')
            if throw:
                raise Exception('Unable to parse shairport-sync client name')
            else:
                return None
        else:
            return m.group(1)

    def get_shairport_sync_player_state(self, return_cmd = False, throw = False):
        # dbus-send --print-reply --system --dest=org.gnome.ShairportSync /org/gnome/ShairportSync org.freedesktop.DBus.Properties.Get string:org.gnome.ShairportSync.RemoteControl string:PlayerState
        cmd = f"{self.__SPS_DBUS_CMD} org.freedesktop.DBus.Properties.Get string:org.gnome.ShairportSync.RemoteControl string:PlayerState"
        if return_cmd:
            return cmd
        try:
            res = subprocess.check_output(cmd, shell = True, executable = '/bin/bash').decode("utf-8")
        except Exception as e:
            self.__logger.warning(f'Unable to get shairport-sync client name: {e}')
            if throw:
                raise e
            else:
                return None

        m = re.search(r"^\s+variant\s+(.*)", res)
        if m is None:
            self.__logger.warning('Unable to parse shairport-sync player state')
            if throw:
                raise Exception('Unable to parse shairport-sync player state')
            else:
                return None
        else:
            return m.group(1)
