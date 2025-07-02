import sys
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeWidgetItem, 
                             QMessageBox, QListWidgetItem, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, QDateTime, QThread, pyqtSignal
from PyQt5.uic import loadUi
from influxdb_client import InfluxDBClient
import matplotlib.pyplot as plt
import warnings

# Suppress deprecation warnings for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning)


class DataFetcher(QThread):
    """Background thread for fetching data from InfluxDB"""
    data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.query_type = None
        self.params = {}
    
    def fetch_hierarchy(self):
        self.query_type = "hierarchy"
        self.start()
    
    def fetch_plot_data(self, start_time, end_time, sensors):
        self.query_type = "plot"
        self.params = {
            'start_time': start_time,
            'end_time': end_time,
            'sensors': sensors
        }
        self.start()
    
    def run(self):
        try:
            if self.query_type == "hierarchy":
                data = self._get_sensor_hierarchy()
                self.data_ready.emit(data)
            elif self.query_type == "plot":
                data = self._get_plot_data()
                self.data_ready.emit(data)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def _get_influx_client(self):
        token_location = os.path.join(os.path.dirname(__file__), "influx.sct")
        token = open(os.path.expanduser(token_location)).read().strip()
        client = InfluxDBClient(url="http://pccmslab1:8086/", token=token)
        return client.query_api()
    
    def _get_sensor_hierarchy(self):
        query_api = self._get_influx_client()
        
        # Query to get all unique topics
        topics_query = """
        from(bucket: "sensor_data")
          |> range(start: -1h)
          |> filter(fn: (r) => r._measurement == "mqtt_consumer")
          |> keep(columns: ["topic"])
          |> distinct(column: "topic")
          |> sort()
        """
        
        # Get all topics
        topics = []
        topics_result = query_api.query(topics_query, org="pisaoutertracker")
        for table in topics_result:
            for record in table.records:
                topics.append(record.get_value())
        
        # For each topic, get its fields
        topic_sensors = {}
        for topic in sorted(topics):
            fields_query = f"""
            from(bucket: "sensor_data")
              |> range(start: -1h)
              |> filter(fn: (r) => r._measurement == "mqtt_consumer")
              |> filter(fn: (r) => r.topic == "{topic}")
              |> keep(columns: ["_field"])
              |> distinct(column: "_field")
              |> sort()
            """
            
            fields_result = query_api.query(fields_query, org="pisaoutertracker")
            fields = []
            for table in fields_result:
                for record in table.records:
                    fields.append(record.get_value())
            
            if fields:
                topic_sensors[topic] = sorted(fields)
        
        return topic_sensors
    
    def _get_plot_data(self):
        query_api = self._get_influx_client()
        start_time = self.params['start_time']
        end_time = self.params['end_time']
        sensors = self.params['sensors']
        
        plot_data = {}
        for sensor in sensors:
            query = f"""
            from(bucket: "sensor_data")
                |> range(start: {start_time}, stop: {end_time})
                |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
                |> filter(fn: (r) => r["_field"] == "{sensor}")
                |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
                |> yield(name: "mean")
            """
            
            tables = query_api.query(query, org="pisaoutertracker")
            timestamps = []
            values = []
            for table in tables:
                for record in table.records:
                    timestamps.append(record.get_time())
                    values.append(record.get_value())
            
            plot_data[sensor] = {'timestamps': timestamps, 'values': values}
        
        return plot_data


class SensorMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load the UI file
        ui_path = os.path.join(os.path.dirname(__file__), "sensor_monitor.ui")
        try:
            loadUi(ui_path, self)
        except Exception as e:
            QMessageBox.critical(None, "UI Error", f"Failed to load UI file:\n{str(e)}")
            sys.exit(1)
        
        # Initialize components
        self.topic_sensors = {}
        self.data_fetcher = DataFetcher()
        
        # Connect signals
        self.setup_connections()
        
        # Initialize time controls
        self.setup_time_controls()
        
        # Load initial data
        self.refresh_sensor_list()
    
    def setup_connections(self):
        """Setup signal connections"""
        # UI signals
        self.refreshButton.clicked.connect(self.refresh_sensor_list)
        self.topicCombo.currentTextChanged.connect(self.on_topic_changed)
        self.plotButton.clicked.connect(self.plot_data)
        self.lastHourButton.clicked.connect(self.set_last_hour)
        self.last24HoursButton.clicked.connect(self.set_last_24_hours)
        
        # Menu actions
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.show_about)
        
        # Data fetcher signals
        self.data_fetcher.data_ready.connect(self.on_data_ready)
        self.data_fetcher.error_occurred.connect(self.on_error)
    
    def setup_time_controls(self):
        """Initialize time controls with default values"""
        now = QDateTime.currentDateTime()
        hour_ago = now.addSecs(-3600)
        
        self.startTime.setDateTime(hour_ago)
        self.endTime.setDateTime(now)
    
    def refresh_sensor_list(self):
        """Refresh the sensor hierarchy from InfluxDB"""
        self.statusLabel.setText("Status: Loading sensors...")
        self.refreshButton.setEnabled(False)
        self.data_fetcher.fetch_hierarchy()
    
    def on_data_ready(self, data):
        """Handle data received from background thread"""
        if self.data_fetcher.query_type == "hierarchy":
            self.topic_sensors = data
            self.populate_sensor_tree()
            self.populate_topic_combo()
            self.statusLabel.setText(f"Status: Loaded {len(data)} topics")
            self.refreshButton.setEnabled(True)
        elif self.data_fetcher.query_type == "plot":
            self.create_plot(data)
    
    def on_error(self, error_message):
        """Handle errors from background thread"""
        QMessageBox.critical(self, "Error", f"Failed to fetch data:\n{error_message}")
        self.statusLabel.setText("Status: Error occurred")
        self.refreshButton.setEnabled(True)
    
    def populate_sensor_tree(self):
        """Populate the sensor hierarchy tree"""
        self.sensorTree.clear()
        
        root = QTreeWidgetItem(self.sensorTree, ["sensor_data (bucket)"])
        mqtt_item = QTreeWidgetItem(root, ["mqtt_consumer (measurement)"])
        
        for topic, sensors in self.topic_sensors.items():
            topic_item = QTreeWidgetItem(mqtt_item, [topic])
            for sensor in sensors:
                QTreeWidgetItem(topic_item, [sensor])
        
        self.sensorTree.expandAll()
    
    def populate_topic_combo(self):
        """Populate the topic combo box"""
        self.topicCombo.clear()
        self.topicCombo.addItems(sorted(self.topic_sensors.keys()))
    
    def on_topic_changed(self, topic):
        """Handle topic selection change"""
        self.sensorList.clear()
        if topic in self.topic_sensors:
            for sensor in self.topic_sensors[topic]:
                item = QListWidgetItem(sensor)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.sensorList.addItem(item)
    
    def get_selected_sensors(self):
        """Get list of selected sensors"""
        selected = []
        for i in range(self.sensorList.count()):
            item = self.sensorList.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        return selected
    
    def set_last_hour(self):
        """Set time range to last hour"""
        now = QDateTime.currentDateTime()
        hour_ago = now.addSecs(-3600)
        self.startTime.setDateTime(hour_ago)
        self.endTime.setDateTime(now)
    
    def set_last_24_hours(self):
        """Set time range to last 24 hours"""
        now = QDateTime.currentDateTime()
        day_ago = now.addSecs(-86400)
        self.startTime.setDateTime(day_ago)
        self.endTime.setDateTime(now)
    
    def plot_data(self):
        """Plot selected sensor data"""
        selected_sensors = self.get_selected_sensors()
        if not selected_sensors:
            QMessageBox.warning(self, "Warning", "Please select at least one sensor to plot.")
            return
        
        # Convert QDateTime to ISO format
        start_time = self.startTime.dateTime().toString("yyyy-MM-ddThh:mm:ssZ")
        end_time = self.endTime.dateTime().toString("yyyy-MM-ddThh:mm:ssZ")
        
        self.statusLabel.setText("Status: Fetching plot data...")
        self.plotButton.setEnabled(False)
        self.data_fetcher.fetch_plot_data(start_time, end_time, selected_sensors)
    
    def create_plot(self, plot_data):
        """Create matplotlib plot with the data"""
        if not plot_data:
            QMessageBox.warning(self, "Warning", "No data available for the selected time range.")
            self.plotButton.setEnabled(True)
            self.statusLabel.setText("Status: Ready")
            return
        
        # Filter out sensors with no data
        valid_sensors = {k: v for k, v in plot_data.items() if v['timestamps']}
        
        if not valid_sensors:
            QMessageBox.warning(self, "Warning", "No data found for selected sensors in the specified time range.")
            self.plotButton.setEnabled(True)
            self.statusLabel.setText("Status: Ready")
            return
        
        # Create matplotlib figure
        num_sensors = len(valid_sensors)
        fig, axes = plt.subplots(num_sensors, 1, figsize=(12, 6*num_sensors), sharex=True)
        
        if num_sensors == 1:
            axes = [axes]
        
        for i, (sensor_name, data) in enumerate(valid_sensors.items()):
            axes[i].plot(data['timestamps'], data['values'], marker='o', linestyle='-', label=sensor_name)
            axes[i].set_title(f'Sensor: {sensor_name}')
            axes[i].set_ylabel('Value')
            axes[i].grid(True)
            axes[i].legend()
        
        axes[-1].set_xlabel('Time')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
        self.plotButton.setEnabled(True)
        self.statusLabel.setText("Status: Plot created")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", 
                         "Sensor Data Monitor\n\n"
                         "A Qt application for monitoring InfluxDB sensor data.\n"
                         "Built with PyQt5 and matplotlib.")


def main():
    app = QApplication(sys.argv)
    
    # Check if UI file exists
    ui_path = os.path.join(os.path.dirname(__file__), "sensor_monitor.ui")
    if not os.path.exists(ui_path):
        QMessageBox.critical(None, "Error", f"UI file not found: {ui_path}")
        sys.exit(1)
    
    # Check if InfluxDB token file exists
    token_path = os.path.join(os.path.dirname(__file__), "influx.sct")
    if not os.path.exists(token_path):
        QMessageBox.critical(None, "Error", f"InfluxDB token file not found: {token_path}")
        sys.exit(1)
    
    window = SensorMonitor()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()