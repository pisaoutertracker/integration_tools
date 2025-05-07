import os
import yaml

safety_settings = {
    "internal_temperatures": [
        "TT05_CO2",  # MARTA supply temperature
        "TT06_CO2",  # MARTA return temperature
        "ch_temperature",  # Coldroom temperature
    ],
    "used_caen_ch": [
        "0.1",
        "2.1",
    ],
}

### Safety functions ###
# Example of a safety function
# def check_dummy_condition(*args, **kwargs):
#     # Dummy condition check
#     return True


def check_dew_point(system_status):
    print(f"Checking dew point: {system_status}")
    try:
        # Get the three required temperature values
        marta_supply_temp = system_status.get("marta", {}).get("TT05_CO2")
        marta_return_temp = system_status.get("marta", {}).get("TT06_CO2")
        coldroom_temp = system_status.get("coldroom", {}).get("ch_temperature", {}).get("value")
        # coldroom = system_status.get("coldroom", {})
        # print(f"Coldroom: {coldroom.get('CmdDoorUnlock_Reff')}")
        # door_status = system_status.get("coldroom", {}).get("CmdDoorUnlock_Reff")
        # print(f"Door status: {door_status}")

        # Create list of available temperatures
        internal_temperatures = []
        if marta_supply_temp is not None:
            internal_temperatures.append(marta_supply_temp)
        if marta_return_temp is not None:
            internal_temperatures.append(marta_return_temp)
        if coldroom_temp is not None:
            internal_temperatures.append(coldroom_temp)

        # print(f"Available temperatures: {internal_temperatures}")

        # Only proceed if we have all three temperatures
        if len(internal_temperatures) != 3:
            print(f"Not all temperatures available. Found {len(internal_temperatures)} out of 3")
            return False

        # Get the minimum temperature among the three
        min_temperature = min(internal_temperatures)

        if "coldroom" not in system_status or "CmdDoorUnlock_Reff" not in system_status["coldroom"]:
            print("Coldroom data not available")
            return False  # Conservative approach - if we can't check, assume it's unsafe

        if system_status["coldroom"]["CmdDoorUnlock_Reff"] == 1:  # Door is open
            # Check if environment data exists
            if "cleanroom" not in system_status or "dewpoint" not in system_status["cleanroom"]:
                return False  # Conservative approach
            reference_dew_point = system_status["cleanroom"]["dewpoint"]  # External dewpoint
            print(f"Reference dew point: {reference_dew_point}")
        else:  # Door is closed
            if "dew_point_c" not in system_status["coldroom"]:
                return False  # Conservative approach
            reference_dew_point = system_status["coldroom"]["dew_point_c"]
            print(f"Reference dew point: {reference_dew_point}")

        # reference_dew_point = system_status["cleanroom"]["dewpoint"]
        # print(f"Min temperature: {min_temperature}, Dew point: {reference_dew_point}")
        return min_temperature > reference_dew_point
    except Exception as e:
        print(f"Error in check_dew_point: {str(e)}")
        return False  # Conservative approach


def check_door_status(system_status):
    try:
        if "coldroom" not in system_status or "door_status" not in system_status["coldroom"]:
            return False  # Conservative approach
        return system_status["coldroom"]["door_status"] == 1  # Door is open
    except Exception as e:
        print(f"Error in check_door_status: {str(e)}")
        return False  # Conservative approach


def check_light_status(system_status):
    try:
        if "coldroom" not in system_status or "light" not in system_status["coldroom"]:
            return False  # Conservative approach
        return system_status["coldroom"]["light"] == 1  # Light is on
    except Exception as e:
        print(f"Error in check_light_status: {str(e)}")
        return False  # Conservative approach


def check_any_hv_on(caen_ch_status):
    try:
        # Check if any used channel is on
        hv_on = False
        for channel in safety_settings["used_caen_ch"]:
            ch_str = f"caen_HV{channel}_IsOn"
            if bool(caen_ch_status.get(ch_str, False)):
                hv_on = True
                break
        return hv_on
    except Exception as e:
        print(f"Error in check_any_hv_on: {str(e)}")
        return True


def check_door_safe_to_open(system_status, caen_ch_status):
    """
    Check if it's safe to open the door based on multiple safety conditions.
    Returns True if it's safe to open the door, False otherwise.
    """
    log_msg = ""
    try:
        # Check if we have all necessary data
        if "coldroom" not in system_status:
            return False  # Conservative approach - if we can't check, assume it's unsafe

        # 1. Check if dew point conditions are safe
        dew_point_safe = check_dew_point(system_status)
        log_msg += f"Dew point safe: {dew_point_safe}\n"

        # 2. Check if high voltage is off
        hv_on = check_any_hv_on(caen_ch_status)
        log_msg += f"High voltage on: {hv_on}\n"

        # 3. Check if light is off (light should be off when opening door)
        # light_off = not check_light_status(system_status)

        # 4. Check if door is currently closed (can't open if already open)
        door_closed = not check_door_status(system_status)
        log_msg += f"Door closed: {door_closed}\n"

        # It's safe to open the door if:
        # - Dew point conditions are safe
        # - High voltage is safe
        # - Light is off
        # - Door is currently closed
        is_safe = dew_point_safe and door_closed and not hv_on
        return is_safe, log_msg

    except Exception as e:
        print(f"Error in check_door_safe_to_open: {str(e)}")
        return False  # Conservative approach - if we can't check, assume it's unsafe


def check_light_safe_to_turn_on(system_status, caen_ch_status):
    """
    Check if it's safe to turn on the light based on multiple safety conditions.
    Returns True if it's safe to turn on the light, False otherwise.
    """
    log_msg = ""
    try:
        # Check if we have all necessary data
        if "coldroom" not in system_status:
            return False  # Conservative approach - if we can't check, assume it's unsafe

        # Check if high voltage is off
        hv_on = check_any_hv_on(caen_ch_status)
        log_msg += f"High voltage on: {hv_on}\n"
        is_safe = not hv_on
        return is_safe

    except Exception as e:
        print(f"Error in check_light_safe_to_turn_on: {str(e)}")
        return False  # Conservative approach - if we can't check, assume it's unsafe
