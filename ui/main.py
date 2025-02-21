import integration_gui
#inherit from integration_gui Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsScene
from math import *
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


import sys
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    window = QMainWindow()
    main_app = MainApp(window)
    window.show()
    sys.exit(app.exec_())
