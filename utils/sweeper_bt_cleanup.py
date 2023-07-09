#!/usr/bin/env python3
import os
import sys
import time

# This is necessary for the import below to work
root_dir = os.path.abspath(os.path.dirname(__file__) + '/..')
sys.path.append(root_dir)

from pcc.dbusclient import DbusClient
from pcc.logger import Logger
from pcc.sweeper import Sweeper
from pcc.receiverserver import ReceiverAPI

logger = Logger().set_namespace(os.path.basename(__file__))
if not os.path.isfile(ReceiverAPI.BT_DISCOVERABLE_SUCCESS_FILE):
    logger.info(f"The file {ReceiverAPI.BT_DISCOVERABLE_SUCCESS_FILE} does not exist: bluetooth must already be " +
        "undiscoverable. Bailing before taking any action.")
    sys.exit(0)

mtime = os.path.getmtime(ReceiverAPI.BT_DISCOVERABLE_SUCCESS_FILE)
if (time.time() - mtime) < Sweeper.BT_DISCOVERABLE_TIMEOUT_S:
    logger.info(f"Bluetooth has not yet been discoverable for {Sweeper.BT_DISCOVERABLE_TIMEOUT_S} seconds. " +
        "Bailing before taking any action.")
    sys.exit(0)
logger.info(f"Bluetooth has been discoverable for over {Sweeper.BT_DISCOVERABLE_TIMEOUT_S} seconds. " +
    "Setting it to undiscoverable...")

DbusClient().set_bluetooth_discoverable(False, throw = True)
logger.info("Successfully sent dbus command to make bluetooth undiscoverable...")

os.remove(ReceiverAPI.BT_DISCOVERABLE_SUCCESS_FILE)
logger.info("Successfully completed making bluetooth undiscoverable.")
