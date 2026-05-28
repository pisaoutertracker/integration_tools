import os
import yaml
import logging

logger = logging.getLogger(__name__)

safety_settings = {
    "internal_temperatures": [
        "TT05_CO2",  # MARTA supply temperature
        "TT06_CO2",  # MARTA return temperature
        "ch_temperature",  # Coldroom temperature
    ]
}

### Safety functions ###
# Example of a safety function
# def check_dummy_condition(*args, **kwargs):
#     # Dummy condition check
#     return True


def check_dew_point(system_status):
    logger.debug(f"Checking dew point: {system_status}")
    try:
        # Get the three required temperature values
        marta_supply_temp = system_status.get("marta", {}).get("TT05_CO2")
        marta_return_temp = system_status.get("marta", {}).get("TT06_CO2")
        coldroom_temp = system_status.get("coldroom", {}).get("ch_temperature", {}).get("value")
        # coldroom = system_status.get("coldroom", {})
        # logger.debug(f"Coldroom: {coldroom.get('CmdDoorUnlock_Reff')}")
        # door_status = system_status.get("coldroom", {}).get("CmdDoorUnlock_Reff")
        # logger.debug(f"Door status: {door_status}")

        # Create list of available temperatures
        internal_temperatures = []
        if marta_supply_temp is not None:
            internal_temperatures.append(marta_supply_temp)
        if marta_return_temp is not None:
            internal_temperatures.append(marta_return_temp)
        if coldroom_temp is not None:
            internal_temperatures.append(coldroom_temp)

        # logger.debug(f"Available temperatures: {internal_temperatures}")

        # Only proceed if we have all three temperatures
        # if len(internal_temperatures) != 3:
        #     logger.debug(f"Not all temperatures available. Found {len(internal_temperatures)} out of 3")
        #     return False

        # Get the minimum temperature among the three
        min_temperature = min(internal_temperatures)

        if "coldroom" not in system_status:
            logger.debug("Coldroom data not available")
            return False  # Conservative approach - if we can't check, assume it's unsafe

        # Check if environment data exists
        if "cleanroom" not in system_status or "dewpoint" not in system_status["cleanroom"]:
            return False  # Conservative approach
        reference_dew_point = system_status["cleanroom"]["dewpoint"]  # External dewpoint
        logger.debug(f"Reference dew point: {reference_dew_point}")
        delta = 1  # Allowable delta between dew point and temperature
        return min_temperature > reference_dew_point + delta
    except Exception as e:
        logger.debug(f"Error in check_dew_point: {str(e)}")
        return False, "Error checking dew point safety"  # Conservative approach


def check_door_status(system_status):
    try:
        if "coldroom" not in system_status or "door_status" not in system_status["coldroom"]:
            return False  # Conservative approach
        return system_status["coldroom"]["CmdDoorUnlock_Reff"] == 1  # Door is open
    except Exception as e:
        logger.debug(f"Error in check_door_status: {str(e)}")
        return False, "Error checking door status"  # Conservative approach


def check_light_status(system_status):
    try:
        if "coldroom" not in system_status or "light" not in system_status["coldroom"]:
            return False  # Conservative approach
        return system_status["coldroom"]["light"] == 1  # Light is on
    except Exception as e:
        logger.debug(f"Error in check_light_status: {str(e)}")
        return False, "Error checking light status"  # Conservative approach


def check_any_hv_on(caen_ch_status, used_channels):
    try:
        # Check if any used channel is on
        hv_on = False
        for channel in used_channels["HV"]:
            ch_str = f"caen_{channel}_IsOn"
            if bool(caen_ch_status.get(ch_str, False)):
                hv_on = True
                break
        return hv_on
    except Exception as e:
        logger.debug(f"Error in check_any_hv_on: {str(e)}")
        return True, "Error checking high voltage status"  # Conservative approach - if we can't check, assume it's unsafe


def check_cleanroom_expired(elapsed_time, threshold=600):
    return elapsed_time > threshold


def check_door_safe_to_open(system_status, caen_ch_status, used_channels):
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
        clean_room_expired = check_cleanroom_expired(system_status["cleanroom"]["elapsed_time"])
        if clean_room_expired:
            dew_point_safe = False
            log_msg += f"!!! Warning: Cleanroom data expired, not able to check dew point !!!\n"
        else:
            dew_point_safe = check_dew_point(system_status)
            if not dew_point_safe:
                log_msg += f"!!! Warning: Dew point conditions are not safe for opening door !!!\n"
                log_msg += f"Dew point safe: NO\n"
            else:
                log_msg += f"Dew point safe: YES\n"

        # 2. Check if high voltage is off
        hv_on = check_any_hv_on(caen_ch_status, used_channels)
        hv_safe = not hv_on
        if hv_safe == False:
            log_msg += f"!!! Warning: High voltage is ON, not safe to open door !!!\n"
            log_msg += f"High voltage safe: NO\n"
        else:
            log_msg += f"High voltage safe: YES\n"

        # 3. Check if light is off (light should be off when opening door)
        # light_off = not check_light_status(system_status)

        # 4. Check if door is currently closed (can't open if already open)
        door_closed = not check_door_status(system_status)
        if not door_closed and not (hv_safe or dew_point_safe):
            log_msg += f"!!! Warning: Door open when conditions are unsafe !!!\n"

        # It's safe to open the door if:
        # - Dew point conditions are safe
        # - High voltage is safe
        # - Light is off
        # - Door is currently closed
        is_safe = dew_point_safe and hv_safe
        return is_safe, log_msg

    except Exception as e:
        logger.debug(f"Error in check_door_safe_to_open: {str(e)}")
        return False, "Error checking door safety"


def check_light_safe_to_turn_on(system_status, caen_ch_status, used_channels):
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
        hv_on = check_any_hv_on(caen_ch_status, used_channels)
        log_msg += f"High voltage on: {hv_on}\n"
        is_safe = not hv_on
        return is_safe

    except Exception as e:
        logger.debug(f"Error in check_light_safe_to_turn_on: {str(e)}")
        return False  # Conservative approach - if we can't check, assume it's unsafe


def check_marta_safe(system_status):
    try:
        if "marta" not in system_status:
            return False, "MARTA data not available"
        if system_status["marta"].get("fsm_state") == "DISCONNECTED":
            return False, "MARTA is disconnected"
        else:
            return True, "MARTA status OK"
    except Exception as e:
        logger.debug(f"Error in check_marta_safe: {str(e)}")
        return False, "Error checking MARTA status"


# def check_lv_safe_on:

# def check_marta_on_for_ot
# def check_marta_on_for_it

#def switch_all_lv_off


# def soft_interlock_loop: ### describe only highlevel
# if condition then : action
# if ! check_lv_safe_on and something_on : switch_all_lv_off()

#when performing an active safety action here we send a msg to the alarm topic "/alarm"

def check_lv_safe_on(caen_ch_status, used_channels):
    """
    Check if any LV channel is on.
    Returns True if any LV channel is on, False if all are off.
    """
    try:
        for channel in used_channels["LV"]:
            if channel is None:
                continue
            ch_str = f"caen_{channel}_IsOn"
            if bool(caen_ch_status.get(ch_str, False)):
                return True
        return False
    except Exception as e:
        logger.debug(f"Error in check_lv_safe_on: {str(e)}")
        return True  # Conservative - assume LV is on if we can't check


def check_marta_on_for_ot(system_status):
    """
    Check if MARTA is running for OT (Outer Tracker).
    Returns True if MARTA is connected and operational.
    """
    try:
        if "marta" not in system_status:
            return False
        fsm_state = system_status["marta"].get("fsm_state", "")
        return fsm_state not in ("DISCONNECTED", "NONE", "")
    except Exception as e:
        logger.debug(f"Error in check_marta_on_for_ot: {str(e)}")
        return False


def check_marta_on_for_it(system_status):
    """
    Check if MARTA is running for IT (Inner Tracker).
    Returns True if MARTA is connected and operational.
    """
    try:
        if "marta" not in system_status:
            return False
        fsm_state = system_status["marta"].get("fsm_state", "")
        return fsm_state not in ("DISCONNECTED", "NONE", "")
    except Exception as e:
        logger.debug(f"Error in check_marta_on_for_it: {str(e)}")
        return False


def switch_all_lv_off(caen, used_channels):
    """
    Turn off all LV channels.
    Returns True if all commands were sent successfully.
    """
    try:
        for channel in used_channels["LV"]:
            if channel is None:
                continue
            logger.warning(f"Safety interlock: turning off LV channel {channel}")
            caen.off(channel)
        return True
    except Exception as e:
        logger.error(f"Error in switch_all_lv_off: {str(e)}")
        return False


def soft_interlock_loop(system_status, caen_ch_status, used_channels, caen, publish_alarm=None):
    """
    Soft interlock loop - monitors safety conditions and takes protective action.

    High-level logic:
      if LV is on AND MARTA is not running:
          → switch all LV off
          → publish alarm message to /alarm topic

    When performing an active safety action, a message is sent to the alarm topic "/alarm"
    via the publish_alarm callback.

    Args:
        system_status (dict): Full system status including MARTA, coldroom, etc.
        caen_ch_status (dict): CAEN channel status with caen_{channel}_IsOn keys.
        used_channels (dict): Active channel list {"LV": [...], "HV": [...]}.
        caen: CAEN control object with on()/off() methods.
        publish_alarm (callable, optional): Function to publish alarm messages.
            Signature: publish_alarm(message_string)

    Returns:
        tuple: (is_safe: bool, message: str)
    """
    try:
        lv_on = check_lv_safe_on(caen_ch_status, used_channels)
        marta_ot = check_marta_on_for_ot(system_status)
        marta_it = check_marta_on_for_it(system_status)
        marta_on = marta_ot or marta_it

        log_msg = f"Soft interlock: LV_on={lv_on}, MARTA_OT={marta_ot}, MARTA_IT={marta_it}"

        if lv_on and not marta_on:
            alarm_msg = (
                "SAFETY INTERLOCK: LV channels are on but MARTA is not running. "
                "Turning off all LV channels to prevent module damage."
            )
            logger.warning(alarm_msg)
            switch_all_lv_off(caen, used_channels)
            if publish_alarm:
                publish_alarm(alarm_msg)
            return False, alarm_msg

        return True, log_msg

    except Exception as e:
        err_msg = f"Error in soft_interlock_loop: {str(e)}"
        logger.error(err_msg)
        return False, err_msg