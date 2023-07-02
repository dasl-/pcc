import os.path
import subprocess
import time
from pcc.directoryutils import DirectoryUtils
from pcc.logger import Logger
from pcc.receiverserver import ReceiverAPI

# If bluetooth has been discoverable for over __BT_DISCOVERABLE_TIMEOUT_S seconds, make it undiscoverable
# to prevent neighbors from accidentally connecting.
#
# Unfortunately, we can't rely on the DiscoverableTimeout config setting in /etc/bluetooth/main.conf to
# make bluetooth undiscoverable after N seconds. The DiscoverableTimeout feature seems buggy at the moment.
# Thus we do it manually with this Sweeper process, which cleans up after the ReceiverAPI class.
#
# When we tried using DiscoverableTimeout, the bluetooth server remained discoverable forever, despite
# dbus returning "False" for the Discoverable setting. However, when we explicitly set the server
# to undiscoverable, the server goes undiscoverable as intended.
class Sweeper():

    # How long to leave bluetooth as discoverable.
    BT_DISCOVERABLE_TIMEOUT_S = 60

    def __init__(self):
        self.__logger = Logger().set_namespace(self.__class__.__name__)

    def run(self):
        while True:
            if not os.path.isfile(ReceiverAPI.BT_DISCOVERABLE_SUCCESS_FILE):
                time.sleep(5)
                continue

            cmd = DirectoryUtils().root_dir + '/utils/sweeper_bt_cleanup.py'
            proc = subprocess.Popen(
                (f"flock --exclusive --nonblock {ReceiverAPI.BT_DISCOVERABLE_LOCK_FILE} --command '{cmd}'"),
                shell = True, executable = '/bin/bash'
            )

            while proc.poll() is None:
                time.sleep(0.1)
            if proc.returncode != 0:
                self.__logger.error(f'The sweeper_bt_cleanup script exited non-zero: {proc.returncode}.')

            time.sleep(5)
