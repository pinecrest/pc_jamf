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

for device in details:
    if asset_tag := device.get("assetTag"):
        if asset_tag.startswith("200"):
            print(f"{asset_tag} -> {asset_tag.zfill(9)}")
            print(pcjs.update_device(device.get("id"), assetTag=asset_tag))
