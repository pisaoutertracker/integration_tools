import requests


def get_modules_on_ring(ring_id, db_url="http://cmslabserver:5000"):
    """Get the modules on a specific ring from the database snapshot."""
    url = f"{db_url}/generic_module_query"
    try:
        response = requests.post(url, json={"mounted_on": {"$regex": ring_id + ".*"}})
        if response.status_code == 200:
            snapshot = response.json()
            modules = {}
            for module in snapshot:
                if ring_id in module.get("mounted_on", ""):
                    modules[module["moduleName"]] = module
            return modules
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error making request to {url}: {str(e)}")
        return None


def get_module(module_id, db_url="http://cmslabserver:5000"):
    """Get a specific module from the database snapshot."""
    url = f"{db_url}/modules/{module_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            return None

    except requests.RequestException as e:
        print(f"Error making request to {url}: {str(e)}")
        return None

def get_module_lpgbtVersion(module, db_url="http://cmslabserver:5000"):
    # the version is under childer, PS Read-out Hybrid, details, ALPGBT_VERSION
    if isinstance(module, str):
        module = get_module(module, db_url)
    if not module:
        print(f"Module {module} not found.")
        return ""
    lpgbtVersion = "N/A"
    if isinstance(module.get("children"), dict):
        if isinstance(module.get("children").get("PS Read-out Hybrid"), dict):
            if isinstance(module.get("children").get("PS Read-out Hybrid").get("details"), dict):
                if module.get("children").get("PS Read-out Hybrid").get("details").get("ALPGBT_VERSION") is not None:
                    lpgbtVersion = module.get("children").get("PS Read-out Hybrid").get("details").get("ALPGBT_VERSION")
    return lpgbtVersion

def get_module_speed(module, db_url="http://cmslabserver:5000"):
    # check if the name or the object is given
    if isinstance(module, str):
        module = get_module(module, db_url)
    if not module:
        print(f"Module {module} not found.")
        return ""
    module_speed = "N/A"
    if (
        "_5_" in module.get("moduleName", "")
        or "_05_" in module.get("moduleName", "")
        or "_5-" in module.get("moduleName", "")
        or "_05-" in module.get("moduleName", "")
    ):
        module_speed = "5G"
    if "_10_" in module.get("moduleName", "") or "_10-" in module.get("moduleName", ""):
        module_speed = "10G"
        # Check hybrid details for speed
    if isinstance(module.get("children"), dict):
        if isinstance(module.get("children").get("PS Read-out Hybrid"), dict):
            if isinstance(module.get("children").get("PS Read-out Hybrid").get("details"), dict):
                if module.get("children").get("PS Read-out Hybrid").get("details").get("ALPGBT_BANDWIDTH") is not None:
                    module_speed = (
                        module.get("children").get("PS Read-out Hybrid").get("details").get("ALPGBT_BANDWIDTH")
                    )
                    if module_speed == "10Gbps":
                        module_speed = "10G"
                    if module_speed == "5Gbps":
                        module_speed = "5G"

    return module_speed


def get_module_endpoints(module_id, db_url="http://cmslabserver:5000"):
    """Get the module endpoints from the database snapshot."""
    url = f"{db_url}/snapshot"
    try:
        response = requests.post(url, json={"cable": module_id, "side": "crateSide"})
        if response.status_code == 200:
            snapshot = response.json()
            ret = {"LV": None, "HV": None, "FC7": None}
            for line in snapshot:
                if snapshot[line]["connections"]:
                    last_conn = snapshot[line]["connections"][-1]
                    # Get the last connection in the crateSide path
                    if "FC7" in last_conn["cable"]:
                        ret["FC7"] = f"{last_conn['cable']}_{last_conn['det_port'][0]}"
                    elif "XSLOT" in last_conn["cable"]:
                        ret["LV"] = f"LV{last_conn['cable'][5:]}.{last_conn['line']}"
                    elif "ASLOT" in last_conn["cable"]:
                        ret["HV"] = f"HV{last_conn['cable'][5:]}.{last_conn['det_port'][0]}"
            return ret
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error making request to {url}: {str(e)}")
        return None


def get_module_fuse_id(module, db_url="http://cmslabserver:5000"):
    """Get the fuse ID for a specific module."""
    if isinstance(module, str):
        module = get_module(module, db_url)
    if not module:
        print(f"Module {module} not found.")
        return None
    fuseId = None
    if "hwId" in module:
        fuseId = int(module["hwId"])
    if "children" in module and "lpGBT" in module["children"]:
        fuseId = int(module["children"]["lpGBT"]["CHILD_SERIAL_NUMBER"])
    return fuseId


if __name__ == "__main__":
    module_id = "PS_16_10_IPG-00005"
    endpoints = get_module_endpoints(module_id)
    if endpoints:
        print(f"Endpoints for module {module_id}: {endpoints}")
    else:
        print(f"Failed to retrieve endpoints for module {module_id}.")

    ring_id = "L1_47_A#1"
    modules = get_modules_on_ring(ring_id)
    if modules:
        # iterate on modules and print the module name and speed and mounted on, sorted by mounted_on
        for module_name, module in sorted(
            modules.items(), key=lambda x: int(x[1].get("mounted_on", ";0").split(";")[1])
        ):
            speed = get_module_speed(module)
            print(f"Speed: {speed} \t  {module.get('mounted_on', 'N/A')} \t  {module_name}")
    else:
        print(f"Failed to retrieve modules for ring {ring_id}.")
