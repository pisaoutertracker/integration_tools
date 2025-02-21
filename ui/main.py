import integration_gui
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QLabel, QFormLayout
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
        ring, position = ring_position.split(';')
        self.ringLE.setText(ring)
        self.positionLE.setText(position)
    
    def draw_ring(self):
        number_of_modules=18
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
        deltaphi=360/number_of_modules*2
        #solid
        pen.setStyle(Qt.SolidLine)
        #draw two circles in the middle-top
        scene.addEllipse(radius-7, -20, 6, 6, pen)
        scene.addEllipse(radius+7, -20, 6, 6, pen)
        scene.addEllipse(radius-4, -17, 1, 1, pen)
        scene.addEllipse(radius+10, -17, 1, 1, pen)

        for i in range(1,number_of_modules+1):
            phi=-(i)*deltaphi+deltaphi/2
            phi-=90
            if i> number_of_modules/2:
                phi+=deltaphi/2
            if self.positionLE.text()==str(i):
                pen.setColor(Qt.red)
            else:
                pen.setColor(Qt.black)
            if i<= number_of_modules/2:
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
            'power': self.powerCB.currentText()
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
        """Run a shell command and return result"""
        try:
            expanded_command = self.expand_placeholders(command)
            self.log_output(f"Running command: {expanded_command}")
            self.log_output(f"Using placeholders: {self.get_placeholder_values()}")
            
            result = subprocess.run(expanded_command, shell=True, check=True, 
                                  capture_output=True, text=True)
            self.log_output(f"Output:\n{result.stdout}")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            self.log_output(f"Error:\n{e.stderr}")
            return False, e.stderr

    def make_api_request(self, endpoint, method, data=None):
        """Make API request and return result"""
        url = self.expand_placeholders(self.apiBaseUrlLE.text())
        endpoint = self.expand_placeholders(endpoint)
        
        try:
            self.log_output(f"Making {method} request to: {url}/{endpoint}")
            
            if data:
                # Expand placeholders in all data values
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
                
            response.raise_for_status()
            result = response.json()
            self.log_output(f"Response: {result}")
            return True, result
        except requests.RequestException as e:
            self.log_output(f"API Error: {str(e)}")
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

    def connect_power(self):
        self.log_output("=== Connecting Power ===")
        success, result = self.make_api_request(
            endpoint=self.connectPowerEndpointLE.text(),
            method=self.connectPowerMethodCB.currentText(),
            data={"power": self.powerCB.currentText()}
        )
        self.connectPowerLED.setStyleSheet(
            "background-color: rgb(85, 170, 0);" if success else "background-color: red;")

    def connect_fiber(self):
        self.log_output("=== Connecting Fiber ===")
        success, result = self.make_api_request(
            endpoint=self.connectFiberEndpointLE.text(),
            method=self.connectFiberMethodCB.currentText(),
            data={"fiber": self.fiberCB.currentText()}
        )
        self.connectFiberLED.setStyleSheet(
            "background-color: rgb(85, 170, 0);" if success else "background-color: red;")

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

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    main_app = MainApp(window)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    import sys
    main()
