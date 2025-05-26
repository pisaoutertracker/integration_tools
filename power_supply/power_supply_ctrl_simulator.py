import sys
import random
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('power_supply_simulator.log')
    ]
)
logger = logging.getLogger(__name__)

class PowerSupplySimulator(QMainWindow):
    def __init__(self):
        super(PowerSupplySimulator, self).__init__()
        loadUi('power_supply.ui', self)
        
        self.simulator_status = {
            'voltage': '0.00',
            'current': '0.00',
            'power': 'OFF',
            'set_voltage': 0.0,
            'set_current': 0.0
        }
        
        self.setup_ui_connections()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_measurements)
        self.timer.start(5000)
        
        self.update_ui()
        self.log_status("Initial simulator status")
        self.setWindowTitle("Power Supply Simulator")
    
    def log_status(self, message):
        """Log the current status with a descriptive message"""
        logger.info(f"{message}: {self.simulator_status}")
    
    def setup_ui_connections(self):
        self.powsup_voltage_set_PB.clicked.connect(self.set_voltage)
        self.powsup_current_set_PB.clicked.connect(self.set_current)
        self.power_ON_PB.clicked.connect(self.power_on)
        self.power_OFF_PB.clicked.connect(self.power_off)
    
    def update_ui(self):
        self.powsup_current_value_label.setText(str(self.simulator_status['current']))
        self.powsup_voltage_value_label.setText(str(self.simulator_status['voltage']))
        self.power_LED.setStyleSheet("background-color: green;" if self.simulator_status['power'] == 'ON' else "background-color: red;")
    
    def update_measurements(self):
        if self.simulator_status['power'] == 'ON':
            voltage = max(0, self.simulator_status['set_voltage'] * (1 + random.uniform(-0.01, 0.01)))
            current = max(0, self.simulator_status['set_current'] * (1 + random.uniform(-0.01, 0.01)))
            
            self.simulator_status['voltage'] = f"{voltage:.2f}"
            self.simulator_status['current'] = f"{current:.2f}"
            
            self.update_ui()
            self.log_status("Simulator measurement update")
    
    def set_voltage(self):
        try:
            voltage = float(self.powsup_voltage_LE.text())
            if voltage < 0:
                raise ValueError("Voltage cannot be negative")
            self.simulator_status['set_voltage'] = voltage
            if self.simulator_status['power'] == 'ON':
                self.simulator_status['voltage'] = f"{voltage:.2f}"
            logger.info(f"Voltage set to {voltage}V (simulated)")
            self.log_status("After voltage set")
            self.update_ui()
        except ValueError as e:
            logger.error(f"Voltage set error: {e}")
            QMessageBox.warning(self, "Input Error", str(e))
    
    def set_current(self):
        try:
            current = float(self.powsup_current_LE.text())
            if current < 0:
                raise ValueError("Current cannot be negative")
            self.simulator_status['set_current'] = current
            if self.simulator_status['power'] == 'ON':
                self.simulator_status['current'] = f"{current:.2f}"
            logger.info(f"Current set to {current}A (simulated)")
            self.log_status("After current set")
            self.update_ui()
        except ValueError as e:
            logger.error(f"Current set error: {e}")
            QMessageBox.warning(self, "Input Error", str(e))
    
    def power_on(self):
        self.simulator_status['power'] = 'ON'
        self.simulator_status['voltage'] = f"{self.simulator_status['set_voltage']:.2f}"
        self.simulator_status['current'] = f"{self.simulator_status['set_current']:.2f}"
        logger.info("Power turned ON (simulated)")
        self.log_status("After power ON")
        self.update_ui()
    
    def power_off(self):
        self.simulator_status['power'] = 'OFF'
        self.simulator_status['voltage'] = "0.00"
        self.simulator_status['current'] = "0.00"
        logger.info("Power turned OFF (simulated)")
        self.log_status("After power OFF")
        self.update_ui()
    
    def closeEvent(self, event):
        self.timer.stop()
        logger.info("Simulator closed cleanly")
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PowerSupplySimulator()
    window.show()
    sys.exit(app.exec_())
