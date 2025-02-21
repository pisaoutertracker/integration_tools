import integration_gui
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QGraphicsScene
from math import *

# Set matplotlib backend before importing pyplot
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.axes_grid1 import make_axes_locatable
import paho.mqtt.client as mqtt
import struct
import numpy as np
from caenGUI import CAENControl

#MQTT_SERVER = "192.168.0.45"
MQTT_SERVER = "test.mosquitto.org"
MQTT_PATH = "/ar/thermal/image"

class MainApp(integration_gui.Ui_MainWindow):
    def __init__(self, window):
        self.setupUi(window)    
        self.ringLE.returnPressed.connect(self.split_ring_and_position)
        self.positionLE.returnPressed.connect(self.draw_ring)
        fibers=["F1","F2"]
        powers=["P1","P2"]
        self.fiberCB.addItems(fibers)
        self.powerCB.addItems(powers)
        self.draw_ring()
        
        # Setup thermal camera plotting
        self.setup_thermal_plot()
        
        # Setup CAEN control
        self.caen = CAENControl(self)
        
        # Setup MQTT client
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

    def setup_mqtt(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_mqtt_connect
        self.client.on_message = self.on_mqtt_message
        self.client.connect(MQTT_SERVER, 1883, 60)
        self.client.loop_start()

    def on_mqtt_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe(MQTT_PATH)

    def on_mqtt_message(self, client, userdata, msg):
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


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    main_app = MainApp(window)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    import sys
    main()
