import threading
import integration_gui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QLineEdit, QLabel, QFormLayout, QTreeWidgetItem,
    QTreeWidget, QMessageBox
)
from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtWidgets import QGraphicsScene
from math import *
import requests
import subprocess
import yaml
import os
import paho.mqtt.client as mqtt
import struct
import numpy as np
from caenGUI import CAENControl
import json
# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.axes_grid1 import make_axes_locatable
import struct
import numpy as np
from caenGUI import CAENControl

# Add this class near the top of the file
class LogEmitter(QObject):
    """Helper class to emit log messages from any thread"""
    log_message = pyqtSignal(str)

class MainApp(integration_gui.Ui_MainWindow):
    def __init__(self, window):
        self.setupUi(window)    
        
        # Initialize log emitter
        self.log_emitter = LogEmitter()
        self.log_emitter.log_message.connect(self.append_log)
        
        # Fix text format setting
        self.placeholdersHelpLabel.setTextFormat(Qt.PlainText)
        
        # Initialize MQTT client to None
        self.client = None
        
        # Load settings before setting up connections
        self.load_settings()
        
        self.ringLE.returnPressed.connect(self.split_ring_and_position)
        self.positionLE.returnPressed.connect(self.draw_ring)
        fibers=["SfibA","SfibB"]
        powers=["BINT1"]
        self.fiberCB.addItems(fibers)
        self.powerCB.addItems(powers)
        self.number_of_modules=18
        self.draw_ring()
        
        # Setup thermal camera plotting
        self.setup_thermal_plot()
        
        # Setup CAEN control
        self.caen = CAENControl(self)
        
        # Connect button signals
        self.checkIDPB.clicked.connect(self.run_check_id)
        self.hvOFFTestPB.clicked.connect(self.run_light_on_test)
        self.hvONTestPB.clicked.connect(self.run_dark_test)
        self.connectPowerPB.clicked.connect(self.connect_power)
        self.connectFiberPB.clicked.connect(self.connect_fiber)
        
        # Connect settings-related signals
        self.apiBaseUrlLE.textChanged.connect(self.save_settings)
        self.checkIDCommandLE.textChanged.connect(self.save_settings)
        self.lightOnCommandLE.textChanged.connect(self.save_settings)
        self.darkTestCommandLE.textChanged.connect(self.save_settings)
        self.connectFiberEndpointLE.textChanged.connect(self.save_settings)
        self.connectPowerEndpointLE.textChanged.connect(self.save_settings)
        self.connectFiberMethodCB.currentTextChanged.connect(self.save_settings)
        self.connectPowerMethodCB.currentTextChanged.connect(self.save_settings)
        
        # Connect Apply button
        self.applySettingsPB.clicked.connect(self.apply_settings)

        # Initial MQTT setup
        self.setup_mqtt()

        # Connect filter signals
        self.speedCB.currentTextChanged.connect(self.update_module_list)
        self.spacerCB.currentTextChanged.connect(self.update_module_list)
        self.spacerCB_2.currentTextChanged.connect(self.update_module_list)
        self.spacerCB_3.currentTextChanged.connect(self.update_module_list)
        
        # Initial module list load
        self.update_module_list()

        # Connect select module button
        self.selectModulePB.clicked.connect(self.select_module)
        
        # Enable selection mode for tree widget
        self.treeWidget.setSelectionMode(QTreeWidget.SingleSelection)

        # Connect selection changes
        self.moduleLE.textChanged.connect(self.update_connection_status)
        self.powerCB.currentTextChanged.connect(self.update_connection_status)
        self.fiberCB.currentTextChanged.connect(self.update_connection_status)
        self.fiber_endpoint=""
        # Initial connection status check
        QTimer.singleShot(100, self.update_connection_status)  # Small delay to ensure UI is ready

    def setup_thermal_plot(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # First plot: Image
        self.im = self.ax1.imshow(np.random.rand(24, 32) * 30 + 10, cmap="plasma")
        divider1 = make_axes_locatable(self.ax1)
        self.cax1 = divider1.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(self.im, cax=self.cax1)

        # Second plot: Trend
        self.time = []
        self.min_values = []
        self.max_values = []
        self.avg_values = []

        self.line_min, = self.ax2.plot(self.time, self.min_values, label='Min')
        self.line_max, = self.ax2.plot(self.time, self.max_values, label='Max')
        self.line_avg, = self.ax2.plot(self.time, self.avg_values, label='Avg')
        self.ax2.legend()

        # Create canvas and add to layout
        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout(self.plotWidget)
        layout.addWidget(self.canvas)

    def get_settings_file(self):
        """Get the settings file path"""
        return os.path.join(os.path.dirname(__file__), 'settings.yaml')

    def load_settings(self):
        """Load settings from YAML file"""
        try:
            with open(self.get_settings_file(), 'r') as f:
                settings = yaml.safe_load(f)
                
            if settings:
                # Load API settings
                self.apiBaseUrlLE.setText(settings.get('api_base_url', ''))
                self.connectFiberEndpointLE.setText(settings.get('fiber_endpoint', ''))
                self.connectPowerEndpointLE.setText(settings.get('power_endpoint', ''))
                
                # Load HTTP methods
                fiber_method = settings.get('fiber_method', 'POST')
                power_method = settings.get('power_method', 'POST')
                self.connectFiberMethodCB.setCurrentText(fiber_method)
                self.connectPowerMethodCB.setCurrentText(power_method)
                
                # Load commands
                self.checkIDCommandLE.setText(settings.get('check_id_command', ''))
                self.lightOnCommandLE.setText(settings.get('light_on_command', ''))
                self.darkTestCommandLE.setText(settings.get('dark_test_command', ''))
                
                # Load MQTT settings
                self.mqttServerLE.setText(settings.get('mqtt_server', 'test.mosquitto.org'))
                self.mqttTopicLE.setText(settings.get('mqtt_topic', '/ar/thermal/image'))
                
                # Load DB endpoint
                self.dbEndpointLE.setText(settings.get('db_endpoint', 'http://localhost:5000/modules'))
                
        except FileNotFoundError:
            # Use defaults if no settings file exists
            self.save_settings()

    def save_settings(self):
        """Save settings to YAML file"""
        settings = {
            'api_base_url': self.apiBaseUrlLE.text(),
            'fiber_endpoint': self.connectFiberEndpointLE.text(),
            'power_endpoint': self.connectPowerEndpointLE.text(),
            'fiber_method': self.connectFiberMethodCB.currentText(),
            'power_method': self.connectPowerMethodCB.currentText(),
            'check_id_command': self.checkIDCommandLE.text(),
            'light_on_command': self.lightOnCommandLE.text(),
            'dark_test_command': self.darkTestCommandLE.text(),
            'mqtt_server': self.mqttServerLE.text(),
            'mqtt_topic': self.mqttTopicLE.text(),
            'db_endpoint': self.dbEndpointLE.text(),  # Add DB endpoint
        }
        
        try:
            with open(self.get_settings_file(), 'w') as f:
                yaml.dump(settings, f, default_flow_style=False)
        except Exception as e:
            self.log_output(f"Error saving settings: {e}")

    def setup_mqtt(self):
        """Setup MQTT client with error handling"""
        try:
            # Disconnect existing client if any
            if self.client:
                try:
                    self.client.disconnect()
                    self.client.loop_stop()
                except:
                    pass
            
            self.client = mqtt.Client()
            self.client.on_connect = self.on_mqtt_connect
            self.client.on_message = self.on_mqtt_message
            self.client.on_disconnect = self.on_mqtt_disconnect
            
            # Use settings from UI
            mqtt_server = self.mqttServerLE.text()
            
            # Connect with timeout
            self.log_output(f"Connecting to MQTT server: {mqtt_server}")
            self.client.connect_async(mqtt_server, 1883, 60)
            self.client.loop_start()
            
        except Exception as e:
            self.log_output(f"MQTT Setup Error: {str(e)}")
            # Don't let MQTT errors crash the UI
            return False
        return True

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection"""
        try:
            if rc == 0:
                self.log_output("Connected to MQTT server")
                mqtt_topic = self.mqttTopicLE.text()
                self.log_output(f"Subscribing to topic: {mqtt_topic}")
                client.subscribe(mqtt_topic)
            else:
                self.log_output(f"MQTT Connection failed with code {rc}")
        except Exception as e:
            self.log_output(f"MQTT Connect Error: {str(e)}")

    def on_mqtt_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection"""
        try:
            self.log_output("Disconnected from MQTT server")
            if rc != 0:
                self.log_output("Unexpected disconnection. Will attempt to reconnect...")
        except Exception as e:
            self.log_output(f"MQTT Disconnect Error: {str(e)}")

    def on_mqtt_message(self, client, userdata, msg):
        """Handle MQTT messages with error protection"""
        try:
            flo_arr = [
                struct.unpack("f", msg.payload[i : i + 4])[0]
                for i in range(0, len(msg.payload), 4)
            ]
            
            # Update image plot
            self.im.set_data(np.array(flo_arr).reshape(24, 32))
            self.im.set_clim(18, 30)
            
            # Update trend plot
            if len(self.time) == 0:
                self.time.append(0)
            else:
                self.time.append(self.time[-1] + 1)
            
            self.min_values.append(min(flo_arr))
            self.max_values.append(max(flo_arr))
            self.avg_values.append(np.mean(flo_arr))
            
            # Keep maximum 600 values
            if len(self.time) > 600:
                self.time.pop(0)
                self.min_values.pop(0)
                self.max_values.pop(0)
                self.avg_values.pop(0)

            self.line_min.set_data(self.time, self.min_values)
            self.line_max.set_data(self.time, self.max_values)
            self.line_avg.set_data(self.time, self.avg_values)
            self.ax2.relim()
            self.ax2.autoscale_view()
            
            self.canvas.draw()
            
        except Exception as e:
            self.log_output(f"MQTT Message Error: {str(e)}")

    def split_ring_and_position(self):
        ring_position = self.ringLE.text()
        ring=ring_position
        position="0"
        if ';' in ring_position:
            ring, position = ring_position.split(';')
        self.ringLE.setText(ring)
        self.positionLE.setText(position)
        if ring[:2] == "L1":
            self.number_of_modules=18
        if ring[:2] == "L2":
            self.number_of_modules=26
        if ring[:2] == "L3":
            self.number_of_modules=36
        self.draw_ring()
    
    def draw_ring(self):
        
        #draw a ring with number_of_modules modules, each is draw as a rectangle
        # even and odd modules are drawn at different radii
        # draw in graphics view
        scene = QGraphicsScene()
        self.graphicsView.setScene(scene)
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(Qt.black)
        #dashed style
        pen.setStyle(Qt.DashLine)
        radius=min(self.graphicsView.width(),self.graphicsView.height())/2.5
        scene.addEllipse(0, 0, radius*2, radius*2, pen)
        deltaphi=360/self.number_of_modules*2
        #solid
        pen.setStyle(Qt.SolidLine)
        #draw two circles in the middle-top
        scene.addEllipse(radius-7, -20, 6, 6, pen)
        scene.addEllipse(radius+7, -20, 6, 6, pen)
        scene.addEllipse(radius-4, -17, 1, 1, pen)
        scene.addEllipse(radius+10, -17, 1, 1, pen)

        for i in range(1,self.number_of_modules+1):
            phi=-(i)*deltaphi+deltaphi/2
            phi-=90
            if i> self.number_of_modules/2:
                phi+=deltaphi/2
            if self.positionLE.text()==str(i):
                pen.setColor(Qt.red)
            else:
                pen.setColor(Qt.black)
            if i<= self.number_of_modules/2:
                x1=(radius*0.95)*cos((phi+deltaphi/4)/180*pi)+radius
                y1=(radius*0.95)*sin((phi+deltaphi/4)/180*pi)+radius
                x2=(radius*0.95)*cos((phi-deltaphi/4)/180*pi)+radius
                y2=(radius*0.95)*sin((phi-deltaphi/4)/180*pi)+radius
                x3=(radius*1.1)*cos((phi+deltaphi/4)/180*pi)+radius
                y3=(radius*1.1)*sin((phi+deltaphi/4)/180*pi)+radius
                x4=(radius*1.1)*cos((phi-deltaphi/4)/180*pi)+radius
                y4=(radius*1.1)*sin((phi-deltaphi/4)/180*pi)+radius
                scene.addLine(x1, y1, x2, y2, pen)
                scene.addLine(x2, y2, x4, y4, pen)
                scene.addLine(x4, y4, x3, y3, pen)
                scene.addLine(x3, y3, x1, y1, pen)  
                
                
            else:
                x1=(radius*0.9)*cos((phi+deltaphi/4)/180*pi)+radius
                y1=(radius*0.9)*sin((phi+deltaphi/4)/180*pi)+radius
                x2=(radius*0.9)*cos((phi-deltaphi/4)/180*pi)+radius
                y2=(radius*0.9)*sin((phi-deltaphi/4)/180*pi)+radius
                x3=(radius*1.05)*cos((phi+deltaphi/4)/180*pi)+radius
                y3=(radius*1.05)*sin((phi+deltaphi/4)/180*pi)+radius
                x4=(radius*1.05)*cos((phi-deltaphi/4)/180*pi)+radius
                y4=(radius*1.05)*sin((phi-deltaphi/4)/180*pi)+radius
                scene.addLine(x1, y1, x2, y2, pen)
                scene.addLine(x2, y2, x4, y4, pen)
                scene.addLine(x4, y4, x3, y3, pen)
                scene.addLine(x3, y3, x1, y1, pen)
        



                


        self.graphicsView.show()

    def get_placeholder_values(self):
        """Get current values for all placeholders"""
        return {
            'ring_id': self.ringLE.text(),
            'position': self.positionLE.text(),
            'module_id': self.moduleLE.text(),
            'fiber': self.fiberCB.currentText(),
            'power': self.powerCB.currentText(),
            'fiber_endpoint': self.fiber_endpoint,
        }

    def expand_placeholders(self, text):
        """Replace placeholders in text with their current values"""
        values = self.get_placeholder_values()
        try:
            return text.format(**values)
        except KeyError as e:
            self.log_output(f"Warning: Unknown placeholder {e}")
            return text
        except ValueError as e:
            self.log_output(f"Warning: Invalid placeholder format - {e}")
            return text

    def run_command(self, command):
        """Run a shell command on a separate thread"""
        def worker():
            try:
                expanded_command = self.expand_placeholders(command)
                self.log_output(f"Running command: {expanded_command}")
                self.log_output(f"Using placeholders: {self.get_placeholder_values()}")
                
                result = subprocess.run(expanded_command, shell=True, check=True, 
                                          capture_output=True, text=True)
                self.log_output(f"Output:\n{result.stdout}")
            except subprocess.CalledProcessError as e:
                self.log_output(f"Error:\n{e.stderr}")
        threading.Thread(target=worker, daemon=True).start()
        return (True, None)

    def show_error_dialog(self, message):
        """Show error dialog with the given message"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("API Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def make_api_request(self, endpoint, method, data=None):
        """Make API request and return result"""
        url = self.expand_placeholders(self.apiBaseUrlLE.text())
        endpoint = self.expand_placeholders(endpoint)
        
        try:
            self.log_output(f"Making {method} request to: {url}/{endpoint}")
            
            if data:
                expanded_data = {
                    k: self.expand_placeholders(str(v)) 
                    for k, v in data.items()
                }
                self.log_output(f"With data: {expanded_data}")
            
            response = requests.request(
                method=method.lower(),
                url=f"{url}/{endpoint}",
                json=expanded_data if data else None
            )
                
            if response.status_code != 200:
                error_msg = f"API Error ({response.status_code}): {response.text}"
                self.log_output(error_msg)
                self.show_error_dialog(error_msg)
                return False, None

            result = response.json()
            self.log_output(f"Response: {result}")
            return True, result
        except requests.RequestException as e:
            error_msg = f"API Error: {str(e)}"
            self.log_output(error_msg)
            self.show_error_dialog(error_msg)
            return False, str(e)

    def log_output(self, text):
        """Log output to both console and text edit"""
        print(text)
        # Emit the log message instead of directly updating the UI
        self.log_emitter.log_message.emit(text)

    def append_log(self, text):
        """Append text to log widget (called in main thread)"""
        self.commandOutputTE.appendPlainText(text)
        self.commandOutputTE.appendPlainText("")  # Add blank line
        # Scroll to bottom
        self.commandOutputTE.verticalScrollBar().setValue(
            self.commandOutputTE.verticalScrollBar().maximum()
        )

    def run_check_id(self):
        self.log_output("=== Running Check ID ===")
        success, output = self.run_command(self.checkIDCommandLE.text())
        self.checkIDLED.setStyleSheet(
            "background-color: rgb(85, 170, 0);" if success else "background-color: red;")

    def run_light_on_test(self):
        self.log_output("=== Running Light On Test ===")
        success, output = self.run_command(self.lightOnCommandLE.text())
        self.hvOFFTestLED.setStyleSheet(
            "background-color: rgb(85, 170, 0);" if success else "background-color: red;")
        self.hvOFFTestCB.setChecked(success)

    def run_dark_test(self):
        self.log_output("=== Running Dark Test ===")
        success, output = self.run_command(self.darkTestCommandLE.text())
        self.hvONTestLED.setStyleSheet(
            "background-color: rgb(85, 170, 0);" if success else "background-color: red;")
        self.hvONTestCB.setChecked(success)

    def disconnect_connection(self, cable_id, port):
        """Disconnect a cable's detSide connections"""
        try:
            # Get current connections
            response = requests.post(
                f"{self.apiBaseUrlLE.text()}/snapshot",
                json={"cable": cable_id, "side": "detSide"}
            )
            if response.status_code == 200:
                snapshot = response.json()
                for line in snapshot:
                    if snapshot[line]["connections"]:
                        # Get the connected module
                        connected_module = snapshot[line]["connections"][-1]["cable"]
                        # Disconnect it
                        data = {
                            "cable2": cable_id,
                            "cable1": connected_module,
                            "port2": port ,
                            "port1": port if port=="power" else "fiber"
                        }
                        self.make_api_request(
                            endpoint="disconnect",
                            method="POST",
                            data=data
                        )
                        return #only disconnect the first
        except Exception as e:
            self.log_output(f"Error disconnecting: {str(e)}")

    def connect_power(self):
        self.log_output("=== Connecting Power ===")
        # First disconnect any existing connections
        self.disconnect_connection(self.powerCB.currentText(), "power")
        
        # Then make the new connection
        data = {
            "cable1": self.moduleLE.text(),
            "cable2": self.powerCB.currentText(),
            "port1": "power",
            "port2": "power"
        }
        success, result = self.make_api_request(
            endpoint=self.connectPowerEndpointLE.text(),
            method=self.connectPowerMethodCB.currentText(),
            data=data
        )
        
        # Update connection status and LEDs
        self.update_connection_status()
        self.update_connection_leds()

    def connect_fiber(self):
        self.log_output("=== Connecting Fiber ===")
        # First disconnect any existing connections
        self.disconnect_connection(self.fiberCB.currentText(), "A")
        
        # Then make the new connection
        data = {
            "cable1": self.moduleLE.text(),
            "cable2": self.fiberCB.currentText(),
            "port1": "fiber",
            "port2": "A"
        }
        success, result = self.make_api_request(
            endpoint=self.connectFiberEndpointLE.text(),
            method=self.connectFiberMethodCB.currentText(),
            data=data
        )
        
        # Update connection status and LEDs
        self.update_connection_status()
        self.update_connection_leds()

    def apply_settings(self):
        """Apply current settings"""
        self.log_output("=== Applying Settings ===")
        
        # Save settings to file
        self.save_settings()
        
        # Reconnect MQTT
        if self.setup_mqtt():
            self.log_output("MQTT settings applied successfully")
        else:
            self.log_output("Failed to apply MQTT settings")

    def update_module_list(self):
        """Update the module list based on current filters"""
        try:
            # Get endpoint from settings
            endpoint = self.dbEndpointLE.text()
            
            # Make request to DB
            response = requests.get(endpoint)
            if response.status_code != 200:
                self.log_output(f"Error fetching modules: {response.status_code}")
                return
                
            modules = response.json()
            #pretty print with indented json
            self.log_output(json.dumps(modules, indent=4))
            # Apply filters
            speed_filter = self.speedCB.currentText()
            spacer_filter = self.spacerCB.currentText()
            spacer_dict = {
                "4.0mm": "40",
                "2.6mm": "26",
                "1.8mm": "18",
                "any": "any"
            }
            spacer_filter = spacer_dict[spacer_filter]

            grade_filter = self.spacerCB_2.currentText()
            status_filter = self.spacerCB_3.currentText()
            module_speed=""
            spacer=""
            filtered_modules = []
            for module in modules:
                if module is None:
                    continue
                if "_5_" in module.get("moduleName", ""):
                    module_speed="5G"
                if "_10_" in module.get("moduleName", ""):
                    module_speed="10G"
                if "_05_" in module.get("moduleName", ""):
                    module_speed="5G"
                if "_10-" in module.get("moduleName", ""):
                    module_speed="10G"
                if "_5-" in module.get("moduleName", ""):
                    module_speed="5G"
                if "_05-" in module.get("moduleName", ""):
                    module_speed="5G"
               # print(module_speed)
                if module.get("children") is not None:                  
                    if module.get("children").get("PS Read-out Hybrid") is not None:            
                        if module.get("children").get("PS Read-out Hybrid").get("details") is not None:                  
                            if module.get("children").get("PS Read-out Hybrid").get("details").get("ALPGBT_BANDWIDTH") is not None:                  
                                module_speed=module.get("children").get("PS Read-out Hybrid").get("details").get("ALPGBT_BANDWIDTH")
                                if module_speed=="10Gbps":
                                    module_speed="10G"
                                if module_speed=="5Gbps":
                                    module_speed="5G"
                module["speed"]=module_speed   
                #print("setting speed",module_speed)
                
                if speed_filter != "any" and module_speed != speed_filter:
                    continue
                #PS_26_05-IBA_00102
                fields=module.get("moduleName", "").split("_")
                if len(fields) > 2:
                    spacer=fields[1]
                if spacer_filter != "any" and spacer != spacer_filter:
                    continue
                module["spacer"]=spacer
                # if grade_filter != "any" and module.get("grade") != grade_filter:
                #     continue
                # if status_filter != "Ready For Mounting" and module.get("status") != status_filter:
                #     continue

        # "details": {
        #     "ID": "585960",
        #     "RECORD_INSERTION_TIME": "2024-05-21 00:00:00",
        #     "LOCATION": "IT-Pisa[INFN Pisa]",
        #     "PART_PARENT_ID": "490740",
        #     "KIND_OF_PART_ID": "9020",
        #     "KIND_OF_PART": "PS Module",
        #     "MANUFACTURER": "INFN Perugia",
        #     "BARCODE": "PS_16_10_IPG-00005",
        #     "SERIAL_NUMBER": "PS_16_10_IPG-00005",
        #     "VERSION": "",
        #     "NAME_LABEL": "PS_16_10_IPG-00005",
        #     "PRODUCTION_DATE": "",
        #     "BATCH_NUMBER": "",
        #     "DESCRIPTION": "Left Hybrid not responding, sensors currents slightly high",
        #     "ARING_INDEX": "",
        #     "APS_SENSOR_SPACING": "",
        #     "AMODULE_INTEGRATION_STATUS": "",
        #     "ASTATUS": "Damaged",
        #     "APOSITION_INDEX": "2"


                filtered_modules.append(module)
            
            # Clear existing items
            self.treeWidget.clear()
            self.treeWidget.header().resizeSection(0, 200)
            # Add filtered modules
            for module in filtered_modules:
                item = QTreeWidgetItem(self.treeWidget)
                item.setText(0, module.get("moduleName", ""))
                item.setText(1, module.get("inventorySlot", ""))
                item.setText(2, module.get("speed", ""))
                item.setText(3, str(module.get("spacer", "")))
               # item.setText(4,json.dumps(module.get("details", {}), indent=4))
                item.setText(4, module.get("details", {}).get("ASTATUS", ""))
                item.setText(5, module.get("details", {}).get("DESCRIPTION", ""))
                item.setText(6, str(module.get("crateSide", {}).get("1", [])))  
                
        except Exception as e:
            self.log_output(f"Error updating module list: {str(e)}")

    def select_module(self):
        """Handle module selection from inventory"""
        selected_items = self.treeWidget.selectedItems()
        if not selected_items:
            self.log_output("No module selected")
            return
        
        selected_item = selected_items[0]
        module_id = selected_item.text(0)  # Get module name from first column
        
        # Set the module ID in the first tab
        self.moduleLE.setText(module_id)
        
        # Switch to first tab
        self.tabWidget.setCurrentIndex(0)
        
        self.log_output(f"Selected module: {module_id}")

    def update_connection_status(self):
        """Update the connection status labels showing both connection directions"""
        try:
            power_id = self.powerCB.currentText()
            fiber_id = self.fiberCB.currentText()

            # Get power connections
            power_status = set()
            if power_id:
                det_endpoint, crate_endpoints = self.get_power_endpoints(power_id)
                if det_endpoint and crate_endpoints:
                    for crate_endpoint in crate_endpoints:
                        power_status.add(f"{det_endpoint} <--> {crate_endpoint}")

            # Get fiber connections
            fiber_status = set()
            if fiber_id:
                det_endpoint, crate_endpoint = self.get_fiber_endpoints(fiber_id)
                if det_endpoint and crate_endpoint:
                    fiber_status.add(f"{det_endpoint} <--> {crate_endpoint}")
                    self.fiber_endpoint = crate_endpoint

            # Update labels
            self.powerConnectionLabel.setText("\n".join(power_status) if power_status else "Not connected")
            self.fiberConnectionLabel.setText("\n".join(fiber_status) if fiber_status else "Not connected")

            # Update LED colors
            self.update_connection_leds()

        except Exception as e:
            self.log_output(f"Error updating connection status: {str(e)}")
            self.powerConnectionLabel.setText("Error checking status")
            self.fiberConnectionLabel.setText("Error checking status")

    def check_connection_match(self, det_endpoint):
        """Check if the detected connection matches the selected module"""
        selected_module = self.moduleLE.text()
        return selected_module == "" or selected_module == det_endpoint

    def update_connection_leds(self):
        """Update LED colors based on connection status and matching"""
        try:
            power_id = self.powerCB.currentText()
            fiber_id = self.fiberCB.currentText()
            
            # Get power connection status
            if power_id:
                det_endpoint, _ = self.get_power_endpoints(power_id)
                if det_endpoint:
                    if self.check_connection_match(det_endpoint):
                        self.connectPowerLED.setStyleSheet("background-color: rgb(85, 170, 0);")  # Green
                    else:
                        self.connectPowerLED.setStyleSheet("background-color: rgb(255, 255, 0);")  # Yellow
                else:
                    self.connectPowerLED.setStyleSheet("background-color: red;")
            
            # Get fiber connection status
            if fiber_id:
                det_endpoint, _ = self.get_fiber_endpoints(fiber_id)
                if det_endpoint:
                    if self.check_connection_match(det_endpoint):
                        self.connectFiberLED.setStyleSheet("background-color: rgb(85, 170, 0);")  # Green
                    else:
                        self.connectFiberLED.setStyleSheet("background-color: rgb(255, 255, 0);")  # Yellow
                else:
                    self.connectFiberLED.setStyleSheet("background-color: red;")
                
        except Exception as e:
            self.log_output(f"Error updating LEDs: {str(e)}")

    def get_fiber_endpoints(self, fiber_id):
        """Get both detSide and crateSide endpoints for a fiber connection"""
        try:
            # Get detSide path
            det_response = requests.post(
                f"{self.apiBaseUrlLE.text()}/snapshot",
                json={"cable": fiber_id, "side": "detSide"}
            )
            if det_response.status_code != 200:
                return None, None

            det_snapshot = det_response.json()
            det_endpoint = None
            for line in det_snapshot:
                if det_snapshot[line]["connections"]:
                    # Get the last connection in the detSide path
                    det_endpoint = det_snapshot[line]["connections"][-1]["cable"]
                    break

            # Get crateSide path from the module
            if det_endpoint:
                crate_response = requests.post(
                    f"{self.apiBaseUrlLE.text()}/snapshot",
                    json={"cable": det_endpoint, "side": "crateSide"}
                )
                if crate_response.status_code == 200:
                    crate_snapshot = crate_response.json()
                    # Look at fiber lines (1,2)
                    for line in ["1", "2"]:
                        if line in crate_snapshot and crate_snapshot[line]["connections"]:
                            last_conn = crate_snapshot[line]["connections"][-1]
                            ports = last_conn['crate_port'] + last_conn['det_port']
                            port = ports[0] if ports else "?"
                            return det_endpoint, f"{last_conn['cable']}_{port}"

            return None, None
        except Exception as e:
            self.log_output(f"Error getting fiber endpoints: {str(e)}")
            return None, None

    def get_power_endpoints(self, power_id):
        """Get both detSide and crateSide endpoints for power connections"""
        try:
            # Get detSide path
            det_response = requests.post(
                f"{self.apiBaseUrlLE.text()}/snapshot",
                json={"cable": power_id, "side": "detSide"}
            )
            if det_response.status_code != 200:
                return None, []

            det_snapshot = det_response.json()
            det_endpoint = None
            for line in det_snapshot:
                if det_snapshot[line]["connections"]:
                    # Get the last connection in the detSide path
                    det_endpoint = det_snapshot[line]["connections"][-1]["cable"]
                    break

            # Get crateSide path from the module
            if det_endpoint:
                crate_response = requests.post(
                    f"{self.apiBaseUrlLE.text()}/snapshot",
                    json={"cable": det_endpoint, "side": "crateSide"}
                )
                if crate_response.status_code == 200:
                    crate_snapshot = crate_response.json()
                    crate_endpoints = []
                    # Look at power lines (3,4)
                    for line in ["3", "4"]:
                        if line in crate_snapshot and crate_snapshot[line]["connections"]:
                            last_conn = crate_snapshot[line]["connections"][-1]
                            ports = last_conn['crate_port'] + last_conn['det_port']
                            port = ports[0] if ports else "?"
                            crate_endpoints.append(f"{last_conn['cable']}_{port}")
                    return det_endpoint, crate_endpoints

            return None, []
        except Exception as e:
            self.log_output(f"Error getting power endpoints: {str(e)}")
            return None, []

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    main_app = MainApp(window)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    import sys

    main()
