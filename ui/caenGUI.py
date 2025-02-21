#!/bin/env python3
#create QT GUI with one button to send message to TCP server
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QHBoxLayout, QFrame, QLabel
from PyQt5.QtCore import pyqtSlot, QTimer, QThread, pyqtSignal
import socket
import json
BUFFER_SIZE = 100000

class CAENQueryThread(QThread):
    """Thread class for handling CAEN queries"""
    dataReady = pyqtSignal(dict)  # Signal to emit when data is received
    error = pyqtSignal(str)  # Signal to emit when error occurs

    def __init__(self, ip='192.168.0.45', port=7000):
        super().__init__()
        self.ip = ip
        self.port = port
        self.message = None
        self.receive = False
        self.running = True

    def setup_query(self, message, receive=False):
        """Setup the query to be executed"""
        self.message = message
        self.receive = receive
        
    def stop(self):
        """Stop the thread"""
        self.running = False
        self.wait()

    def run(self):
        """Thread's main method"""
        if not self.message:
            return

        try:
            tcpClass = tcp_util(ip=self.ip, port=self.port)
            tcpClass.sendMessage(self.message)
            
            if self.receive:
                data = tcpClass.socket.recv(BUFFER_SIZE)[8:].decode("utf-8")
                parsedData = {}
                for token in data.split(','):
                    if token.startswith('caen'):
                        key, value = token.split(":")
                        value = float(value)
                        parsedData[key] = value
                self.dataReady.emit(parsedData)
            
            tcpClass.closeSocket()
            
        except Exception as e:
            self.error.emit(str(e))

class tcp_util():
    """Utility class for tcp
    comunication management. """
    def __init__(self, ip, port):
        self.ip          = ip
        self.port        = port
        self.socket      = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.headerBytes = 4

        self.connectSocket()
        pass

    def __del__ (self):
        """Desctuctor, closes socket"""
        try:
            self.closeSocket()
        except:
            pass

    def connectSocket(self):
        """Connects socket"""
        self.socket.connect((self.ip,self.port))
        pass

    def closeSocket(self):
        """Closes socket connection"""
        self.socket.close()
        pass

    def sendMessage(self,message):
        """Encodes message and sends it on socket"""
        encodedMessage = self.encodeMessage(message)
        self.socket.send(encodedMessage)
        pass

    def encodeMessage(self,message):
        """Encodes message adding 4 bytes header"""
        messageLength = len(message) + self.headerBytes +4
        N=0
        encodedMessage = (messageLength).to_bytes(4, byteorder='big') + N.to_bytes(4, byteorder='big') + message.encode('utf-8')
        return encodedMessage

from argparse import Namespace

class caenGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # Create query thread
        self.queryThread = CAENQueryThread()
        self.queryThread.dataReady.connect(self.handle_query_response)
        self.queryThread.error.connect(self.handle_query_error)

    def __del__(self):
        """Cleanup when widget is destroyed"""
        self.queryThread.stop()

    def initUI(self):
        self.setWindowTitle('CAEN GUI')
#        self.setGeometry(100, 100, 300, 400)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
#        self.channels = ['HV011','CR01','CR02','CR03','CR04']+["BLV%02d"%x for x in range(1,11)] + ['INT%02d'%x for x in range(1,5)]
#       self.channels = ['CR01','CR02','CR03','CR04','BLV07','BLV08','BLV09','BLV10']
        self.channels=["BLV12","HV012"]
#        for s in [8,9,10,11]:
#            self.channels +=['LV%d_%d'%(s,x) for x in range(8)]

        self.led={}
        self.label={}
        #add buttons for On and Off, a status led and a voltage value for each channel in a new horizontal layour
        #object then add the horizontal layout to the main vertical layout
        for i,channel in enumerate(self.channels):
            if i%12 ==0 :
                vlayout=QVBoxLayout()
                self.layout.addLayout(vlayout)
            hlayout=QHBoxLayout()
            vlayout.addLayout(hlayout)
            self.button = QPushButton('Channel '+channel+' ON', self)
            self.button.clicked.connect(lambda checked,channel=channel: self.on(channel))
            hlayout.addWidget(self.button)
            self.button = QPushButton('Channel '+channel+' OFF', self)
            self.button.clicked.connect(lambda checked,channel=channel: self.off(channel))
            hlayout.addWidget(self.button)
            #use QFrame as a led
            self.led[channel] = QFrame(self)
            self.led[channel].setFrameShape(QFrame.Box)
            self.led[channel].setFixedSize(30,30)

            self.led[channel].setStyleSheet("background-color: red")

            hlayout.addWidget(self.led[channel])
            self.label[channel] = QLabel('0.0')
            hlayout.addWidget(self.label[channel])



        #create timer for periodic update of the GUI with info from caen
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(2000)
        
        self.show()

    @pyqtSlot()
    def update(self):
        """Periodic update method"""
        self.queryThread.setup_query('GetStatus,PowerSupplyId:caen', True)
        self.queryThread.start()

    def handle_query_response(self, data):
        """Handle the response from query thread"""
        try:
            for channel in self.channels:
                if data['caen_'+channel+'_IsOn'] > 0.5:
                    self.led[channel].setStyleSheet("background-color: green")
                else:
                    self.led[channel].setStyleSheet("background-color: red")
                self.label[channel].setText(
                    f'V: {data["caen_"+channel+"_Voltage"]:6.2f}V '
                    f'C: {data["caen_"+channel+"_Current"]:6.2f}A '
                    f'P: {data["caen_"+channel+"_Voltage"]*data["caen_"+channel+"_Current"]:6.2f}W'
                )
        except Exception as e:
            print(f"Error handling response: {e}")

    def handle_query_error(self, error_msg):
        """Handle errors from query thread"""
        print(f"Query error: {error_msg}")

    @pyqtSlot()
    def on(self, channel):
        self.queryThread.setup_query(f'TurnOn,PowerSupplyId:caen,ChannelId:{channel}')
        self.queryThread.start()

    @pyqtSlot()
    def off(self, channel):
        self.queryThread.setup_query(f'TurnOff,PowerSupplyId:caen,ChannelId:{channel}')
        self.queryThread.start()

def main():
    app = QApplication(sys.argv)
    ex = caenGUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


