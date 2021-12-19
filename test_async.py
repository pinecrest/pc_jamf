import logging
import pprint
import time
from getpass import getpass

import tqdm

from pc_jamf import PCJAMF

logger = logging.getLogger(__name__)


username = input("User: ")
password = getpass()
host = "https://b-jss1.pinecrest.edu:8443"

pcjs = PCJAMF(username, password, host)
pcjs.authenticate()
devices = pcjs.all_devices()

start = time.monotonic()
details = pcjs.all_devices(details=True)
async_elapsed = time.monotonic() - start
logger.info(
    f"Completed async run in {async_elapsed:.2f} seconds and fetched {len(details)} devices."
)

start = time.monotonic()
details = [pcjs.device(device["id"], detail=True) for device in tqdm.tqdm(devices)]
sync_elapsed = time.monotonic() - start
logger.info(
    f"Completed sync run in {sync_elapsed:.2f} seconds and fetched {len(details)} devices."
)
logger.info(
    f"Async run was {sync_elapsed/async_elapsed:.1f}x faster than synchronous run."
)
