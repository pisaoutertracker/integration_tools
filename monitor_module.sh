#!/bin/bash
# Usage: ./monitor_module.sh modulename monitor_time_seconds
if [ $# -ne 2 ]; then
    echo "Usage: $0 modulename monitor_time_seconds"
    exit 1
fi

MODULE_NAME=$1
MONITOR_TIME=$2

# Check if jq is available
if ! command -v jq >/dev/null 2>&1; then
    echo "Error: jq is required but not installed. Please install jq first."
    echo "On Ubuntu/Debian: sudo apt-get install jq"
    echo "On CentOS/RHEL: sudo yum install jq"
    exit 1
fi

# Get module information
OUT=`/home/thermal/integration_tools/modulesearch.py $MODULE_NAME`

# Extract OG number, OT number, and LV channel from OUT
OG_NUMBER=$(echo "$OUT" | grep -o 'OG[0-9]\+' | perl -pe 's/.*OG//')
OT_NUMBER=$(echo "$OUT" | grep -o 'OT[0-9]\+'| perl -pe 's/OT//')
LV_CHANNEL=$(echo "$OUT" | grep -o 'LV[0-9.]\+' | perl -pe 's/.*LV: //')

echo "========================================="
echo "MODULE MONITORING SESSION"
echo "========================================="
echo "Module Name: $MODULE_NAME"
echo "Monitor Time: $MONITOR_TIME seconds"
echo "Extracted OG Number: $OG_NUMBER"
echo "Extracted OT Number: $OT_NUMBER"
echo "Extracted LV Channel: $LV_CHANNEL"
echo "========================================="

# Get calibration data from MongoDB
echo "Retrieving calibration data from database..."
MODULE_NAME_UPPER=$(echo "$MODULE_NAME" | tr '[:lower:]' '[:upper:]')
CALIBRATION_DATA=$(curl -s "http://cmslabserver:5000/modules/$MODULE_NAME_UPPER")

if [ $? -ne 0 ] || [ -z "$CALIBRATION_DATA" ]; then
    echo "Warning: Could not retrieve calibration data from database"
    CALIBRATION_DATA="{}"
fi

echo "Calibration data retrieved: $CALIBRATION_DATA"

# Parse and display the temperature_offsets for debugging
echo "Extracting temperature_offsets..."
TEMP_OFFSETS=$(echo "$CALIBRATION_DATA" | jq -r '.temperature_offsets // {}' 2>/dev/null)
echo "Temperature offsets found: $TEMP_OFFSETS"

# Setup and start runCalibration process
echo "Setting up calibration process..."
source setup.sh

if [ ! -f "balistic_template.xml" ]; then
    echo "Error: balistic_template.xml not found!"
    exit 1
fi

cp balistic_template.xml ./balistic.xml
perl -pe 's/target=.*:5000/target=192.168.0.19'$OT_NUMBER':5000/' -i balistic.xml
perl -pe 's/OpticalGroup Id="0"/OpticalGroup Id="'$OG_NUMBER'"/' -i balistic.xml

echo "Starting runCalibration process..."
runCalibration -f balistic.xml -c monitoronly -b >& /tmp/balistic.log &
#get pid of the last background process
CALIBRATION_PID=$!
echo "Running calibration with PID: $CALIBRATION_PID"

if [ -z "$CALIBRATION_PID" ]; then
    echo "Error: Failed to start runCalibration process!"
    exit 1
fi

sleep 1

echo "Turning on CAEN channel $LV_CHANNEL..."
/home/thermal/integration_tools/caen/caencli.py -c $LV_CHANNEL --on
if [ $? -eq 0 ]; then
    echo "CAEN channel $LV_CHANNEL turned on."
else
    echo "Warning: Failed to turn on CAEN channel $LV_CHANNEL"
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Cleaning up..."
    if [ ! -z "$CALIBRATION_PID" ]; then
        echo "Stopping calibration process (PID: $CALIBRATION_PID)..."
        kill $CALIBRATION_PID 2>/dev/null
        wait $CALIBRATION_PID 2>/dev/null
        echo "Calibration process stopped."
    fi
    
    if [ ! -z "$LV_CHANNEL" ]; then
        echo "Turning off CAEN channel $LV_CHANNEL..."
        /home/thermal/integration_tools/caen/caencli.py -c $LV_CHANNEL --off 2>/dev/null
        echo "CAEN channel $LV_CHANNEL turned off."
    fi
    
    echo "Cleanup completed."
    exit 0
}

# Set up signal handlers for clean exit
trap cleanup SIGINT SIGTERM

# Function to get calibration offset for a given field
get_calibration_offset() {
    local field_name=$1
    offset=$(echo "$CALIBRATION_DATA" | jq -r ".temperature_offsets.\"$field_name\" // 0" 2>/dev/null)
    echo "$offset"
}

# Function to parse and display temperature data
parse_temperature_data() {
    local mqtt_line=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] Raw MQTT data: $mqtt_line"
    
    # Parse JSON fields using jq
    counter=$(echo "$mqtt_line" | jq -r '.counter // "N/A"' 2>/dev/null)
    mqtt_timestamp=$(echo "$mqtt_line" | jq -r '.timestamp // "N/A"' 2>/dev/null)
    beboardid=$(echo "$mqtt_line" | jq -r '.BeBoardId // "N/A"' 2>/dev/null)
    fuseid=$(echo "$mqtt_line" | jq -r ".\"LpGBT_OG${OG_NUMBER}_fuseId\" // \"N/A\"" 2>/dev/null)
    
    echo "  Metadata:"
    echo "    counter: $counter"
    echo "    mqtt_timestamp: $mqtt_timestamp"
    echo "    BeBoardId: $beboardid"
    echo "    LpGBT_OG${OG_NUMBER}_fuseId: $fuseid"
    
    echo "  Temperature readings (Raw | Calibrated):"
    
    # Get all temperature field names using jq
    temp_fields=$(echo "$mqtt_line" | jq -r 'keys[] | select(test("_temp$"))' 2>/dev/null)
    
    for field_name in $temp_fields; do
        field_value=$(echo "$mqtt_line" | jq -r ".\"$field_name\"" 2>/dev/null)
        
        # Process SSA and MPA temperature fields
        if [[ "$field_name" =~ (SSA|MPA)_H[0-9]+_C[0-9]+_temp ]]; then
            # Extract chip type (SSA or MPA)
            chip_type=$(echo "$field_name" | grep -oE '^(SSA|MPA)')
            
            # Extract the numbers after H and after the second underscore
            h_num=$(echo "$field_name" | sed -E 's/.*_H([0-9]+)_.*/\1/')
            c_num=$(echo "$field_name" | sed -E 's/.*_H[0-9]+_C([0-9]+)_temp/\1/')
            
            # Convert H number using modulo 2
            h_converted=$((h_num % 2))
            converted_name="${chip_type}_H${h_converted}_${c_num}"
            
            # Debug the conversion process
            echo "    Converting: $field_name -> H$h_num(mod 2)=H$h_converted -> $converted_name"
            
            # Get calibration offset for this field
            calibration_offset=$(get_calibration_offset "$converted_name")
            
            # Calculate calibrated temperature (RAW + OFFSET)
            calibrated_temp=$(echo "$field_value + $calibration_offset" | bc -l)
            calibrated_temp=$(printf "%6.2f" "$calibrated_temp")
            field_value=$(printf "%6.2f" "$field_value")
            
            echo "    $field_name -> $converted_name: $field_value°C | $calibrated_temp°C (offset: $calibration_offset)"
        else
            # For other temperature fields, just show raw value
            field_value=$(printf "%6.2f" "$field_value")
            echo "    $field_name: $field_value°C | $field_value°C (no calibration)"
        fi
    done
    echo "----------------------------------------"
}

# Start monitoring
echo "Starting monitoring session for $MONITOR_TIME seconds..."
echo "Listening to MQTT topic: /ph2acf/#"
echo "========================================="

# Calculate end time
END_TIME=$(($(date +%s) + MONITOR_TIME))

# Monitor MQTT messages for the specified time
while [ $(date +%s) -lt $END_TIME ]; do
    # Get one MQTT message with a timeout
    mqtt_output=$(timeout 5 mosquitto_sub -h 192.168.0.45 -t '/ph2acf/#' -C 1 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$mqtt_output" ]; then
        parse_temperature_data "$mqtt_output"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] No MQTT data received in last 5 seconds..."
    fi
    
    # Small delay to prevent overwhelming output
    sleep 1
done

# Call cleanup function
cleanup

# Final summary
echo "========================================="
echo "MONITORING SESSION COMPLETED"
echo "========================================="
echo "Module Name: $MODULE_NAME"
echo "Total monitoring time: $MONITOR_TIME seconds"
echo "OT Number: $OT_NUMBER"
echo "OG Number: $OG_NUMBER"
echo "CAEN Channel: $LV_CHANNEL"
echo "Session ended at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="
