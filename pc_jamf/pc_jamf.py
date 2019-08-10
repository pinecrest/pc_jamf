import requests
import time
from urllib.parse import urljoin
from datetime import datetime, timezone
from pprint import pprint
import json
import pathlib
from typing import Union
from requests.auth import HTTPBasicAuth
import html
import xml.etree.ElementTree as ET

AUTH_ENDPOINT = "auth/tokens"
MOBILE_DEVICE_ENDPOINT = "inventory/obj/mobileDevice"
SEARCH_DEVICE_ENDPOINT = "inventory/searchMobileDevices"
VALIDATION_ENDPOINT = "auth/current"
INVALIDATE_ENDPOINT = "auth/invalidateToken"
CLASSIC_ENDPOINT = "/JSSResource"
CLASSIC_DEVICENAME_ENDPOINT = f"{CLASSIC_ENDPOINT}/mobiledevicecommands/command/DeviceName"
DEVICE_RENAMING_RESTRICTION_PROFILE_ID = 127


class PCJAMF:
    """
    The PCJAMF class provides an interface to the Pine Crest JAMF server for mobile device management (MDM)

    Class Methods:
        available: checks to see if the server is accessible
            server (str): the protocol, url, and port of a JAMF server
            path (str): the path to the server. (optional)
            verify (str, bool): whether to verify SSL certificates. Set to a PEM CA store 
                for custom validation. Set to False for self-signed certs

    Args:
        username: the username to use for authentication
        password: the password to use for authentication
        server: the JAMF server path, including protocol, fqdn, and port
        verify (str, bool): the path to a CA file for cert verification 
            or False to disable SSL certificate verification

    """

    jamf_api_root = "/uapi/"

    @classmethod
    def available(
        cls,
        server: str,
        path: str = "v1/jamf-pro-server-url",
        verify: Union[str, bool] = True,
    ) -> bool:
        """
        checks to see if the provided jamf server is accessible
        """

        cls.jamf_url = urljoin(server, cls.jamf_api_root)
        url = urljoin(cls.jamf_url, path)
        response = requests.get(url, verify=verify)
        print(f"{url}: {response.status_code}")
        return response.ok or response.status_code == 401

    def __init__(self, username: str, password: str, server: str=None, verify: Union[str, bool]=True):
        if server:
            self.jamf_server = server
            self.jamf_url = urljoin(self.jamf_server, self.jamf_api_root)
        self.session = requests.Session()
        self.session.verify = verify
        self.session.auth = (username, password)
        self.session.headers.update({"Accept": "application/json"})
        self.token = None
        self.auth_expiration = None
        self.classic_session = requests.Session()
        self.classic_session.verify = verify
        self.classic_session.auth = HTTPBasicAuth(username, password)
        self.classic_session.headers.update({"Accept": "application/xml"})

    def authenticate(self):
        """
        Connect to the JAMF server, authenticate using existing credentials, and get an API token
        """
        r = self.session.post(self._url(AUTH_ENDPOINT))
        if not r.ok:
            raise Exception(f"Invalid status code found. ({r.status_code})")
        auth_data = r.json()
        self.session.auth = None
        self.token = auth_data["token"]
        self.auth_expiration = datetime.fromtimestamp(auth_data["expires"] / 1000)
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    @property
    def authenticated(self):
        """
        Indicates if the server object is currently authenticated
        """
        return self.token and self.auth_expiration > datetime.now()

    def _url(self, endpoint):
        return urljoin(self.jamf_url, endpoint)

    def all_devices(self):
        r = self.session.get(self._url(MOBILE_DEVICE_ENDPOINT))
        return r.json()

    def search_devices(self, *, serial=None, name=None, udid=None, asset_tag=None):
        search_params = {"pageNumber": 0, "pageSize": 100}
        if not any((serial, name, udid, asset_tag)):
            raise Exception("You must provide at least one search term")

        if name:
            search_params["name"] = name
        if serial:
            search_params["serialNumber"] = serial
        if udid:
            search_params["udid"] = udid
        if asset_tag:
            search_params["assetTag"] = asset_tag

        r = self.session.post(url=self._url(SEARCH_DEVICE_ENDPOINT), json=search_params)
        payload = r.json()
        print(payload)
        if payload["totalCount"] > 0:
            return payload["results"]
        else:
            raise Exception(
                f"No results found for query\nserial: {serial}\nid: {name}\nudid:{udid}"
            )

    def device(self, device_id, detail=False):
        url = self._url(f"{MOBILE_DEVICE_ENDPOINT}/{device_id}")
        if detail:
            url += "/detail"
        r = self.session.get(url)
        return r.json()


    def update_device_name(self, device_id, name):

        url = self._url(html.escape(f"{CLASSIC_DEVICENAME_ENDPOINT}/{name}/id/{device_id}"))
        cr = self.classic_session.post(url=url, data='')
        if cr.status_code != 201:
            print(url)
            print(cr.text)
            print(cr.status_code)
            raise Exception('Unable to push device name command')

        return cr.text

    def delete_device(self, device_id):
        url = self._url(html.escape(f"{CLASSIC_ENDPOINT}/mobiledevices/id/{device_id}"))
        print(f'deleting device {device_id}')
        cr = self.classic_session.delete(url=url, data='')
        if cr.status_code == 200:
            print(f"Device {device_id} successfully deleted.")
            return True
        else:
            print(url)
            print(cr.text)
            raise Exception('Unable to push device name command')

    def device_flattened(self, device_id):
        device = {}
        extended_device_info = self.device(device_id=device_id, detail=True)
        device.update(
            {
                k: v
                for k, v in extended_device_info.items()
                if not isinstance(v, list) and not isinstance(v, dict)
            }
        )
        if "location" in extended_device_info:
            device.update(
                {
                    f"location_{k}": v
                    for k, v in extended_device_info["location"].items()
                    if not isinstance(v, dict) and not isinstance(v, list)
                }
            )
            device.update(
                {
                    f"location_{k}_name": v["name"]
                    for k, v in extended_device_info["location"].items()
                    if isinstance(v, dict) or isinstance(v, list)
                }
            )
        if "ios" in extended_device_info:
            device.update(
                {
                    k: v
                    for k, v in extended_device_info["ios"].items()
                    if not isinstance(v, dict) and not isinstance(v, list)
                }
            )
            device["application_count"] = len(
                extended_device_info["ios"]["applications"]
            )
            device.update(
                {
                    f"network_{k}": v
                    for k, v in extended_device_info["ios"]["network"].items()
                }
            )
        return device

    def validate(self):
        r = self.session.post(self._url(VALIDATION_ENDPOINT))
        return r.status_code == 200

    def invalidate(self):
        r = self.session.post(self._url(INVALIDATE_ENDPOINT))
        if r.ok:
            del self.session.headers["Accept"]
            del self.token
            del self.auth_expiration 
        return bool(r.ok)

    def change_device_configuration_profile_exclusion(self, device_id: int, configuration_profile_id: int, exclude_device: bool=True) -> bool:
        """
        Add or remove a mobile device from a mobile device configuration profile exclusion list
        """
        device = self.device(device_id=device_id)
        root = self.get_configuration_profile(configuration_profile_id)
        excluded_devices = root.findall(".//exclusions/mobile_devices")[0]
        excluded_ids = [elm.text for elm in excluded_devices.findall("./mobile_device/id")]
        if exclude_device and device_id not in excluded_ids:
            device_element = ET.SubElement(excluded_devices, 'mobile_device')
            try:
                ET.SubElement(device_element, 'id').text = str(device_id)
                ET.SubElement(device_element, 'name').text = device['name']
                ET.SubElement(device_element, 'udid').text = device['udid']
                ET.SubElement(device_element, 'wifi_mac_address').text = device['wifiMacAddress']
            except KeyError:
                raise Exception(f"device was not properly formed. {device}")
        elif not exclude_device:
            try:
                device_element = excluded_devices.findall(f"./mobile_device/[id='{device_id}']")[0]
                excluded_devices.remove(device_element) 
            except IndexError:
                return True # We don't really care if it's missing from the list
        else:
            return True
        return self.update_configuration_profile(root)
        

    def get_configuration_profile(self, configuration_profile_id: int) -> ET.ElementTree:
        r = self.classic_session.get(f"{self.jamf_server}JSSResource/mobiledeviceconfigurationprofiles/id/{configuration_profile_id}")
        return ET.fromstring(r.text)

    def update_configuration_profile(self, configuration_profile: ET.ElementTree) -> bool:
        configuration_id = configuration_profile.findall("./general/id")[0].text
        r = self.classic_session.put(f"{self.jamf_server}JSSResource/mobiledeviceconfigurationprofiles/id/{configuration_id}", ET.tostring(configuration_profile))
        return r.status_code == 201

    def update_device(self, device_id, **kwargs):
        if kwargs:
            r = self.session.post(
                self._url(f"{MOBILE_DEVICE_ENDPOINT}/{device_id}/update"), json=kwargs
            )
            return r.status_code == 200
        else:
            raise Exception("Nothing to update")

    def set_device_room(self, device_id: int, room_name: str) -> dict:
        """
        Method to retrieve a room location from JAMF
        """
        return self.update_device(device_id, location={'room': room_name})