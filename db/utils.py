import requests


def get_module_endpoints(module_id, db_url="http://cmslabserver:5000"):
    """Get the module endpoints from the database snapshot."""
    url= f"{db_url}/snapshot"
    try:
        response = requests.post(
            url,
            json={"cable": module_id, "side": "crateSide"}
        )
        if response.status_code == 200:
            snapshot = response.json()
            ret = {
                "LV": None,
                "HV": None,
                "fiber": None
            }
            for line in snapshot:
                if snapshot[line]["connections"]:
                    last_conn = snapshot[line]["connections"][-1]
                    # Get the last connection in the crateSide path
                    if "FC" in last_conn["cable"]:
                        ports = last_conn['crate_port'] + last_conn['det_port']
                        port = ports[0] if ports else "?"
                        ret["fiber"] = f"{last_conn['cable']}_{port}"
                    elif "XSLOT" in last_conn['cable']:
                        ret["LV"] = f"LV{last_conn['cable'][5:]}.{last_conn['line']}"
                    elif "ASLOT" in last_conn['cable']:
                        ret["HV"] = f"HV{last_conn['cable'][5:]}.{last_conn['line']}"
            return ret
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error making request to {url}: {str(e)}")
        return None


if __name__ == "__main__":
    module_id = "PS_16_10_IPG-00005"
    endpoints = get_module_endpoints(module_id)
    if endpoints:
        print(f"Endpoints for module {module_id}: {endpoints}")
    else:
        print(f"Failed to retrieve endpoints for module {module_id}.")



