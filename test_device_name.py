from getpass import getpass

from alive_progress import alive_it

from pc_jamf import PCJAMF

username = "sean.tibor"
password = getpass()
host = "https://b-jss1.pinecrest.edu:8443"

pcjs = PCJAMF(username, password, host)
pcjs.authenticate()

names = {
    "2223": "fi-cartA-013",
    "2243": "fi-cartA-014",
    "2258": "fi-cartA-017",
    "2271": "fi-cartA-018",
    "2283": "fi-cartA-001",
    "2294": "fi-cartA-019",
    "2353": "fi-cartA-002",
    "2364": "fi-cartA-012",
    "2409": "fi-cartA-009",
    "2431": "fi-cartA-007",
    "2438": "fi-cartA-016",
    "2444": "fi-cartA-010",
    "2450": "fi-cartA-023",
    "2454": "fi-cartA-004",
    "2463": "fi-cartA-011",
    "2494": "fi-cartA-024",
    "2502": "fi-cartA-022",
    "2503": "fi-cartA-015",
    "2533": "fi-cartA-005",
    "2534": "fi-cartA-008",
    "2545": "fi-cartA-020",
    "2613": "fi-cartA-021",
    "2641": "fi-cartA-006",
    "2645": "fi-cartA-003",
}

for device_id, name in alive_it(names.items()):
    pcjs.flush_mobile_device_commands(device_id=device_id)
    pcjs.update_device_name(device_id, name)
